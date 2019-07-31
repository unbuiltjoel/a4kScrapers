# -*- coding: utf-8 -*-

import os
import warnings
import time
from .third_party.source_utils import tools
from .urls import trackers, hosters, get_urls

_scraper_sources_dict = {}
total_results = {}

def _assert_result(test, scraper_module, scraper_sources, scraper, torrent_list):
    results_count = len(torrent_list)

    if os.getenv('A4KSCRAPERS_TEST_TOTAL') == '1':
        for torrent in torrent_list:
            total_results[torrent['release_title']] = 1
        return

    if scraper not in trackers or scraper in ['torrentz2']:
        tools.log('tracker %s is disabled' % scraper, 'notice')
        return

    expected_count = 1
    if os.getenv('A4KSCRAPERS_TEST_ALL') == '1' and scraper not in ['showrss']:
        expected_count = len(get_urls(scraper))

    if scraper_sources._request is not None and scraper_sources._request.has_exc:
        expected_count = 0

    test.assertEqual(results_count, expected_count, '%s failed to find torrent' % scraper)

    if scraper == 'showrss':
        return

    for torrent in torrent_list:
        test.assertIsNotNone(torrent['size'], '%s missing size info' % scraper)
        test.assertIsNotNone(torrent['seeds'], '%s missing seeds info' % scraper)

def _assert_hosters_result(test, scraper_module, scraper_sources, scraper, hoster_results):
    if scraper not in hosters:
        tools.log('hoster %s is disabled' % scraper, 'notice')
        return

    if scraper_sources._request is not None and scraper_sources._request.has_exc:
        return

    test.assertGreater(len(hoster_results), 0, '%s failed to find link' % scraper)

def _get_movie_query(scraper):
    movie_imdb = None
    if scraper == 'movcr':
        movie_title = 'Gully Boy'
        movie_year = '2019'
    elif scraper == 'nyaa':
        movie_title = 'Ghost in the Shell'
        movie_year = '1995'
    elif scraper == 'rlsbb':
        movie_title = 'Avengers Endgame'
        movie_year = '2019'
    elif scraper == 'scenerls':
        movie_title = 'Alita Battle Angel'
        movie_year = '2019'
    else:
        movie_title = 'Fantastic Beasts and Where to Find Them'
        movie_year = '2016'
        movie_imdb = 'tt3183660'

    return (movie_title, movie_year, movie_imdb)

def _get_episode_query():
    simple_info = {}
    simple_info['show_title'] = 'Game of Thrones'
    simple_info['episode_title'] = 'The Dragon and the Wolf'
    simple_info['year'] = '2011'
    simple_info['season_number'] = '7'
    simple_info['episode_number'] = '7'
    simple_info['show_aliases'] = ''
    simple_info['country'] = 'US'
    simple_info['no_seasons'] = '7'

    all_info = {}
    all_info['showInfo'] = {}
    all_info['showInfo']['ids'] = {}
    all_info['showInfo']['ids']['imdb'] = 'tt0944947'

    return (simple_info, all_info)

def _get_supported_hosts():
    return ["nitroflare.com", "uploaded.to", "depositfiles.com", "filefactory.com", "mediafire.com", "turbobit.net", "1fichier.com", "streamcloud.eu", "filer.net", "datafile.com", "datei.to", "openload.co", "cloudtime.to", "zippyshare.com", "brazzers.com", "flashx.tv", "rapidvideo.com", "vidto.me", "wicked.com", "kink.com", "hitfile.net", "filenext.com", "mofos.com", "realitykings.com", "uploadboy.com", "bangbros.com", "teamskeet.com", "badoinkvr.com", "julesjordan.com", "userscloud.com", "filespace.com", "nubilefilms.com", "mexashare.com", "clicknupload.org", "bitporno.com", "vidlox.me", "streamango.com", "ulozto.net", "hulkshare.com", "vidoza.net", "hqcollect.me", "pornhubpremium.com", "spicyfile.com", "xubster.com", "worldbytez.com", "rapidrar.com", "ddfnetwork.com", "ironfiles.net"]

