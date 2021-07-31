#!/usr/bin/env python3

if __name__ == "__main__":
    from pprint import pprint
    import importlib
    import json
    import os
    import shlex
    import subprocess
    import sys
    import time

    direpa_script=os.path.dirname(os.path.realpath(__file__))
    direpa_script_parent=os.path.dirname(direpa_script)
    module_name=os.path.basename(direpa_script)
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    with open(os.path.join(direpa_script, "config", "config.json"), "r") as f:
        pkg.deps(json.load(f)["deps"])

    # cmd_filter_bad_window("wmctrl -i -a 0x00600005")
    # cmd_filter_bad_window("wmctrl -l")

    # keep this part commented ####################

    # launch_window=pkg.Window_open("firefox")
    # while not launch_window.has_window():
    #     user_input=input("Do you want to continue(y/n): ")
    #     if user_input == "n":
    #         break
    # print(launch_window.window.name)
    # print(launch_window.is_existing_window)

    # launch_window=pkg.Window_open("code --new-window /data/projs/apps/dt/python/guitools/")
    # print(launch_window.window.name)
    # print(launch_window.is_existing_window)

    # launch_window=pkg.Window_open("ls -l")
    # while not launch_window.has_window():
    #     user_input=input("Do you want to continue(y/n): ")
    #     if user_input == "n":
    #         break
    # sys.exit()

    print("Select window with mouse click:")
    print(pkg.Window().select().hex_id)

    executable=pkg.xdginfo('.')[1]
    proc = subprocess.Popen(shlex.split("{} .".format(executable)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(proc.pid)
    hex_id=pkg.Windows.get_window_hex_id_from_pid(proc.pid) # careful with this function as several different windows can share the same pid (ie: firefox, chrome, code)
    window=pkg.Window(hex_id)
    window.print()

    window.tile("left")
    window.ptr.set_relative_coords(200,50)
    time.sleep(2)

    window.tile("right")
    window.ptr.set_relative_coords(200,50)
    time.sleep(2)

    window.kbd.key("Menu")
    time.sleep(1)
    window.kbd.key("Escape")
    time.sleep(1)
    window.kbd.key("Ctrl+l")
    window.kbd.type("/data/bin")
    time.sleep(1)
    window.kbd.key("Escape")

    timer=pkg.TimeOut(0).start()
    pkg.Regular_windows().print()
    print(timer.get_elapsed_time())

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

    active_window=pkg.Windows().get_active()
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

    window=pkg.Window(window.hex_id)
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

    for monitor in pkg.Monitors().monitors:
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

    for monitor in pkg.Monitors().monitors:
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

    windows=pkg.Windows()
    windows.print()
    print()
    windows=pkg.Windows().sorted_by_class().filter_regular_type()
    windows.print()

    mouse=pkg.Mouse()
    for monitor in pkg.Monitors().monitors:
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
