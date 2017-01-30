from subprocess import Popen, PIPE
import io

from gtts import gTTS
from requests.exceptions import HTTPError

from a_mbot import config

cmd = config.ffplay_path + ' -nodisp -autoexit -'


def say(text, *, lang='en'):
    tts = io.BytesIO()
    try:
        gTTS(text=text, lang=lang).write_to_fp(tts)
    except HTTPError:
        if lang == 'ru':
            gTTS(text='не буду я такое читать', lang=lang).write_to_fp(tts)
        else:
            gTTS(text='I won\'t read it', lang='en').write_to_fp(tts)

    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    p.communicate(input=tts.getvalue())
