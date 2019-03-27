#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.1
# name: guitools
# license: MIT

import sys, os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import modules.shell_helpers.shell_helpers as shell

del sys.path[0:2]

import re
from pprint import pprint

class Keyboard(object):
    def __init__(self, win_dec_id=""):
        self.win_dec_id=win_dec_id

    def key(self, keys, win_dec_id=""):
        if win_dec_id:
            os.system("xdotool key --window {} {}".format(win_dec_id, keys ))
        elif self.win_dec_id:
            os.system("xdotool key --window {} {}".format(self.win_dec_id, keys ))
        else:
            os.system("xdotool key {}".format(keys))

    def type(self, text, win_dec_id=""):
        if win_dec_id:
            os.system("xdotool type --window {} {}".format(win_dec_id, text ))
        elif self.win_dec_id:
            os.system("xdotool type --window {} {}".format(self.win_dec_id, text ))
        else:
            os.system("xdotool type {}".format(text))
