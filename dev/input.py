#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.1.0
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

def get_key_pressed():
    print("code in progress")
