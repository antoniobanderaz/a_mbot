from subprocess import Popen, PIPE
import io

from gtts import gTTS

import config

cmd = config.ffplay_path + ' -nodisp -autoexit -'

def say(text, *, lang='en'):
    tts = io.BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(tts)
    
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    p.communicate(input=tts.getvalue())
