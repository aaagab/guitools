#!/usr/bin/env python3
from pprint import pprint
import os
import re
import subprocess
import sys

from .helpers import cmd_filter_bad_window, bubble_sort_array
from .window import Window

from ..gpkgs.timeout import TimeOut
from ..gpkgs import message as msg

class Windows(object):
    def __init__(self, obj_monitors=None):
        self.windows=[]
        self.obj_monitors=obj_monitors
        if self.obj_monitors is None:
            self.set_obj_monitors()
        self.get_all_windows()
    
    def get_active(self):
        hex_id=self.get_active_hex_id()
        if not hex_id:
            return ""
        else:
            return Window(obj_monitors=self.obj_monitors).update_fields(hex_id)

    def set_obj_monitors(self):
        from .monitors import Monitors
        self.obj_monitors=Monitors()
        return self

    @staticmethod
    def get_desktop_status():
        desktop_info=cmd_filter_bad_window("wmctrl -m")
        desktop_status=""
        if "mode: ON" in desktop_info:
            desktop_status="on"
        elif "mode: OFF" in desktop_info:
            desktop_status="off"

        return desktop_status

    @staticmethod
    def show_desktop(on_off="on"):
        timer=TimeOut(10).start()
        while Windows.get_desktop_status() != on_off.lower():
            cmd_filter_bad_window("wmctrl -k {}".format(on_off), False)
            if timer.has_ended(pause=.001):
                msg.error("Impossible to set show_desktop '{}'".format(on_off))
                sys.exit()

        return Windows.get_active_hex_id()

    @staticmethod
    def get_window_hex_id_from_pid(pid):
        timer=TimeOut(3).start()
        while True:
            window_ids=cmd_filter_bad_window("wmctrl -lp")

            for line in window_ids.splitlines():
                tmp_line=re.sub(' +', ' ', line.strip())
                tmp_line=tmp_line.split(" ")
                hex_id=hex(int(tmp_line[0], 16))
                line_pid=int(tmp_line[2])
                if pid == line_pid:
                    return hex_id
            
            if timer.has_ended(pause=.001):
                msg.warning("no hex_id for pid '{}'".format(pid))
                break

        return ""

    @staticmethod
    def get_active_hex_id():
        hex_id=hex(int(subprocess.check_output(["xdotool", "getactivewindow"]).decode().rstrip()))
        # hex_id=hex(int(shell.cmd_get_value("xdotool getactivewindow")))
        if not hex_id:
            return ""
        else:
            return hex_id

    @staticmethod
    def exists(hex_id):
        window_ids=cmd_filter_bad_window("wmctrl -l")
        for line in window_ids.splitlines():
            line_hex_id=hex(int(line.split(" ")[0].strip(), 16))
            if hex_id == line_hex_id:
                return True
        
        return False

    def get_all_windows(self):
        window_ids=cmd_filter_bad_window("wmctrl -l")

        for line in window_ids.splitlines():
            hex_id=hex(int(line.strip().split(" ")[0], 16))
            self.windows.append(Window(obj_monitors=self.obj_monitors).update_fields(hex_id))
        return self

    def filter_regular_type(self):
        tmp_windows=[]
        for window in self.windows:
            if window.type == "_NET_WM_WINDOW_TYPE_NORMAL" or window.type == "UNKNOWN":
                tmp_windows.append(window)

        self.windows=tmp_windows

        return self

    def get_taskbars(self):
        tmp_windows=[]
        for window in self.windows:
            if window.type == "_NET_WM_WINDOW_TYPE_DOCK":
                tmp_windows.append(window)

        return tmp_windows

    def sorted_by_class(self):
        classes=[]
        for window in self.windows:
            classes.append(window._class.lower())

        classes=sorted(set(classes))

        tmp_windows=[]
        for _class in classes:
            tmp_names=[]
            tmp_indexes=[]
            for w, window in enumerate(self.windows):
                if window._class.lower() == _class:
                    tmp_indexes.append(w)                        
                    tmp_names.append(window.name.lower())

            for index in bubble_sort_array(tmp_names, len(tmp_names)):
                tmp_windows.append(self.windows[tmp_indexes[index]])

        self.windows=tmp_windows

        return self

    def print(self):
        for window in self.windows:
            window.print()
