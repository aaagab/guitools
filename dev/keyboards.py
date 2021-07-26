#!/usr/bin/env python3
from pprint import pprint
import os
import re
import sys
import time

class Keyboard(object):
    def __init__(self, win_dec_id=""):
        self.win_dec_id=win_dec_id

    def key(self, keys, win_dec_id=""):
        if win_dec_id:
            os.system("xdotool key --clearmodifiers --window {} {}".format(win_dec_id, keys ))
        elif self.win_dec_id:
            os.system("xdotool key --clearmodifiers --window {} {}".format(self.win_dec_id, keys ))
        else:
            os.system("xdotool key {}".format(keys))

    def type(self, text, win_dec_id=""):
        if win_dec_id:
            os.system("xdotool type --clearmodifiers --window {} {}".format(win_dec_id, text ))
        elif self.win_dec_id:
            os.system("xdotool type --clearmodifiers --window {} {}".format(self.win_dec_id, text ))
        else:
            os.system("xdotool type {}".format(text))
