#!/usr/bin/env python3
from pprint import pprint
import os
import re
import subprocess
import sys
import time

class Mouse(object):
    def __init__(self, win_dec_id="", win_frame_upper_left_x="", win_frame_upper_left_y=""):
        self.win_dec_id=win_dec_id
        self.x=""
        self.y=""
        self.xy=""
        self.rx=""
        self.ry=""
        self.rxy=""

    def get_x(self):
        self.update_coords()
        return self.x

    def get_y(self):
        self.update_coords()
        return self.y

    def update_coords(self):
        if self.win_dec_id == "":
            for line in subprocess.check_output(["xdotool", "getmouselocation"]).decode().rstrip().splitlines():
                for elem in line.split():
                    attrs=elem.split(":")
                    if attrs[0] == "x":
                        self.x=int(attrs[1])
                    elif attrs[0] == "y":
                        self.y=int(attrs[1])

            self.xy=[self.x, self.y]

        return self

    def get_coords(self):
        self.update_coords()
        return self.xy

    def set_coords(self, x, y):
        os.system("xdotool mousemove {} {}".format(x, y))

    def set_relative_coords(self, x, y, base_x="", base_y=""):
        dst_x = dst_y = ""
        if self.win_dec_id != "":
            if base_x != "" and base_y != "":
                dst_x=self.rx+base_x+int(x)
                dst_y=self.ry+base_y+int(y)
            else:
                dst_x=self.rx+int(x)
                dst_y=self.ry+int(y)
        else:
            self.update_coords()
            if base_x != "" and base_y != "":
                dst_x=base_x+int(x)
                dst_y=base_y+int(y)
            else:
                dst_x=self.x+int(x)
                dst_y=self.y+int(y)
        
        os.system("xdotool mousemove {} {}".format(dst_x, dst_y))

    def click(self, btn_num, win_dec_id=""):
        if win_dec_id != "":
            os.system("xdotool click --clearmodifiers --window {} {}".format(win_dec_id, btn_num))
        elif self.win_dec_id != "":
            os.system("xdotool click --clearmodifiers --window {} {}".format(self.win_dec_id, btn_num))
        else:
            os.system("xdotool click --clearmodifiers {}".format(btn_num))

    def left_click(self, win_dec_id=""):
        self.click(1, win_dec_id)

    def middle_click(self, win_dec_id=""):
        self.click(2, win_dec_id)

    def right_click(self, win_dec_id=""):
        self.click(3, win_dec_id)

    def scrollup(self, win_dec_id=""):
        self.click(4, win_dec_id)

    def scrolldown(self, win_dec_id=""):
        self.click(5, win_dec_id)

    def double_click(self, win_dec_id=""):
        self.click(1, win_dec_id)
        time.sleep(.1)
        self.click(1, win_dec_id)

    def triple_click(self, win_dec_id=""):
        self.click(1, win_dec_id)
        time.sleep(.1)
        self.click(1, win_dec_id)
        time.sleep(.1)
        self.click(1, win_dec_id)
