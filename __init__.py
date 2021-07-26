#!/usr/bin/env python3
# author: Gabriel Auger
# name: guitools
# license: MIT
__version__= "2.0.1"

import sys
import os

from .dev.input import get_key_pressed
from .dev.keyboards import Keyboard
from .dev.monitors import Tile, Monitor, Monitors
from .dev.mouses import Mouse
from .dev.windows import Windows, Taskbars, Window, Regular_windows

if hasattr(sys.modules["__main__"], "__file__"):
    direpa_main=os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
    direpa_file=os.path.dirname(os.path.realpath(__file__))
    if direpa_file == direpa_main:
        from .gpkgs.deps import deps
        from .gpkgs.xdginfo import xdginfo
        from .gpkgs.timeout import TimeOut

