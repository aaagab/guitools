#!/usr/bin/env python3
from pprint import pprint
import os
import shlex
import subprocess
import sys

from Xlib.xobject.drawable import Window as XlibWindow
from Xlib.X import AnyPropertyType
from Xlib.display import Display

from .monitors import Monitors
from .xlibhelpers import XlibHelpers, WindowType
from .window import Window
from .windows import Windows

from ..gpkgs.timeout import TimeOut


class WindowOpen():
    def __init__(self, 
        display:Display|None=None, 
        root:XlibWindow|None=None,
        obj_monitors:Monitors|None=None
    )-> None:
        self._xlib=XlibHelpers(display=display, root=root)
        self.display=self._xlib.display
        self.root=self._xlib.root
        self.window:Window|None=None
        self._obj_monitors=obj_monitors
        self._verified_hex_ids:list[str]=[]
        self._command:str|list[str]|None=None
        self.regular_hex_ids:list[str]=[]
        self._desktop_hex_ids:list[str]=[]

    def get_window_hex_ids(self)-> dict[str, list[str]]:
        regular_hex_ids:list[str]=[]
        desktop_hex_ids:list[str]=[]
        prop = self.root.get_full_property(self.display.get_atom("_NET_CLIENT_LIST_STACKING"), property_type=AnyPropertyType)
        if prop is None:
            raise NotImplementedError()
        
        for window_id in prop.value:
            xwin = self.display.create_resource_object('window', window_id)
            prop = xwin.get_full_property(self.display.get_atom("_NET_WM_WINDOW_TYPE"), property_type=AnyPropertyType)
            is_desktop=False
            is_taskbar=False
            if prop is not None:
                values=list(prop.value)
                if WindowType.DESKTOP.value in values:
                    is_desktop=True
                    desktop_hex_ids.append(hex(window_id))
                if WindowType.DOCK.value in values:
                    is_taskbar=True
            is_regular=is_desktop is False and is_taskbar is False
            if is_regular is True:
                regular_hex_ids.append(hex(window_id))
        return dict(
                desktop_hex_ids=desktop_hex_ids,
                regular_hex_ids=regular_hex_ids,
            )

    def execute(self, cmd:str|list[str]):
        self.window=None
        self._command=cmd
        
        dy_hex_ids=self.get_window_hex_ids()
        self._desktop_hex_ids=dy_hex_ids["desktop_hex_ids"]
        self.regular_hex_ids=dy_hex_ids["regular_hex_ids"]

        if isinstance(cmd, str):
            cmd=shlex.split(cmd)
        self.proc=subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return self

    def focus_desktop(self):
        self._desktop_hex_id=None
        timer=TimeOut(3).start()
        while True:
            found=False
            for hex_id in self._desktop_hex_ids:
                self._xlib.focus_window(hex_id)
                if self._xlib.get_active_window_hex_id() == hex_id:
                    self._desktop_hex_id=hex_id
                    found=True
                    break
            if timer.has_ended(pause=.3):
                break
            elif found is True:
                break
        if self._desktop_hex_id is None:
            raise Exception("For window_open focusing desktop failed")

    def has_window(self, class_name:str|None=None):
        self.focus_desktop()
        timer=TimeOut(3).start()
        while True:
            active_hex_id=self._xlib.get_active_window_hex_id()
            if active_hex_id == self._desktop_hex_id:
                tmp_existing_hex_ids=self.get_window_hex_ids()["regular_hex_ids"]

                diff_set=(set(tmp_existing_hex_ids) - set(self.regular_hex_ids))
                if diff_set:
                    for hex_id in diff_set:
                        if self.confirm_window(hex_id, class_name) is True:
                            return True
            else:
                if self.confirm_window(active_hex_id, class_name) is True:
                    return True
                else:
                    self._xlib.focus_window(self._desktop_hex_id)

            if timer.has_ended(pause=.3):
                self.window=None
                return False

    def confirm_window(self, hex_id:str, class_name:str|None):
        xwin=self._xlib.get_window_from_hex_id(hex_id=hex_id)
        if xwin is None:
            raise Exception(f"Couldn't get xlib window from {hex_id}.")
        tmp_window=Window(display=self.display, xwin=xwin,obj_monitors=self._obj_monitors)
        tmp_window.set_exe_info(command=self._command)

        if class_name is None:
            self.window=tmp_window
            return True
        else:
            if class_name == tmp_window.class_name:
                self.window=tmp_window
                return True
            else:
                self._verified_hex_ids.append(hex_id)
                self.window=None
                return False
