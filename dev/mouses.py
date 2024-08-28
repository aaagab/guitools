#!/usr/bin/env python3
from pprint import pprint
import os
import re
import subprocess
import sys
import time

class Mouse(object):
    def __init__(self, win_dec_id:int|None=None) -> None:
        self.win_dec_id=win_dec_id
        self.x:int=0
        self.y:int=0
        self.xy:int=0
        self.rx:int=0
        self.ry:int=0
        self.rxy:int=0

    def get_x(self):
        self.update_coords()
        return self.x

    def get_y(self):
        self.update_coords()
        return self.y

    def update_coords(self):
        if self.win_dec_id is None:
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

    def set_coords(self, x:int, y:int):
        os.system("xdotool mousemove {} {}".format(x, y))
        return self

    def set_relative_coords(self, x:int, y:int, base_x:int=0, base_y:int=0):
        dst_x:int=0
        dst_y:int=0
        if self.win_dec_id is None:
            self.update_coords()
            dst_x=base_x+x
            dst_y=base_y+y
        else:
            dst_x=self.rx+base_x+x
            dst_y=self.ry+base_y+y
        os.system("xdotool mousemove {} {}".format(dst_x, dst_y))
        return self

    def click(self, btn_num:int, win_dec_id:int|None=None):
        if win_dec_id is not None:
            os.system("xdotool click --clearmodifiers --window {} {}".format(win_dec_id, btn_num))
        elif self.win_dec_id is not None:
            os.system("xdotool click --clearmodifiers --window {} {}".format(self.win_dec_id, btn_num))
        else:
            os.system("xdotool click --clearmodifiers {}".format(btn_num))

    def left_click(self, win_dec_id:int|None=None):
        self.click(1, win_dec_id)

    def middle_click(self, win_dec_id:int|None=None):
        self.click(2, win_dec_id)

    def right_click(self, win_dec_id:int|None=None):
        self.click(3, win_dec_id)

    def scrollup(self, win_dec_id:int|None=None):
        self.click(4, win_dec_id)

    def scrolldown(self, win_dec_id:int|None=None):
        self.click(5, win_dec_id)

    def double_click(self, win_dec_id:int|None=None):
        self.click(1, win_dec_id)
        time.sleep(.1)
        self.click(1, win_dec_id)

    def triple_click(self, win_dec_id:int|None=None):
        self.click(1, win_dec_id)
        time.sleep(.1)
        self.click(1, win_dec_id)
        time.sleep(.1)
        self.click(1, win_dec_id)
