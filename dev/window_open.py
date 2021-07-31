#!/usr/bin/env python3
from pprint import pprint
import os
import shlex
import subprocess
import sys

from .regular_window import Regular_windows
from .window import Window

from ..gpkgs.timeout import TimeOut
    
class Window_open(object):
    def __init__(self, cmd):
        self.is_existing_window=""
        self.window=""
        self.existing_hex_ids=[]
        self.execute(cmd)
        self.existing_windows=[]

    def execute(self, cmd):
        self.is_existing_window=False
        self.window=""
        self.existing_windows_obj=Regular_windows()
        self.existing_hex_ids=[win["hex_id"] for win in self.existing_windows_obj.windows]
        self.desktop_hex_ids=[hex_id for hex_id in self.existing_windows_obj.desktop_hex_ids]
        
        subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.has_window()
        return self

    def has_window(self, active_hex_id=None):
        if self.window:
            return True

        desktop_hex_id=Windows.show_desktop()

        timer=TimeOut(3).start()
        hex_id=""
        while not hex_id:
            tmp_existing_windows=Regular_windows().windows
            tmp_existing_hex_ids=[win["hex_id"] for win in tmp_existing_windows]
            hex_id=(set(tmp_existing_hex_ids) - set(self.existing_hex_ids))
            if hex_id:
                break

            if active_hex_id is None:
                active_hex_id=Windows.get_active_hex_id()
                
            if active_hex_id != desktop_hex_id:
                if active_hex_id in self.existing_hex_ids:
                    self.is_existing_window=True
                hex_id=active_hex_id
                break

            if timer.has_ended(pause=.3):
                return False

        if isinstance(hex_id, set):
            hex_id=list(hex_id)[0]

        self.window=Window(hex_id)
        self.existing_hex_ids=[]

        return True
