#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1544156629
# name: guitools
# license: MIT
from pprint import pprint

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from guitools import *
from modules.deps.deps import deps
from modules.json_config.json_config import Json_config
import time
del sys.path[0:2]

conf=Json_config()
deps(conf.data["deps"])

os.system("xdg-open .")
time.sleep(1.5)

window=Windows().get_active()
print(window.name)

time.sleep(.5)
window.set_above()
window.maximize()
window.focus()
window.unset_above()

time.sleep(.5)
window.set_above()
window.tile("left")
window.focus()
window.unset_above()

time.sleep(.5)
window.set_above()
window.tile("right")
window.focus()
window.unset_above()

time.sleep(.5)
window.set_above()
window.minimize()
window.unset_above()

window=Window(window.hex_id)
window.print()

time.sleep(1)
window.set_above()
window.set_geometry(dict(x=100, y=128, width=200, height=200))
window.focus()
window.unset_above()

time.sleep(1)
window.set_above()
window.center()
window.focus()
window.unset_above()

for monitor in Monitors().monitors:
    monitor.print()
    tiles=monitor.get_tiles(2, 2, True, [1,4])
    for tile in tiles:
            tile.print()
            time.sleep(0.5)
            window.set_above()
            window.set_geometry(dict(
                    x=tile.upper_left_x, 
                    y=tile.upper_left_y, 
                    width=tile.width, 
                    height=tile.height)
            )
            window.focus()
            window.unset_above()

for monitor in Monitors().monitors:
    monitor.print()
    tiles=monitor.get_tiles(3, 3, False)
    for tile in tiles:
            time.sleep(0.5)
            window.set_above()
            window.set_geometry(dict(
                    x=tile.upper_left_x, 
                    y=tile.upper_left_y, 
                    width=tile.width, 
                    height=tile.height)
            )
            window.focus()
            window.unset_above()

windows=Windows()
windows.print()
print()
windows=Windows().sorted_by_class().filter_regular_type()
windows.print()

mouse=Mouse()
for tile in Monitors().monitors[0].get_tiles(10, 10, True):
    time.sleep(.05)
    mouse.set_coords(tile.upper_left_x, tile.upper_left_y)

time.sleep(1)
if window.exists():
    print("Window still exists.")
window.close()
if not window.exists():
    print("window does not exists anymore.")

# mouse.click(3)
# mouse.right_click()
# mouse.double_click()
# mouse.triple_click()