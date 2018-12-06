#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-rc-1544109312
# name: diplay
# license: MIT
from pprint import pprint

from modules.importpath.importpath import Import_path

import_path=Import_path().open()
try:
    from display import get_display
    import_path.success()
except Exception as e:
    import_path.error(e)
import_path.close()


pprint(get_display())
