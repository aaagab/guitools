#!/usr/bin/env python3
from pprint import pprint
import os
import shlex
import subprocess
import sys

from .regular_window import Regular_windows
from .window import Window
from .windows import Windows

from ..gpkgs.timeout import TimeOut


class Window_open(object):
    def __init__(self, obj_monitors=None):
        self.window=None
        self.existing_hex_ids=[]
        self.obj_monitors=obj_monitors

    def execute(self, cmd):
        self.window=None
        self.existing_hex_ids=[win["hex_id"] for win in Regular_windows().windows]
        proc=subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return self

    def has_window(self, _class=None):
        if self.window is not None:
            return True

        timer=TimeOut(3).start()
        while True:
            tmp_existing_windows=Regular_windows().windows
            tmp_existing_hex_ids=[win["hex_id"] for win in tmp_existing_windows]
            diff_set=(set(tmp_existing_hex_ids) - set(self.existing_hex_ids))

            if diff_set:
                for hex_id in diff_set:
                    tmp_window=Window(hex_id=hex_id, obj_monitors=self.obj_monitors)
                    if _class is None:
                        self.window=tmp_window
                        return True
                    else:
                        if _class == tmp_window._class:
                            self.window=tmp_window
                            return True
                        else:
                            self.existing_hex_ids.append(hex_id)
                            tmp_window=None

            if timer.has_ended(pause=.3):
                self.window=None
                return False
