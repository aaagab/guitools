#!/usr/bin/env python3
from pprint import pprint
import os
import shlex
import subprocess
import sys

from .regular_window import Regular_windows
from .window import Window
from .windows import Windows
from ..gpkgs import message as msg

from ..gpkgs.timeout import TimeOut


class Window_open(object):
    def __init__(self, obj_monitors=None):
        self.window=None
        self._obj_monitors=obj_monitors
        self._verified_hex_ids=[]
        self._command=None

    def execute(self, cmd):
        self.window=None
        self._command=cmd
        self.regular_windows=Regular_windows()
        if isinstance(cmd, str):
            cmd=shlex.split(cmd)
        proc=subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return self

    def focus_desktop(self):
        self.desktop_hex_id=None
        for hex_id in self.regular_windows.desktop_hex_ids:
            Regular_windows.focus(hex_id)
            if Windows.get_active_hex_id() == hex_id:
                self.desktop_hex_id=hex_id
                break

        if self.desktop_hex_id is None:
            msg.error("For window_open focusing desktop failed", exit=1)

    def has_window(self, _class=None):
        self.focus_desktop()
        timer=TimeOut(3).start()
        previous_active_hex_id=None
        active_hex_id=Windows.get_active_hex_id()
        while True:
            active_hex_id=Windows.get_active_hex_id()

            if active_hex_id == self.desktop_hex_id:
                tmp_existing_hex_ids=Regular_windows().windows_hex_ids
                diff_set=(set(tmp_existing_hex_ids) - set(self.regular_windows.windows_hex_ids))
                if diff_set:
                    for hex_id in diff_set:
                        if self.confirm_window(_class, hex_id) is True:
                            return True
            else:
                if self.confirm_window(_class, active_hex_id) is True:
                    return True
                else:
                    Regular_windows.focus(self.desktop_hex_id)

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
                self.window=None
                return False
