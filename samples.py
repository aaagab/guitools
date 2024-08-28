#!/usr/bin/env python3

if __name__ == "__main__":
    from typing import cast
    from pprint import pprint
    from contextlib import suppress
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
    with suppress(ImportError):
        import __init__ as pkg #type:ignore
        from __init__ import Window, Notify
    del sys.path[0]

    with open(os.path.join(direpa_script, "config", "config.json"), "r") as f:
        pkg._deps(json.load(f)["deps"])

    _xlib=pkg.XlibHelpers()

    # print("Select window with mouse click:")
    # print(_xlib.select())

    obj_monitors=pkg.Monitors()
    main_monitor=obj_monitors.get_primary_monitor()
    for monitor in obj_monitors.monitors:
        monitor.print()
        
    print(main_monitor.name)

    executable=pkg._xdginfo('.')[1]
    if "dolphin" in executable:
        executable+=" --new-window"

    # executable="/usr/bin/featherpad --win"
    # executable="/usr/bin/kate"
    # executable="/usr/bin/konsole"
    for window in pkg.Windows().regular_windows:
        print(window.class_name, window.class_name_short, window.name)

    # print()
    # xwin=_xlib.get_recent_window_from_class("Code")
    # print(pkg.Window(xwin=xwin).name)
    # xwin=_xlib.get_recent_window_from_class("dolphin")
    # print(pkg.Window(xwin=xwin).name)
    # xwin=_xlib.get_recent_window_from_class("konsole")
    # print(pkg.Window(xwin=xwin).name)
    # xwin=_xlib.get_recent_window_from_class("firefox")
    # print(pkg.Window(xwin=xwin).name)

    with pkg.Notify(start_thread=False) as notify:
        procs:list[subprocess.Popen[bytes]]=[]
        windows=[] #type:ignore
        with suppress(NameError): windows=cast(list[Window], windows)

        try:
            width=600
            height=600 
            x=50
            y=50
            step=25

            for i in range(5):
                index=i+1
                proc = subprocess.Popen(shlex.split("{} .".format(executable)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                procs.append(proc)
                hex_id=_xlib.get_window_hex_id_from_pid(proc.pid)
                xwin=_xlib.get_window_from_hex_id(hex_id)
                window=pkg.Window(xwin=xwin)
                windows.append(window)
                window.resize(width=width, height=width)
                window.move(x=x+main_monitor.x, y=y+main_monitor.y)
                x+=step
                y+=step
                width+=step
                height+=step

            width=600
            height=600 
            x=100
            y=100
            step=50
            for window in windows:
                window.set_geometry(x=x+main_monitor.x, y=y+main_monitor.y, width=width, height=height)
                x+=step
                y+=step
                width+=step
                height+=step
                time.sleep(.5)

            for window in windows:
                window.set_sticky()
                window.unset_sticky()
                window.set_above()
                window.unset_above()
                window.set_below()
                window.unset_below()
                window.focus()
                window.minimize()
                time.sleep(.5)
                window.maximize()
                time.sleep(.5)
                window.set_geometry(x=100+main_monitor.x, y=100+main_monitor.y, width=500, height=500)
                time.sleep(.2)
                window.unmap()
                time.sleep(.5)
                window.map()
                time.sleep(.5)
                window.center(monitor=main_monitor)
                time.sleep(.5)
                window.set_name(f"test window {windows.index(window)+1}")
                print(window.get_name())
                time.sleep(1)
                window.set_fullscreen()
                time.sleep(1)
                window.close()
                time.sleep(.2)
        finally:
            for window in windows:
                window.close()

    proc = subprocess.Popen(shlex.split("{} .".format(executable)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        hex_id=_xlib.get_window_hex_id_from_pid(proc.pid) # careful with this function as several different windows can share the same pid (ie: firefox, chrome, code)
        xwin=_xlib.get_window_from_hex_id(hex_id)
        window=pkg.Window(xwin=xwin)

        window.tile(move=pkg.TileMove.LEFT)
        window.ptr.set_relative_coords(300,100)
        time.sleep(1)


        window.tile(move=pkg.TileMove.RIGHT)
        window.ptr.set_relative_coords(200,50)
        time.sleep(1)

        window.kbd.key("Menu")
        time.sleep(1)
        window.kbd.key("Escape")
        time.sleep(1)
        window.kbd.key("Ctrl+l")
        window.kbd.type("/data/bin")
        time.sleep(1)
        window.kbd.key("Escape")

        timer=pkg._TimeOut(0).start()
        for win in pkg.Windows().regular_windows:
            win.print()
        print(timer.get_elapsed_time())

        for monitor in pkg.Monitors().monitors:
            for move in [pkg.TileMove.LEFT, pkg.TileMove.MAXIMIZE, pkg.TileMove.RIGHT]:
                retval=window.tile(move=move,monitor_index=monitor.index)
                print("monitor:", monitor.index, " tile:", move.name, " retval:", retval)
                window.focus()
                time.sleep(.2)

        active_window=pkg.Windows.get_active_window()
        print(active_window.pid)
        window.set_exe_info()
        pprint(vars(window.exe_info))
        print(window.name)
        print("monitor:", window.monitor.index)

        window.tile(move=pkg.TileMove.LEFT,monitor_index=0)

        time.sleep(.5)
        window.set_above()
        window.maximize()
        window.focus()
        window.unset_above()

        time.sleep(.5)
        window.set_above()
        window.tile(move=pkg.TileMove.LEFT)
        window.focus()
        window.unset_above()

        time.sleep(.5)
        window.set_above()
        window.tile(move=pkg.TileMove.RIGHT)
        window.focus()
        window.unset_above()

        time.sleep(.5)
        window.set_above()
        window.minimize()
        window.unset_above()

        window=pkg.Windows().get_window(window.hex_id)
        window.print()

        time.sleep(1)
        window.set_above()
        window.set_geometry(x=100, y=128, width=200, height=200)
        window.focus()
        window.unset_above()

        time.sleep(1)
        window.set_above()
        window.center()
        window.focus()
        window.unset_above()

        for monitor in pkg.Monitors().monitors:
            monitor.print()
            tiles=monitor.get_tiles(xdivs=2, ydivs=2, cover_taskbar=False, tile_nums=[1,4])
            for tile in tiles:
                    tile.print()
                    time.sleep(0.5)
                    window.set_above()
                    window.set_geometry(
                            x=tile.x, 
                            y=tile.y, 
                            width=tile.width, 
                            height=tile.height)
                    
                    window.focus()
                    window.unset_above()

        for monitor in pkg.Monitors().monitors:
            monitor.print()
            tiles=monitor.get_tiles(xdivs=3, ydivs=3, cover_taskbar=False)
            for tile in tiles:
                    time.sleep(0.2)
                    window.set_above()
                    window.set_geometry(
                            x=tile.x, 
                            y=tile.y, 
                            width=tile.width, 
                            height=tile.height)
                    
                    window.focus()
                    window.unset_above()

        windows=pkg.Windows().regular_windows
        for window in windows:
            window.print()
        print()
        windows=pkg.Windows.sorted_by_class(windows=pkg.Windows().regular_windows)
        for window in windows:
            window.print()

        mouse=pkg.Mouse()
        for monitor in pkg.Monitors().monitors:
            for tile in monitor.get_tiles(xdivs=10, ydivs=10, cover_taskbar=False):
                time.sleep(.05)
                mouse.set_coords(tile.x, tile.y)

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
    finally:
        proc.kill()

