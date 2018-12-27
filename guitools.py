#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1545942382
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

del sys.path[0:2]

