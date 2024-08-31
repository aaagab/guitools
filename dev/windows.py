#!/usr/bin/env python3
from pprint import pprint
import os
import sys


from typing import cast
from .helpers import bubble_sort_array
from .helpers import ExeInfo
from .window import Window
from .monitors import Monitors

from Xlib.display import Display
from Xlib.X import AnyPropertyType
from Xlib.xobject.drawable import Window as XlibWindow

from .xlibhelpers import XlibHelpers

class Windows():
    def __init__(self, display:Display|None=None, root:XlibWindow|None=None, obj_monitors:Monitors|None=None) -> None:
        
        self._xlib=XlibHelpers(display=display, root=root)
        self.display=self._xlib.display
        self.root=self._xlib.root

        self.windows:list[Window]=[]
        self.regular_windows:list[Window]=[]
        self._desktop_windows:list[Window]=[]
        self.taskbars:list[Window]=[]
        self.obj_monitors=obj_monitors
        self.set_windows()

    @staticmethod
    def get_window(hex_id:str, obj_monitors:Monitors|None=None):
        _xlib=XlibHelpers()
        xwin=_xlib.get_window_from_hex_id(hex_id=hex_id)
        if xwin is None:
            return None
        else:
            return Window(xwin=xwin, display=_xlib.display, root=_xlib.root, obj_monitors=obj_monitors)

    @staticmethod
    def get_active_window(obj_monitors:Monitors|None=None):
        _xlib=XlibHelpers()
        xwin=_xlib.get_active_xwindow()
        if xwin is None:
            return None
        else:
            return Window(xwin=xwin, display=_xlib.display, root=_xlib.root, obj_monitors=obj_monitors)
        
    @staticmethod
    def select_window():
        _xlib=XlibHelpers()
        return Window(display=_xlib.display, root=_xlib.root, xwin=_xlib.select())

    def set_windows(self):
        self.windows=[]
        self.regular_windows=[]
        self._desktop_windows=[]
        self.taskbars=[]

        prop = self.root.get_full_property(self.display.get_atom("_NET_CLIENT_LIST"), property_type=AnyPropertyType)
        if prop is None:
            raise NotImplementedError()
        for window_id in prop.value:
            xwin = self.display.create_resource_object('window', window_id)
            window=Window(xwin, display=self.display, root=self.root, obj_monitors=self.obj_monitors)
            self.windows.append(window)
            if window.is_desktop:
                self._desktop_windows.append(window)
            if window.is_taskbar:
                self.taskbars.append(window)
            if window.is_regular:
                self.regular_windows.append(window)
        return self

    @staticmethod
    def sorted_by_class(windows:list[Window]):
        classes=[]
        for window in windows:
            if window.class_name is None:
                classes.append("")
            else:
                classes.append(window.class_name.lower())

        classes=sorted(set(classes))

        tmp_windows=[]
        for class_name in classes:
            tmp_names=[]
            tmp_indexes=[]
            for w, window in enumerate(windows):
                window_class_name=""
                if window.class_name is not None:
                    window_class_name=window.class_name.lower()
                if window_class_name == class_name:
                    tmp_indexes.append(w)
                    window_name=""
                    if window.name is not None:
                        window_name=window.name.lower()
                    tmp_names.append(window_name)

            for index in bubble_sort_array(tmp_names, len(tmp_names)):
                tmp_windows.append(windows[tmp_indexes[index]])

        return tmp_windows
    
    @staticmethod
    def sorted_by_exe_names(windows:list[Window]):
        exe_names=[]
        for window in windows:
            if window.exe_info is None:
                window_pid=0
                if window.pid is not None:
                    window_pid=window.pid
                window.exe_info=ExeInfo(window_pid)
            exe_names.append(window.exe_info.exe_name.lower())

        exe_names=sorted(set(exe_names))
        tmp_windows=[]
        for exe_name in exe_names:
            tmp_names=[]
            tmp_indexes=[]
            for w, window in enumerate(windows):
                if cast(ExeInfo, window.exe_info).exe_name.lower() == exe_name:
                    tmp_indexes.append(w)
                    window_name=""
                    if window.name is not None:
                        window_name=window.name.lower()
                    tmp_names.append(window_name)

            for index in bubble_sort_array(tmp_names, len(tmp_names)):
                tmp_windows.append(windows[tmp_indexes[index]])

        return tmp_windows
