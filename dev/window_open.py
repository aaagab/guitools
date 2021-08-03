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
        self._obj_monitors=obj_monitors
        self._verified_hex_ids=[]
        self._shared=False
        self._command=None

    def execute(self, cmd, shared=False):
        self.window=None
        self._shared=shared
        self._command=cmd
        if self._shared is True:
            self._verified_hex_ids=[]
        else:
            self._verified_hex_ids=[win["hex_id"] for win in Regular_windows().windows]
        proc=subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return self

    def has_window(self, _class=None):
        if self.window is not None:
            return True

        desktop_hex_id=None

        timer=TimeOut(3).start()
        while True:
            if self._shared is True:
                active_hex_id=Windows.get_active_hex_id()
                
                if active_hex_id not in self._verified_hex_ids:
                    if active_hex_id != desktop_hex_id:
                        if self.confirm_window(_class, active_hex_id) is True:
                            return True
            else:
                tmp_existing_windows=Regular_windows().windows
                tmp_existing_hex_ids=[win["hex_id"] for win in tmp_existing_windows]
                diff_set=(set(tmp_existing_hex_ids) - set(self._verified_hex_ids))

                if diff_set:
                    for hex_id in diff_set:
                        if self.confirm_window(_class, hex_id) is True:
                            return True

            if timer.has_ended(pause=.3):
                self.window=None
                return False

    def confirm_window(self, _class, hex_id):
        tmp_window=Window(hex_id=hex_id, obj_monitors=self._obj_monitors, command=self._command)
        if _class is None:
            self.window=tmp_window
            return True
        else:
            if _class == tmp_window._class:
                self.window=tmp_window
                return True
            else:
                self._verified_hex_ids.append(hex_id)
                tmp_window=None
                return False
