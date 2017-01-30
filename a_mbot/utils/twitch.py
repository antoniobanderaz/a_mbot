import requests
import datetime

from a_mbot import config

_twitch_api = 'https://api.twitch.tv/kraken/'

_headers = {'Accept': 'application/vnd.twitchtv.v3+json',
            'Client-ID': config.client_id}


def _method(method_name, *params):
    return _twitch_api + '/'.join((method_name,) + params)


def _get_object(url):
    resp = requests.get(url, headers=_headers)

    try:
        return resp.json()
    except ValueError:
        return None


def _get_stream_url(channel_name):
    return _method('streams', channel_name)


def _get_chatters_url(channel_name):
    return f'http://tmi.twitch.tv/group/user/{channel_name}/chatters'


def get_stream_object(channel_name):
    obj = _get_object(_get_stream_url(channel_name))
    try:
        return obj['stream']
    except KeyError:
        return None


def get_chatters_object(channel_name):
    return _get_object(_get_chatters_url(channel_name))


def is_online(channel_name):
    return get_stream_object(channel_name) is not None


def stream_start_time(channel_name):
    stream_object = get_stream_object(channel_name)
    if stream_object:
        start_time_str = stream_object['created_at']
        return datetime.datetime.strptime(start_time_str,
                                          '%Y-%m-%dT%H:%M:%SZ')


def uptime(channel_name):
    start_time = stream_start_time(channel_name)
    if start_time:
        return datetime.datetime.utcnow() - start_time


def curr_game(channel_name):
    stream_object = get_stream_object(channel_name)
    if stream_object:
        return stream_object['game']


def get_chatters(channel_name):
    stream_object = get_chatters_object(channel_name)
    if stream_object:
        return stream_object['chatters']


def get_chatters_count(channel_name):
    stream_object = get_chatters_object(channel_name)
    if stream_object:
        return stream_object['chatter_count']


def _chat_command(command, *args):
    return '.{} {}'.format(command, ' '.join([str(i) for i in args]))


def timeout(username, time):
    return _chat_command('timeout', username, time)


def ban(username):
    return _chat_command('ban', username)


def me(message):
    return _chat_command('me', message)


def unban(username):
    return _chat_command('unban', username)
