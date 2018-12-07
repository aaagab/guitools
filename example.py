#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1544149604
# name: diplay
# license: MIT
from pprint import pprint


import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from display import *
from modules.deps.deps import deps
from modules.json_config.json_config import Json_config
del sys.path[0:2]

conf=Json_config()
deps(conf.data["deps"])

pprint(get_display())

pprint(get_all_windows())



