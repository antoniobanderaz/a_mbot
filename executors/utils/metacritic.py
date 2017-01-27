import requests
import collections

from bs4 import BeautifulSoup

_user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'

Stats = collections.namedtuple('Stats', 'metacritic user_score')


def find_game_url(game):
    if not game:
        return

    url = 'http://www.metacritic.com/game/pc/' + \
          game.lower().replace(' ', '-')
    return url


def get_stats(game_url):
    if not game_url:
        return

    resp = requests.get(game_url, headers={'User-Agent': _user_agent})
    root = BeautifulSoup(resp.text)

    try:
        metacritic = root.find(class_='main_details').find('span').text.strip()
        user_score = root.find(class_='side_details').find(class_='user').text
    except AttributeError:
        return

    return Stats(metacritic=metacritic, user_score=user_score + '/10')
