import unittest

from ..templatetags.get_url_name import get_url_name

from ..templatetags.exist import exist


class ExistTest(unittest.TestCase):
    def test_success(self):
        lst = [[1, 2, 3, 4, "fwefwf", 11, "fsdfd"]]
        self.assertTrue(exist(lst))

    def test_fail(self):
        lst = [[1, 2, None, 4, "fwefwf", 11, "fsdfd"]]
        self.assertFalse(exist(lst))
        self.assertFalse(exist([]))


class GetUrlTest(unittest.TestCase):
    def test_fail(self):
        url = "https://myan112112imelist.net/anime/12883/Tsuritama"
        self.assertEqual(get_url_name(url), None)
        self.assertEqual(get_url_name(None), None)
        self.assertEqual(get_url_name("something"), None)
        self.assertEqual(get_url_name(123123), None)

    def test_myanimelist(self):
        url = "https://myanimelist.net/anime/12883/Tsuritama"
        self.assertEqual(get_url_name(url), "MyAnimeList")

    def test_shiki(self):
        url = "https://shikimori.one/animes/48895-overlord-iv"
        self.assertEqual(get_url_name(url), "Shikimori")

    def test_mangaupdate(self):
        url = "https://www.mangaupdates.com/series/j9xujg8/sekai-saikyou-no-shitsuji-black-shokuba-wo-tsuihousareta-ore-koori-no-reijou-ni-hirowareru"
        self.assertEqual(get_url_name(url), "MangaUpdates")

    def test_anilist(self):
        url = "https://anilist.co/anime/141391/Yofukashi-no-Uta/"
        self.assertEqual(get_url_name(url), "AniList")

    def test_worldart(self):
        url = "http://www.world-art.ru/animation/animation.php?id=11434v"
        self.assertEqual(get_url_name(url), "WorldArt")

    def test_mangadex(self):
        url = "https://mangadex.org/title/3f28c47a-bf8d-4e79-83ca-2e64fe906372/jashin-chan-dropkick"
        self.assertEqual(get_url_name(url), "MangaDex")

    def test_mangalib(self):
        url = "https://mangalib.me/won-peeo-leidi?section=info"
        self.assertEqual(get_url_name(url), "MangaLib")
