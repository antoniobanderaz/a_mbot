from subprocess import Popen, PIPE
import io

from gtts import gTTS

import config

cmd = config.ffplay_path + ' -nodisp -autoexit -'

def say(text):
    tts = io.BytesIO()
    gTTS(text=text, lang='ru').write_to_fp(tts)
    
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    p.communicate(input=tts.getvalue())