def _get_scraper_sources(scraper_module, scraper, url):
    if _scraper_sources_dict.get(scraper, None) is None:
        _scraper_sources_dict[scraper] = scraper_module.sources(url=url)
    return _scraper_sources_dict[scraper]

def _get_scraper_source(scraper_module, scraper, url):
    if _scraper_sources_dict.get(scraper, None) is None:
        _scraper_sources_dict[scraper] = scraper_module.source(url=url)
    return _scraper_sources_dict[scraper]

def _clock_scraping(scrape_fn, scraper):
    start = time.time()
    results = scrape_fn()
    end = time.time()
    time_ms = int(round((end - start) * 1000))
    tools.log('%s took: %s ms' % (scraper, time_ms), 'notice')
    return (results, time_ms)

def _movie(scraper_module, scraper, url, test=None):
    (movie_title, movie_year, movie_imdb) = _get_movie_query(scraper)
    scraper_sources = _get_scraper_sources(scraper_module, scraper, url)

    def scrape():
        return scraper_sources.movie(movie_title, movie_year, movie_imdb)

    (results, time_ms) = _clock_scraping(scrape, scraper)
    if test:
        _assert_result(test, scraper_module, scraper_sources, scraper, results)
    return (results, time_ms)

def _movie_from_hoster(scraper_module, scraper, url, test=None):
    (movie_title, movie_year, movie_imdb) = _get_movie_query(scraper)
    scraper_sources = _get_scraper_source(scraper_module, scraper, url)
    simple_info = scraper_sources.movie(None, movie_title, None, None, movie_year)

    def scrape():
        return scraper_sources.sources(simple_info, _get_supported_hosts(), [])
    
    (results, time_ms) = _clock_scraping(scrape, scraper)
    if test:
        _assert_hosters_result(test, scraper_module, scraper_sources, scraper, results)

    return (results, time_ms)

def _episode(scraper_module, scraper, url, test=None):
    (simple_info, all_info) = _get_episode_query()
    scraper_sources = _get_scraper_sources(scraper_module, scraper, url)

    def scrape():
        return scraper_sources.episode(simple_info, all_info)

    (results, time_ms) = _clock_scraping(scrape, scraper)
    if test:
        _assert_result(test, scraper_module, scraper_sources, scraper, results)

    return (results, time_ms)

def _episode_from_hoster(scraper_module, scraper, url, test=None):
    (simple_info, all_info) = _get_episode_query()
    scraper_sources = _get_scraper_source(scraper_module, scraper, url)
    temp_simple_info = scraper_sources.tvshow(None, None, simple_info['show_title'], None, None, simple_info['year'])
    temp_simple_info = scraper_sources.episode(temp_simple_info, None, None, simple_info['episode_title'], None, simple_info['season_number'], simple_info['episode_number'])

    def scrape():
        return scraper_sources.sources(temp_simple_info, _get_supported_hosts(), [])
    
    (results, time_ms) = _clock_scraping(scrape, scraper)
    if test:
        _assert_hosters_result(test, scraper_module, scraper_sources, scraper, results)

    return (results, time_ms)

def test_torrent(self, scraper_module, scraper, url=None):
    warnings.filterwarnings(action='ignore', category=ResourceWarning)

    if scraper in ['showrss', 'eztv']:
        return _episode(scraper_module, scraper, url, test=self)
    return _movie(scraper_module, scraper, url, test=self)

def test_hoster(self, scraper_module, scraper, url=None):
    warnings.filterwarnings(action='ignore', category=ResourceWarning)
    if os.getenv('TRAVIS') == 'true' and scraper in ['rlsbb','scenerls']:
        tools.log('skipping %s in Travis build' % scraper, 'notice')
        return

    if scraper in ['directdl']:
        return _episode_from_hoster(scraper_module, scraper, url, test=self)
    return _movie_from_hoster(scraper_module, scraper, url, test=self)
