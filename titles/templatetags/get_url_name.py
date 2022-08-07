from django import template
import re
register = template.Library()


@register.filter(name='get_url_name')
def get_url_name(url):
    mapper = {'shikimori.one': 'Shikimori',
              'myanimelist.net': 'MyAnimeList',
              'mangaupdates.com': 'MangaUpdates',
              'anilist.co': 'AniList',
              'world-art.ru': 'WorldArt',
              'mangadex.org': 'MangaDex',
              'mangalib.me': 'MangaLib'}
    regex = re.compile(
        r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)")
    # regex.search(url)
    return mapper[regex.search(url).group(1)]
