#!/usr/bin/env python3
from pprint import pprint
import copy
import os
import re
import sys
import subprocess

from Xlib.display import Display
from Xlib.xobject.drawable import Window as XlibWindow

from .monitor import Monitor
from .mouses import Mouse
from .taskbars import Taskbars, Taskbar

from .xlibhelpers import XlibHelpers

class Monitors():
    def __init__(self,
        display:Display|None=None, 
        root:XlibWindow|None=None,
    ) -> None:
        self._xlib=XlibHelpers(display=display, root=root)
        self.display=self._xlib.display
        self.root=self._xlib.root
        self.monitors:list[Monitor]=[]
        self.set_monitors()

    def get_monitor_from_coords(self, x:int, y:int, width:int, height:int):
        for monitor in self.monitors:
            if monitor.contains(x+width, y+height):
                return monitor
        return None
    
    def get_primary_monitor(self):
        for monitor in self.monitors:
            if monitor.is_primary is True:
                return monitor
        return None

    def get_active_monitor(self, active_win_hex_id:str|None=None) -> Monitor:
        monitor:Monitor
        if len(self.monitors) > 1:
            if active_win_hex_id is None:
                active_win_hex_id=self._xlib.get_active_window_hex_id()
            if active_win_hex_id is not None:
                active_win=self._xlib.get_window_from_hex_id(active_win_hex_id)
                if active_win is not None:
                    geometry=self._xlib.get_geometry(active_win, show_frame=False)
                    monitor=self.get_monitor_from_coords(
                        geometry.x,
                        geometry.y,
                        geometry.width,
                        geometry.height,
                    )
            if monitor is None:
                x, y = Mouse().get_coords()
                monitor=self.get_monitor_from_coords(x, y, 0, 0)
                if monitor is None:
                    monitor=self.monitors[0]
        else:
            monitor=self.monitors[0]
        return monitor

    def get_taskbar_position(self, taskbar:Taskbar, monitor:Monitor):
        # left, top, right, bottom
        if taskbar.width == monitor.width:
            if taskbar.x == monitor.x:
                if taskbar.y == monitor.y:
                    return "top"
                elif taskbar.y == (monitor.y + monitor.height - taskbar.height):
                    return "bottom"
                else:
                    return "none"
            else:
                return "none"
        elif taskbar.height == monitor.height:
            if taskbar.y == monitor.y:
                if taskbar.x == monitor.x:
                    return "left"
                elif taskbar.x == (monitor.x + monitor.width - taskbar.width):
                    return "right"
                else:
                    return "none"
            else:
                return "none"
        else:
            return "none"
        pass

    def set_taskbar_attrs(self, taskbar:Taskbar, monitor:Monitor):
        position=self.get_taskbar_position(taskbar, monitor)
        if position == "bottom":
            monitor.tb_width=monitor.width
            monitor.tb_height=monitor.height-taskbar.height
            monitor.tb_x=monitor.x
            monitor.tb_y=monitor.y
            monitor.tb_range_x=[
                monitor.x,
                monitor.x+monitor.width
            ]
            monitor.tb_range_y=[
                monitor.y,
                monitor.y+monitor.height-taskbar.height
            ]
        elif position == "top":
            monitor.tb_width=monitor.width
            monitor.tb_height=monitor.height-taskbar.height
            monitor.tb_x=monitor.x
            monitor.tb_y=monitor.y+taskbar.height
            monitor.tb_range_x=[
                monitor.x,
                monitor.x+monitor.width
            ]
            monitor.tb_range_y=[
                monitor.y+taskbar.height,
                monitor.y+monitor.height
            ]
        elif position == "left":
            monitor.tb_width=monitor.width-taskbar.width
            monitor.tb_height=monitor.height
            monitor.tb_x=monitor.x+taskbar.width
            monitor.tb_y=monitor.y
            monitor.tb_range_x=[
                monitor.x+taskbar.width,
                monitor.x+monitor.width
            ]
            monitor.tb_range_y=[
                monitor.y,
                monitor.y+monitor.height
            ]
        elif position == "right":
            monitor.tb_width=monitor.width-taskbar.width
            monitor.tb_height=monitor.height
            monitor.tb_x=monitor.x
            monitor.tb_y=monitor.y
            monitor.tb_range_x=[
                monitor.x,
                monitor.x+monitor.width-taskbar.width
            ]
            monitor.tb_range_y=[
                monitor.y,
                monitor.y+monitor.height
            ]
        elif position == "none":
            pass

    def set_monitors(self):
        taskbars=Taskbars().taskbars
        display = Display()
        root = display.screen().root
        coords=dict()
        for m in root.xrandr_get_monitors(is_active=False).monitors:
            monitor=Monitor()
            monitor.is_primary=m.primary == 1
            monitor.name=display.get_atom_name(m.name)
            monitor.width=m.width_in_pixels
            monitor.height=m.height_in_pixels
            monitor.x=m.x
            monitor.y=m.y
            monitor.range_x=[
                monitor.x,
                monitor.width+monitor.x
            ]
            monitor.range_y=[
                monitor.y,
                monitor.height+monitor.y
            ]

            monitor.tb_width=monitor.width
            monitor.tb_height=monitor.height
            monitor.tb_x=monitor.x
            monitor.tb_y=monitor.y
            monitor.tb_range_x=monitor.range_x
            monitor.tb_range_y=monitor.range_y
            
            for taskbar in taskbars:
                if monitor.contains(taskbar.x, taskbar.y):
                    self.set_taskbar_attrs(taskbar, monitor)

            if m.x not in coords:
                coords[m.x]=dict()
            if m.y not in coords[m.x]:
                coords[m.x][m.y]=dict()
            if monitor.name not in coords[m.x][m.y]:
                coords[m.x][m.y][monitor.name]=[]
            coords[m.x][m.y][monitor.name]=[]
            coords[m.x][m.y][monitor.name].append(monitor)

        index=0
        for x in sorted(coords):
            for y in sorted(coords[x]):
                for name in sorted(coords[x][y]):
                    for mon in sorted(coords[x][y][name]):
                        mon.index=index
                        self.monitors.append(mon)
                        index+=1

        return self
