#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1545414114
# name: guitools
# license: MIT
from pprint import pprint
import sys, os
import time
import shlex

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from guitools import *
from modules.deps.deps import deps
from modules.json_config.json_config import Json_config
from modules.xdginfo.xdginfo import xdginfo
from modules.timeout.timeout import Timeout

del sys.path[0:2]

conf=Json_config()
deps(conf.data["deps"])

timer=Timeout(0)
Regular_windows().print()
print(timer.get_elapsed_time())
sys.exit()

executable=xdginfo('.')[1]
proc = subprocess.Popen(shlex.split("{} .".format(executable)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
hex_id=Windows.get_window_hex_id_from_pid(proc.pid)
window=Window(hex_id)
print(window.pid)

window.tile("left",0)
print(window.get_tile())
print(window.monitor.index)
window.focus()
time.sleep(.5)

window.tile("right",0)
print(window.get_tile())
print(window.monitor.index)
window.focus()
time.sleep(.5)

window.maximize(0)
print(window.get_tile())
print(window.monitor.index)
window.focus()
time.sleep(.5)

window.tile("left",1)
print(window.get_tile())
print(window.monitor.index)
window.focus()
time.sleep(.5)

window.tile("right",1)
print(window.get_tile())
print(window.monitor.index)
window.focus()
time.sleep(.5)

window.maximize(1)
print(window.get_tile())
print(window.monitor.index)
window.focus()
time.sleep(.5)

active_window=Windows().get_active()
print(active_window.pid)
print(window.command)
print(window.name)
print(window.monitor.index)

window.tile("left",0)

direction=["left", "right"]
counter=0
index=0
while direction:
    time.sleep(.3)
    if window.tile(direction[index]):
        if index==0:
            index=1
        else:
            index=0
        counter+=1

    if counter == 4:
        break

# time.sleep(1)
# window.close()
# sys.exit()

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
            time.sleep(0.2)
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
for monitor in Monitors().monitors:
    for tile in monitor.get_tiles(10, 10, True):
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
