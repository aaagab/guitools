#!/usr/bin/env python3
from pprint import pprint
import os
import re
import sys

from .xlibhelpers import WindowType, XlibHelpers

from Xlib.display import Display
from Xlib.xobject.drawable import Window
from Xlib.X import AnyPropertyType

class Taskbar(object):
    def __init__(self) -> None:
        self.x:int=0
        self.y:int=0
        self.width:int=0
        self.height:int=0

class Taskbars(object):
    def __init__(self,
        display:Display|None=None, 
        root:Window|None=None,
    ):
        self._xlib=XlibHelpers(display=display, root=root)
        self.display=self._xlib.display
        self.root=self._xlib.root

        _NET_WM_STRUT = self.display.get_atom('_NET_WM_STRUT')

        self.taskbars=[]
        prop = self.root.get_full_property(self.display.get_atom('_NET_CLIENT_LIST'), property_type=AnyPropertyType)
        if prop is None:
            raise NotImplementedError()

        for window_id in prop.value:
            xwin = self.display.create_resource_object('window', window_id)
            prop = xwin.get_full_property(self.display.get_atom("_NET_WM_WINDOW_TYPE"), property_type=AnyPropertyType)
            if prop is not None:
                if WindowType.DOCK.value in list(prop.value):
                    geometry=self._xlib.get_geometry(xwin, show_frame=False)
                    taskbar=Taskbar()
                    taskbar.x=geometry.x
                    taskbar.y=geometry.y
                    taskbar.width=geometry.width
                    taskbar.height=geometry.height
                    self.taskbars.append(taskbar)
