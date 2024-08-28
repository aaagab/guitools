#!/usr/bin/env python3
from pprint import pprint
import os
import re
import sys

class Keyboard(object):
    def __init__(self, win_dec_id:int|None=None):
        self.win_dec_id=win_dec_id

    def key(self, keys:str, win_dec_id:int|None=None):
        if win_dec_id is not None:
            os.system("xdotool key --clearmodifiers --window {} {}".format(win_dec_id, keys ))
        elif self.win_dec_id is not None:
            os.system("xdotool key --clearmodifiers --window {} {}".format(self.win_dec_id, keys ))
        else:
            os.system("xdotool key {}".format(keys))

    def type(self, text:str, win_dec_id:int|None=None):
        if win_dec_id is not None:
            os.system("xdotool type --clearmodifiers --window {} {}".format(win_dec_id, text ))
        elif self.win_dec_id is not None:
            os.system("xdotool type --clearmodifiers --window {} {}".format(self.win_dec_id, text ))
        else:
            os.system("xdotool type {}".format(text))
