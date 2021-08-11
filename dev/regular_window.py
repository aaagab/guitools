#!/usr/bin/env python3
from pprint import pprint
import os
import re
import sys
import time

from .helpers import get_exe_paths_from_pid, cmd_filter_bad_window, bubble_sort_array

from ..gpkgs import message as msg

class Regular_windows(object):
    def __init__(self):
        self.windows=[]
        self.windows_hex_ids=[]
        self.desktop_hex_ids=[]
        self.set_windows()
        self.sorted_by_exe_names()

    def set_windows(self):
        xprop_fields=""
        while not xprop_fields:
            self.windows=[]
            self.desktop_hex_ids=[]

            window_ids=cmd_filter_bad_window("wmctrl -lpx")

            for line in window_ids.splitlines():
                tmp_line=re.sub(' +', ' ', line.strip()).split(" ")
                hex_id=hex(int(tmp_line[0], 16))
                xprop_fields=cmd_filter_bad_window("xprop -id {} _NET_WM_WINDOW_TYPE".format(hex_id))
                if xprop_fields == "BadWindow":
                    xprop_fields=""
                    break

                if "_NET_WM_WINDOW_TYPE_NORMAL" in xprop_fields or "not found" in xprop_fields:
                    window=dict(
                        hex_id=hex_id,
                        pid=int(tmp_line[2]),
                        _class=tmp_line[3].split(".")[0],
                        name=" ".join(tmp_line[5:]),
                    )

                    exe_name, command, filenpa_exe = get_exe_paths_from_pid(window["pid"])

                    window.update(
                        exe_name=exe_name,
                        command=command,
                        filenpa_exe=filenpa_exe
                    )

                    self.windows.append(window)
                    self.windows_hex_ids.append(hex_id)
                if "_NET_WM_WINDOW_TYPE_DESKTOP" in xprop_fields:
                    self.desktop_hex_ids.append(hex_id)
        
    @staticmethod
    def focus(hex_id):
        cmd_filter_bad_window("wmctrl -i -a {}".format(hex_id), False)
    
    @staticmethod
    def minimize(hex_id):
        dec_id=int(hex_id, 16)
        os.system("xdotool windowminimize {}".format(dec_id))

    def print(self):
        for window in self.windows:
            pprint(window)

    def sorted_by_exe_names(self):
        exe_names=[]
        for window in self.windows:
            exe_names.append(window["exe_name"].lower())

        exe_names=sorted(set(exe_names))

        tmp_windows=[]
        for exe_name in exe_names:
            tmp_names=[]
            tmp_indexes=[]
            for w, window in enumerate(self.windows):
                if window["exe_name"].lower() == exe_name:
                    tmp_indexes.append(w)                        
                    tmp_names.append(window["name"].lower())

            for index in bubble_sort_array(tmp_names, len(tmp_names)):
                tmp_windows.append(self.windows[tmp_indexes[index]])

        self.windows=tmp_windows

        return self