#!/usr/bin/env python3
from pprint import pprint
import os
import sys
import threading
from enum import Enum
import time
from typing import cast

from Xlib.xobject.drawable import Window as XlibWindow
from Xlib.X import AnyPropertyType
from Xlib.protocol.event import ClientMessage
from Xlib import X, Xutil, error
from Xlib.display import Display
from Xlib.Xatom import STRING

from .xlibhelpers import WindowType, XlibHelpers, WindowState, WindowStateAction, Atom, WindowViewState
from .helpers import ExeInfo, cmd_filter_bad_window
from .keyboards import Keyboard
from .mouses import Mouse
from .monitors import Monitors
from .monitor import Tile, Monitor

from ..gpkgs.timeout import TimeOut
from ..gpkgs.timeit import TimeIt

class TileMove(str, Enum):
    MAXIMIZE=0
    LEFT=1
    RIGHT=2

class Gravity(Enum):
    __order__ = "DEFAULT NORTH_WEST NORTH NORTH_EAST WEST CENTER EAST SOUTH_WEST SOUTH SOUTH_EAST STATIC"
    DEFAULT=0
    NORTH_WEST=1
    NORTH=2
    NORTH_EAST=3
    WEST=4
    CENTER=5
    EAST=6
    SOUTH_WEST=7
    SOUTH=8
    SOUTH_EAST=9
    STATIC=10

class Notify(XlibHelpers):
    """
        Notify class is not for production, it is just to show how to use the xlib next_event
        if start_thread is True then at least one regular event_mask must be added (i.e. X.PropertyChangeMask) so the thread is not stuck at next_event()
    """
    def __init__(self,
        display:Display|None=None, 
        root:XlibWindow|None=None,
        start_thread=True,
    )-> None:
        self._xlib=XlibHelpers(display=display, root=root)
        self.display=self._xlib.display
        self.root=self._xlib.root
        self.state=dict(run=True)
        self.thread=threading.Thread(target=self.catch_events, args=())
        self.start_thread=start_thread
        
    def catch_events(self):
        # self.root.change_attributes(event_mask=X.PropertyChangeMask | X.SubstructureNotifyMask | X.StructureNotifyMask) 
        # self.root.change_attributes(event_mask=X.KeyPressMask | X.KeyReleaseMask | X.UnmapNotify | X.MapNotify)
        # self.root.change_attributes(event_mask=X.PropertyChangeMask | X.SubstructureNotifyMask)
        self.root.change_attributes(event_mask=X.PropertyChangeMask | X.SubstructureNotifyMask)

        while self.state["run"] is True:
            event = self.display.next_event()
            if event.type != X.PropertyNotify:
                print(" ->", event)
            if event.type == X.ClientMessage:
                print(" -> ClientMessage {} {}".format(
                    self.display.get_atom_name(event.type),
                    self.display.get_atom_name(event.client_type),
                ))
            elif event.type == X.ConfigureNotify:
                print(" -> ConfigureNotify {}".format(
                    self.display.get_atom_name(event.type),
                ))
            elif event.type == X.CreateNotify:
                print(" -> CreateNotify {}".format(
                    self.display.get_atom_name(event.type),
                ))
                self.state["window"]=event.window
            elif event.type == X.PropertyNotify:
                print(" -> PropertyNotify {} {}".format(
                    self.display.get_atom_name(event.type),
                    self.display.get_atom_name(event.atom),
                ))
            elif event.type == X.DestroyNotify:
                print(" -> DestroyNotify {}".format(
                    self.display.get_atom_name(event.type),
                ))

    def __enter__(self):
        if self.start_thread is True:
            self.thread.start()
        return self
    
    def __exit__(self ,type, value, traceback):
        self.state["run"]=False
        if self.start_thread is True:
            self.thread.join()

