#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-rc-1543498732
# name: diplay
# license: MIT
from tkinter import *
import re
from pprint import pprint
import os

try:
    import modules.shell_helpers.shell_helpers as shell
except:
    sys.path.insert(1, os.path.join(sys.path[0], '..'))
    import shell_helpers.shell_helpers as shell

def get_monitor_from_coords(x, y, monitors):
    for monitor in monitors:
        x_found=False
        y_found=False
        if x >= monitor["range_x"][0] and x <= monitor["range_x"][1]:
            x_found=True

        if y >= monitor["range_y"][0] and y <= monitor["range_y"][1]:
            y_found=True
        
        if x_found and y_found:
            return monitor["name"]

    return ""

def get_display():
    root = Tk()

    display={}

    mouseX, mouseY =root.winfo_pointerxy()
    display.update(
        mouse=dict(
            x= mouseX,
            y= mouseY
        ),
        active_window=dict(
            dec_id=shell.cmd_get_value("xdotool getactivewindow")
        )
    )

    active_window_xwininfo=shell.cmd_get_value("xwininfo -id {}".format(display["active_window"]["dec_id"]))
    display["active_window"].update(
                hex_id=hex(int(display["active_window"]["dec_id"]))
            )

    display["active_window"].update(
                hex_id=hex(int(display["active_window"]["dec_id"]))
            )

    active_window_xprop=shell.cmd_get_value("xprop -id {} _NET_WM_PID WM_CLASS _NET_WM_NAME".format(display["active_window"]["dec_id"]))

    for line in active_window_xprop.splitlines():
        if "PID" in line:
            display["active_window"].update(
                pid=int(line.split("=")[1].strip())
            )
        elif "CLASS" in line:
            display["active_window"].update({
                "class":line.split("=")[1].split(",")[0].strip().replace('"','')
            })
        elif "NAME" in line:
            display["active_window"].update(
                name=line.split("=")[1].strip().replace('"','')
        )

    for line in active_window_xwininfo.splitlines():
        if "Absolute upper-left X:" in line:
            display["active_window"].update(
                upper_left_x=int(line.split(":")[1].strip())
            )
        elif "Absolute upper-left Y:" in line:
            display["active_window"].update(
                upper_left_y=int(line.split(":")[1].strip())
            )
        elif "Width:" in line:
            display["active_window"].update(
                width=int(line.split(":")[1].strip())
            )
        elif "Height:" in line:
            display["active_window"].update(
                height=int(line.split(":")[1].strip())
            )

    monitors=[]
    popup_relative_lower_right_x=-30
    popup_relative_lower_right_y=-50
    rgx_str_geometry=r".*\s(\d+)x(\d+)([\+\-]\d+)([\+\-]\d+)\s.*"
    for line in shell.cmd_get_value("xrandr").splitlines():
        if " connected" in line:
            geometry=re.match(rgx_str_geometry,line)
            if geometry:
                monitor=dict(
                    name=line.split(" ")[0],
                    width=int(geometry.group(1)),
                    height=int(geometry.group(2)),
                    upper_left_x=int(geometry.group(3)),
                    upper_left_y=int(geometry.group(4))
                )
                monitor.update(
                    range_x=[
                        monitor["upper_left_x"],
                        monitor["width"]+monitor["upper_left_x"]
                    ],
                    range_y=[
                        monitor["upper_left_y"],
                        monitor["height"]+monitor["upper_left_y"]
                    ],
                )
                monitors.append(monitor)

    display.update(monitors=monitors)

    display["active_window"].update(
        monitor=get_monitor_from_coords(
            display["active_window"]["upper_left_x"], 
            display["active_window"]["upper_left_y"], 
            monitors)
    )

    display["mouse"].update(
        monitor=get_monitor_from_coords(
            display["mouse"]["x"], 
            display["mouse"]["y"], 
            monitors)
    )

    return display

if __name__ == "__main__":
    try:
        from modules.deps.deps import deps
        from modules.json_config.json_config import Json_config
    except:
        sys.path.insert(1, os.path.join(sys.path[0], '..'))
        from deps.deps import deps
        from json_config.json_config import Json_config

    conf=Json_config()
    deps(conf.data["deps"])
