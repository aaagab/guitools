#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1545413888
# name: guitools
# license: MIT

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from windows import Windows, Taskbars, Window


import modules.shell_helpers.shell_helpers as shell
from mouses import *

del sys.path[0:2]

import re
from pprint import pprint
import copy

class Tile(object):
    def __init__(self):
        self.upper_left_x=""
        self.upper_left_y=""
        self.width=""
        self.height=""
        self.nums=""
        self.index=""
        self.range_x=[]
        self.range_y=[]

    def print(self):
        pprint(vars(self))

    def contains(self, x, y):
        x_found=False
        y_found=False
        if x >= self.range_x[0] and x < self.range_x[1]:
            x_found=True

        if y >= self.range_y[0] and y < self.range_y[1]:
            y_found=True
        
        if x_found and y_found:
            return True
        else:
            return False

class Monitor(object):
    def __init__(self):
        self.name=""
        self.width=""
        self.height=""
        self.upper_left_x=""
        self.upper_left_y=""
        self.range_x=""
        self.range_y=""
        # taskbar attribute
        self.tb_width=""
        self.tb_height=""
        self.tb_upper_left_x=""
        self.tb_upper_left_y=""
        self.tb_range_x=""
        self.tb_range_y=""

        self.index=""

    def print(self):
        pprint(vars(self))

    def contains(self, x, y):
        x_found=False
        y_found=False
        if x >= self.range_x[0] and x <= self.range_x[1]:
            x_found=True

        if y >= self.range_y[0] and y <= self.range_y[1]:
            y_found=True
        
        if x_found and y_found:
            return True
        else:
            return False

    def get_tiles(self, int_v_divs, int_h_divs, bool_taskbar, tile_nums=[]):
        if tile_nums:
            if not isinstance(tile_nums, list):
                tile_nums=[tile_nums]

        num_tiles= int_v_divs * int_h_divs
        tmp_tile_nums=copy.deepcopy(tile_nums)
        tile_width=""
        tile_height=""

        if bool_taskbar:
            tile_width=int(self.tb_width/int_v_divs)
            tile_height=int(self.tb_height/int_h_divs)
        else:
            tile_width=int(self.width/int_v_divs)
            tile_height=int(self.height/int_h_divs)

        tiles=[]
        index=1
        for h_div in range(int_h_divs):
            for v_div in range(int_v_divs):
                tile=Tile()
                tile.upper_left_x=self.upper_left_x+(v_div*tile_width)
                tile.upper_left_y=self.upper_left_y+(h_div*tile_height)
                tile.width=tile_width
                tile.height=tile_height
                tile.index=index
                tile.range_x=[
                    tile.upper_left_x,
                    tile.upper_left_x+tile.width
                ]
                tile.range_y=[
                    tile.upper_left_y,
                    tile.upper_left_y+tile.height
                ]
                tile.nums=num_tiles

                if tile_nums:
                    for value in tmp_tile_nums:
                        if value == index:
                            tiles.append(tile)
                            tmp_tile_nums.remove(value)
                            break
                else:
                    tiles.append(tile)

                index+=1
            
            if tile_nums:
                if len(tiles) == len(tile_nums):
                    break

        return tiles

class Monitors(object):
    def __init__(self):
        self.monitors=[]
        self.get_monitors()

    def get_monitor_from_coords(self, x, y):
        for monitor in self.monitors:
            if monitor.contains(x, y):
                return monitor

        return ""

    def get_active(self):
        monitor=""
        if len(self.monitors) > 1:
            # active_win=Windows().get_active()
            active_win_hex_id=Windows.get_active_hex_id()
            if active_win_hex_id != "":
                active_win=Window(active_win_hex_id)
                monitor=self.get_monitor_from_coords(
                    active_win.upper_left_x,
                    active_win.upper_left_y,
                )
            if not monitor:
                x, y = Mouse().get_coords()
                monitor=self.get_monitor_from_coords(x, y)
                if not monitor:
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

    def get_monitors(self):
        monitors=[]
        rgx_str_geometry=r".*\s(\d+)x(\d+)([\+\-]\d+)([\+\-]\d+)\s.*"

        taskbars=Taskbars().taskbars
        monitor_index=0
        for line in shell.cmd_get_value("xrandr").splitlines():
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