class Window():
    def __init__(
        self, 
        xwin:XlibWindow, 
        display:Display|None=None, 
        root:XlibWindow|None=None,
        obj_monitors:Monitors|None=None
    )-> None:
        
        self._xlib=XlibHelpers(display=display, root=root)
        self.display=self._xlib.display
        self.root=self._xlib.root

        self.xwin=xwin
        self.ptr=Mouse()
        self.kbd=Keyboard()
        self.obj_monitors:Monitors|None=obj_monitors
        if self.obj_monitors is None:
            self.obj_monitors=Monitors(display=self.display, root=self.root)
        self.dec_id:int=xwin.id
        self.hex_id:str=hex(xwin.id)
        self.pid:int|None=None
        self.types:list[WindowType]=[]

        self.x:int=0
        self.y:int=0
        self.width:int=0
        self.height:int=0
        
        self.class_name:str|None=None
        self.class_name_short:str|None=None
        self.name:str|None=None
        self.border_left:int=0
        self.border_right:int=0
        self.border_bottom:int=0
        self.border_top:int=0
        self.frame_width:int=0
        self.frame_height:int=0
        self.frame_x:int=0
        self.frame_y:int=0
        self.exe_info:ExeInfo|None=None
        self.monitor:Monitor|None=None
        self.min_width:int=0
        self.min_height:int=0

        self.is_taskbar:bool=False
        self.is_desktop:bool=False
        self.is_regular:bool=False
        self.is_mapped:bool=True


        self.update_fields()

    def set_exe_info(self, command:str|list[str]|None=None):
        if self.pid is None:
            raise Exception("Window pid is None")
        self.exe_info=ExeInfo(self.pid, command=command)

    def update_fields(self, monitor:Monitor|None=None):
        self.types=[]

        prop=self.xwin.get_full_property(self.display.get_atom("_NET_WM_PID"), property_type=AnyPropertyType)
        if prop is not None:
            self.pid=prop.value[0]

        self.update_geometry()

        class_name=self.xwin.get_wm_class()
        if class_name is not None:
            self.class_name=".".join(class_name)
            self.class_name_short=class_name[0]

        prop = self.xwin.get_full_property(self.display.get_atom("_NET_WM_NAME"), property_type=AnyPropertyType)
        if prop is not None:
            self.name=prop.value.decode()

        prop = self.xwin.get_full_property(self.display.get_atom("_NET_FRAME_EXTENTS"), property_type=AnyPropertyType)
        if prop is not None:
            self.border_left, self.border_right, self.border_top, self.border_bottom = prop.value
            # print("BORDERS:", self.border_left, self.border_right, self.border_top, self.border_bottom)

        self.frame_width=self.width+self.border_left+self.border_right
        self.frame_height=self.height+self.border_top+self.border_bottom
        self.frame_x=self.x-self.border_left
        self.frame_y=self.y-self.border_top

        prop = self.xwin.get_full_property(self.display.get_atom("_NET_WM_WINDOW_TYPE"), property_type=AnyPropertyType)
        if prop is not None:
            values=list(prop.value)
            if WindowType.DESKTOP.value in values:
                self.is_desktop=True
            if WindowType.DOCK.value in values:
                self.is_taskbar=True
        self.is_regular=self.is_desktop is False and self.is_taskbar is False

        # Mouse and kdb setup
        self.ptr.rx=self.x
        self.ptr.ry=self.y
        self.ptr.win_dec_id=self.dec_id
        self.kbd.win_dec_id=self.dec_id

        if monitor is None:
            if self.obj_monitors is None:
                self.obj_monitors=Monitors(display=self.display, root=self.root)
            self.monitor=self.obj_monitors.get_monitor_from_coords(
                self.frame_x,
                self.frame_y,
                self.frame_width,
                self.frame_height,
            )
            if self.monitor is None:
                self.monitor=self.obj_monitors.monitors[0]
        else:
            self.monitor=monitor

        hints=self.xwin.get_wm_normal_hints()
        if hints is not None:
            self.min_width=hints.min_width
            self.min_height=hints.min_height

        return self

    def print(self):
        pprint(vars(self))
        return self

    def get_center_coords(self, monitor:Monitor|None=None):
        if monitor is None:
            if self.obj_monitors is None:
                self.obj_monitors=Monitors(display=self.display, root=self.root)
            monitor=self.obj_monitors.get_active_monitor()

        mid_width=int(monitor.width/2)
        mid_height=int(monitor.height/2)
        center_x=monitor.range_x[0]+mid_width
        center_y=monitor.range_y[0]+mid_height

        mid_window_width=int((self.width+self.border_left+self.border_right)/2)
        mid_window_height=int((self.height+self.border_top+self.border_bottom)/2)

        x=center_x-mid_window_width
        y=center_y-mid_window_height
        
        return [x, y]

    def exists(self):
        return self._xlib.window_exists(self.hex_id)
        
    def update_geometry(self):
        geometry=self._xlib.get_geometry(self.xwin, show_frame=False)
        if ((geometry.x == 0 and geometry.y == 0 and geometry.width is None and geometry.height is None) or 
                (geometry.x == 0 and geometry.y == 0 and geometry.width == 1 and geometry.height == 1)):
            pass
        else:
            self.x=geometry.x
            self.y=geometry.y
            self.width=geometry.width
            self.height=geometry.height

    def set_geometry(self, x:int|None=None, y:int|None=None, width:int|None=None, height:int|None=None, gravity:Gravity=Gravity.DEFAULT):
        show_info=False
        if show_info is True:
            print(f"\nREQUESTED: x:{x} y:{y} w:{width} h:{height} g:{gravity}")
            print(f"MINIMUM: w:{self.min_height} h:{self.min_width}")

        self.update_geometry()

        requested_width=width
        if requested_width is not None and requested_width < self.min_width:
            requested_width=self.min_width
        requested_height=height
        if requested_height is not None and requested_height < self.min_height:
            requested_height=self.min_height
        requested_x=x
        requested_y=y

        gravity_flags=gravity.value

        if x is None:
            x=self.x
        x = x + self.border_left
        
        if y is None:
            y=self.y
        y = y +self.border_top

        if width is None:
            width = self.width
        width = width - self.border_left -self.border_right

        if height is None:
            height = self.height
        height = height - self.border_top - self.border_bottom

        gravity_flags |= (1 << 8)
        gravity_flags |= (1 << 9)
        gravity_flags |= (1 << 10)
        gravity_flags |= (1 << 11)

        if show_info is True:
            print(f"CALCULATED: x:{x} y:{y} w:{width} h:{height}")

        if self._xlib.has_wm_state(state=WindowState.HIDDEN, xwin=self.xwin):
            self.focus(wait_ms=1000)

        if self.xwin.get_wm_state() is None:
            self.map()
        self.set_fullscreen(action=WindowStateAction.REMOVE, wait_ms=2000)
        self._xlib.set_wm_state(action=WindowStateAction.REMOVE, state=WindowState.HIDDEN, xwin=self.xwin, wait_ms=2000)
        self._xlib.set_wm_state(action=WindowStateAction.REMOVE, state=WindowState.MAXIMIZED_VERT, xwin=self.xwin, extra_state=WindowState.MAXIMIZED_HORZ, wait_ms=2000)

        self._xlib.set_prop("_NET_MOVERESIZE_WINDOW", [gravity_flags, x, y, width, height], self.xwin)
       
        if show_info is True:
            self._xlib.get_geometry(self.xwin, show_frame=False)

        timeout=TimeOut(1).start()
        matched=False
        while timeout.has_ended(pause=.001) is False:
            self.update_geometry()
            if ((requested_width is not None and requested_width != self.width) or
                (requested_height is not None and requested_height != self.height) or
                (requested_x is not None and requested_x != self.x) or
                (requested_y is not None and requested_y != self.y)):
                    continue
            matched=True
            break
        
        if show_info is True:
            if matched is False:
                print(f"NOT MATCHED: x:{requested_x} y:{requested_y} w:{requested_width} h:{requested_height}")
            print(f"RETRIEVED: x:{self.x} y:{self.y} w:{self.width} h:{self.height}")

        return self

    def move(self, x:int, y:int):
        self.set_geometry(x=x, y=y)
        return self

    def resize(self, width:int, height:int):
        self.set_geometry(width=width, height=height)
        return self

    def tile(self, move:TileMove, monitor_index:int|None=None):
        if self.obj_monitors is None:
            self.obj_monitors=Monitors(display=self.display, root=self.root)
        if monitor_index is None:
            monitor_index=0
        else:
            if monitor_index in range(0, len(self.obj_monitors.monitors)):
                monitor_index=monitor_index
            else:
                monitor_index=0

        monitor:Monitor=self.obj_monitors.monitors[monitor_index]

        if move == TileMove.MAXIMIZE:
            self.move(monitor.x, monitor.y)
            self.maximize()
        else:        
            tiles:list[Tile]=monitor.get_tiles(xdivs=2, ydivs=1, cover_taskbar=False)
            selected_tile:Tile
            if move == TileMove.LEFT:
                selected_tile=tiles[0]
            elif move == TileMove.RIGHT:
                selected_tile=tiles[-1]
            else:
                raise NotImplementedError()
            self.set_geometry(
                x=selected_tile.x, 
                y=selected_tile.y, 
                width=selected_tile.width, 
                height=selected_tile.height
            )

    def focus(self, wait_ms:int|None=None):
        current_dec_id=self._xlib.get_active_window_dec_id()
        if current_dec_id is None:
            current_dec_id=0
        self._xlib.set_prop(Atom.ACTIVE_WINDOW, [0, X.CurrentTime, current_dec_id], self.xwin)
        if wait_ms is not None:
            self._xlib.wait_for_state(wait_ms=wait_ms, state=Atom.WM_STATE_FOCUSED, need_state=True, xwin=self.xwin)
            self._xlib.set_wm_state(action=WindowStateAction.REMOVE, state=WindowState.HIDDEN, xwin=self.xwin, wait_ms=wait_ms)
        return self

    def set_above(self, wait_ms:int|None=None):
        self._xlib.set_wm_state(action=WindowStateAction.ADD, state=WindowState.ABOVE, xwin=self.xwin, wait_ms=wait_ms)
        return self
    
    def unset_above(self, wait_ms:int|None=None):
        self._xlib.set_wm_state(action=WindowStateAction.REMOVE, state=WindowState.ABOVE, xwin=self.xwin, wait_ms=wait_ms)
        return self

    def set_sticky(self, wait_ms:int|None=None):
        self._xlib.set_wm_state(action=WindowStateAction.ADD, state=WindowState.STICKY, xwin=self.xwin, wait_ms=wait_ms)
        return self
    
    def unset_sticky(self, wait_ms:int|None=None):
        self._xlib.set_wm_state(action=WindowStateAction.REMOVE, state=WindowState.STICKY, xwin=self.xwin, wait_ms=wait_ms)
        return self

    def map(self):
        self.xwin.map()
        timeout=TimeOut(2).start()
        while True:
            if self.xwin.get_wm_state() is not None: # get_wm_state() is needed to make window visible on KDE
                break
            if timeout.has_ended(.001) is True:
                raise NotImplementedError
        self.update_geometry()
        self.move(x=self.x, y=self.y)
        self.is_mapped=True
        return self

    def unmap(self):
        self.update_geometry()
        self.xwin.unmap()
        timeout=TimeOut(2).start()
        while True:
            if self.xwin.get_wm_state() is None: # get_wm_state() is needed to make window invisible on KDE
                break
            if timeout.has_ended(.001) is True:
                raise NotImplementedError
        self.is_mapped=False
        return self

    def set_below(self, wait_ms:int|None=None):
        self._xlib.set_wm_state(action=WindowStateAction.ADD, state=WindowState.BELOW, xwin=self.xwin, wait_ms=wait_ms)
        return self
    
    def unset_below(self, wait_ms:int|None=None):
        self._xlib.set_wm_state(action=WindowStateAction.REMOVE, state=WindowState.BELOW, xwin=self.xwin, wait_ms=wait_ms)
        return self

    def set_fullscreen(self, action:WindowStateAction=WindowStateAction.ADD, wait_ms:int|None=None):
        self._xlib.set_wm_state(action=action, state=WindowState.FULLSCREEN, xwin=self.xwin, wait_ms=wait_ms)
        return self

    def minimize(self, wait_ms:int|None=None):
        self._xlib.set_window_view_state(xwin=self.xwin, view_state=WindowViewState.IconicState, wait_ms=wait_ms)
        return self

    def maximize(self,
        action:WindowStateAction=WindowStateAction.ADD, 
        wait_ms:int|None=None
    ):
        if self._xlib.has_wm_state(state=WindowState.HIDDEN, xwin=self.xwin):
            self.focus(wait_ms=1000)
        self._xlib.set_wm_state(action=action, state=WindowState.MAXIMIZED_VERT, xwin=self.xwin, extra_state=WindowState.MAXIMIZED_HORZ, wait_ms=wait_ms)
        return self

    def center(self, monitor:Monitor|None=None):
        x, y =self.get_center_coords(monitor=monitor)
        self.move(x, y)
        return self

    def close(self):
        self._xlib.set_prop("_NET_CLOSE_WINDOW", [int(time.mktime(time.localtime())), 1], self.xwin)
        return self
    
    def get_name(self):
        prop = self.xwin.get_full_property(self.display.get_atom("_NET_WM_NAME"), property_type=AnyPropertyType)
        if prop is not None:
            self.name=prop.value.decode()
            return self.name
        else:
            return None

    def set_name(self, name:str):
        # both properties are needed on KDE
        self._xlib.set_prop("WM_NAME", name, self.xwin)
        self._xlib.set_prop("_NET_WM_NAME", name, self.xwin)
        self.name=name
        return self
