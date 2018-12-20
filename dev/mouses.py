#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1545324749
# name: guitools
# license: MIT

import sys, os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import modules.shell_helpers.shell_helpers as shell

del sys.path[0:2]

import re
from pprint import pprint

class Mouse(object):
    def __init__(self):
        pass

    def get_x(self):
        return self.get_coords()[0]

    def get_y(self):
        return self.get_coords()[1]

    def get_coords(self):
        for line in shell.cmd_get_value("xdotool getmouselocation").splitlines():
            for elem in line.split():
                attrs=elem.split(":")
                if attrs[0] == "x":
                    mouseX=int(attrs[1])
                elif attrs[0] == "y":
                    mouseY=int(attrs[1])

        return [mouseX, mouseY]

    def set_coords(self, x, y):
        os.system("xdotool mousemove {} {}".format(x, y))

    def click(self, btn_num):
        os.system("xdotool click --clearmodifiers {}".format(btn_num))

    def left_click(self):
        self.click(1)

    def middle_click(self):
        self.click(2)

    def right_click(self):
        self.click(3)

    def scrollup(self):
        self.click(4)

    def scrolldown(self):
        self.click(5)

    def double_click(self):
        self.click(1)
        time.sleep(.1)
        self.click(1)

    def triple_click(self):
        self.click(1)
        time.sleep(.1)
        self.click(1)
        time.sleep(.1)
        self.click(1)
