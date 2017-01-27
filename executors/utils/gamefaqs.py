import requests
import collections
import urllib

from bs4 import BeautifulSoup

_user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'

Stats = collections.namedtuple('Stats', 'own rate diff time play')


def get_class_starts_with(tag, s):
    for class_ in tag.attrs['class']:
        if class_.startswith(s):
            return class_


def find_game_url(game):
    if not game:
        return

    url = 'http://www.gamefaqs.com/search?game=' + \
           urllib.parse.quote_plus(game)
    resp = requests.get(url, headers={'User-Agent': _user_agent,
                                      'Referer': 'http://www.gamefaqs.com/'})
    gamefaqs = BeautifulSoup(resp.text)

    tr_list = gamefaqs.find(class_='results').find_all('tr')
    
    games = {}
    for tr in tr_list:
        platform = tr.find(class_='rmain').text.strip()
        url = tr.find(class_='rtitle').find('a').attrs['href']
        games[platform.lower()] = 'http://www.gamefaqs.com' + url

    try:
        return games['pc']
    except KeyError:
        return ''


def get_stats(game_url):
    if not game_url:
        return

    resp = requests.get(game_url, headers={'User-Agent': _user_agent})
    root = BeautifulSoup(resp.text)

    rating_list = root.find_all(class_='rating')

    stats = {get_class_starts_with(tag, 'mygames_stats_')[14:]: tag.text
             for tag in rating_list}

    if stats:
        return Stats(**stats)
