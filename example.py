#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-rc-1544109439
# name: diplay
# license: MIT
from pprint import pprint

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from display import get_display
del sys.path[0:2]

pprint(get_display())
