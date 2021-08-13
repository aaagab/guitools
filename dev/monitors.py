#!/usr/bin/env python3
from pprint import pprint
import copy
import os
import re
import sys
import subprocess

from .monitor import Monitor
from .mouses import Mouse
from .taskbars import Taskbars
from .window import Window
from .windows import Windows

class Monitors(object):
    def __init__(self):
        self.monitors=[]
        self.set_monitors()

    def get_monitor_from_coords(self, x, y, width, height):
        for monitor in self.monitors:
            if monitor.contains(x+width, y+height):
                return monitor

        return None

    def get_active(self, active_win_hex_id=None):
        monitor=""
        if len(self.monitors) > 1:
            if active_win_hex_id is None:
                active_win_hex_id=Windows.get_active_hex_id()
            if active_win_hex_id != "":
                active_win=Window(active_win_hex_id)
                monitor=self.get_monitor_from_coords(
                    active_win.frame_upper_left_x,
                    active_win.frame_upper_left_y,
                    active_win.frame_width,
                    active_win.frame_height,
                )
            if monitor is None:
                x, y = Mouse().get_coords()
                monitor=self.get_monitor_from_coords(x, y, 0, 0)
                if monitor is None:
                    monitor=self.monitors[0]
        else:
            monitor=self.monitors[0]

        return monitor

    def get_taskbar_position(self, taskbar, monitor):
        # left, top, right, bottom
        if taskbar.width == monitor.width:
            if taskbar.upper_left_x == monitor.upper_left_x:
                if taskbar.upper_left_y == monitor.upper_left_y:
                    return "top"
                elif taskbar.upper_left_y == (monitor.upper_left_y + monitor.height - taskbar.height):
                    return "bottom"
                else:
                    return "none"
            else:
                return "none"
        elif taskbar.height == monitor.height:
            if taskbar.upper_left_y == monitor.upper_left_y:
                if taskbar.upper_left_x == monitor.upper_left_x:
                    return "left"
                elif taskbar.upper_left_x == (monitor.upper_left_x + monitor.width - taskbar.width):
                    return "right"
                else:
                    return "none"
            else:
                return "none"
        else:
            return "none"
        pass

    def set_taskbar_attrs(self, taskbar, monitor):
        position=self.get_taskbar_position(taskbar, monitor)
        if position == "bottom":
            monitor.tb_width=monitor.width
            monitor.tb_height=monitor.height-taskbar.height
            monitor.tb_upper_left_x=monitor.upper_left_x
            monitor.tb_upper_left_y=monitor.upper_left_y
            monitor.tb_range_x=[
                monitor.upper_left_x,
                monitor.upper_left_x+monitor.width
            ]
            monitor.tb_range_y=[
                monitor.upper_left_y,
                monitor.upper_left_y+monitor.height-taskbar.height
            ]
        elif position == "top":
            monitor.tb_width=monitor.width
            monitor.tb_height=monitor.height-taskbar.height
            monitor.tb_upper_left_x=monitor.upper_left_x
            monitor.tb_upper_left_y=monitor.upper_left_y+taskbar.height
            monitor.tb_range_x=[
                monitor.upper_left_x,
                monitor.upper_left_x+monitor.width
            ]
            monitor.tb_range_y=[
                monitor.upper_left_y+taskbar.height,
                monitor.upper_left_y+monitor.height
            ]
        elif position == "left":
            monitor.tb_width=monitor.width-taskbar.width
            monitor.tb_height=monitor.height
            monitor.tb_upper_left_x=monitor.upper_left_x+taskbar.width
            monitor.tb_upper_left_y=monitor.upper_left_y
            monitor.tb_range_x=[
                monitor.upper_left_x+taskbar.width,
                monitor.upper_left_x+monitor.width
            ]
            monitor.tb_range_y=[
                monitor.upper_left_y,
                monitor.upper_left_y+monitor.height
            ]
        elif position == "right":
            monitor.tb_width=monitor.width-taskbar.width
            monitor.tb_height=monitor.height
            monitor.tb_upper_left_x=monitor.upper_left_x
            monitor.tb_upper_left_y=monitor.upper_left_y
            monitor.tb_range_x=[
                monitor.upper_left_x,
                monitor.upper_left_x+monitor.width-taskbar.width
            ]
            monitor.tb_range_y=[
                monitor.upper_left_y,
                monitor.upper_left_y+monitor.height
            ]
        elif position == "none":
            pass

    def set_monitors(self):
        monitors=[]
        rgx_str_geometry=r".*\s(\d+)x(\d+)([\+\-]\d+)([\+\-]\d+)\s.*"

        taskbars=Taskbars().taskbars
        monitor_index=0
        # for line in shell.cmd_get_value("xrandr").splitlines():
        for line in subprocess.check_output(["xrandr"]).decode().rstrip().splitlines():
            if " connected" in line:
                geometry=re.match(rgx_str_geometry,line)
                if geometry:
                    monitor=Monitor()
                    monitor.name=line.split(" ")[0]
                    monitor.width=int(geometry.group(1))
                    monitor.height=int(geometry.group(2))
                    monitor.upper_left_x=int(geometry.group(3))
                    monitor.upper_left_y=int(geometry.group(4))
                    monitor.range_x=[
                        monitor.upper_left_x,
                        monitor.width+monitor.upper_left_x
                    ]
                    monitor.range_y=[
                        monitor.upper_left_y,
                        monitor.height+monitor.upper_left_y
                    ]

                    monitor.tb_width=monitor.width
                    monitor.tb_height=monitor.height
                    monitor.tb_upper_left_x=monitor.upper_left_x
                    monitor.tb_upper_left_y=monitor.upper_left_y
                    monitor.tb_range_x=monitor.range_x
                    monitor.tb_range_y=monitor.range_y
                    
                    monitor.index=monitor_index
                    monitor_index+=1
                    for taskbar in taskbars:
                        if monitor.contains(taskbar.upper_left_x, taskbar.upper_left_y):
                            self.set_taskbar_attrs(taskbar, monitor)

                    self.monitors.append(monitor)

        return self
