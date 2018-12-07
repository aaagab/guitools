#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-beta-1544149179
# name: bwins
# license: MIT

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import modules.shell_helpers.shell_helpers as shell
del sys.path[0:2]

import re
from pprint import pprint

def get_all_windows():
    # wmctrl -lpGx
    windows=shell.cmd_get_value("wmctrl -lpGx")
    obj_windows=[]
    for window in windows.splitlines():
        divider=True
        field=""
        fields=[]
        num_fields=10
        field_num=1
        last_field_started=False
        for i, c in enumerate(window):
            if i == 0:
                field+=c
            elif i < len(window)-1:
                if field_num < num_fields:
                    if c == " ":
                        if not window[i-1] == " ":
                            fields.append(field)
                            field_num+=1
                            field=""
                    else:

                        field+=c
                else:
                    if last_field_started:
                        field+=c
                    else:
                        if c != " ":
                            last_field_started=True
                            field+=c
            else:
                # print(field_num)
                field+=c
                fields.append(field)
                field_num+=1
                field=""
        
        obj_windows.append({
            "hex_id": fields[0],
            "dec_id": int(fields[0], 16),
            "sticky": True if fields[1] == "-1" else False,
            "pid": int(fields[2]),
            "upper_left_x": int(fields[3]),
            "upper_left_y": int(fields[4]),
            "width": int(fields[5]),
            "height": int(fields[6]),
            "class_long": fields[7],
            "class": fields[7].split(".")[0],
            "hostname": fields[8],
            "name": fields[9]
        })

    return obj_windows
