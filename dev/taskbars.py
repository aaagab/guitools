#!/usr/bin/env python3
from pprint import pprint
import os
import re
import sys

from .helpers import cmd_filter_bad_window

from ..gpkgs import message as msg
    
class Taskbar(object):
    def __init__(self):
        self.upper_left_x=""
        self.upper_left_y=""
        self.width=""
        self.height=""

class Taskbars(object):
    def __init__(self):
        xprop_fields=""
        while not xprop_fields:
            self.taskbars=[]
        
            window_ids=cmd_filter_bad_window("wmctrl -lGpx")
            for line in window_ids.splitlines():
                line=re.sub(r" +", " ", line.strip()).split(" ")
                hex_id=hex(int(line[0], 16))

                xprop_fields=cmd_filter_bad_window("xprop -id {} _NET_WM_WINDOW_TYPE".format(hex_id))
                if xprop_fields == "BadWindow":
                    xprop_fields=""
                    break

                if "_NET_WM_WINDOW_TYPE_DOCK" in xprop_fields:
                    taskbar=Taskbar()
                    taskbar.upper_left_x=int(line[3])
                    taskbar.upper_left_y=int(line[4])
                    taskbar.width=int(line[5])
                    taskbar.height=int(line[6])
                    self.taskbars.append(taskbar)