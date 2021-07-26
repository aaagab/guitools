#!/usr/bin/env python3
# author: Gabriel Auger
# name: guitools
# license: MIT
__version__= "2.0.2"

import sys
import os

from .dev.input import get_key_pressed
from .dev.keyboards import Keyboard
from .dev.monitors import Tile, Monitor, Monitors
from .dev.mouses import Mouse
from .dev.windows import Windows, Taskbars, Window, Regular_windows

from .gpkgs.deps import deps
from .gpkgs.xdginfo import xdginfo
from .gpkgs.timeout import TimeOut

