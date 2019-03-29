#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.1.0
# name: guitools
# license: MIT
import re
from pprint import pprint

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import modules.shell_helpers.shell_helpers as shell
from dev.monitors import *
from dev.mouses import *
from dev.windows import *
from dev.input import get_key_pressed

del sys.path[0:2]

