#!/usr/bin/env python3
import os
import re
import sys
from array import array
from enum import Enum
from Xlib.xobject.drawable import Window
from Xlib.display import Display
from Xlib.protocol.request import GetGeometry
from Xlib.protocol.event import ClientMessage
from Xlib.Xatom import STRING
from Xlib.X import AnyPropertyType
from Xlib import X
from typing import cast
import time

from .helpers import hex_to_int, cmd_filter_bad_window
from ..gpkgs.timeout import TimeOut

class WindowType(Enum):
    __order__ = "COMBO DESKTOP DIALOG DND DOCK DROPDOWN_MENU MENU NORMAL NOTIFICATION POPUP_MENU SPLASH TOOLBAR UTILITY"
    # __order__ = "DIALOG DESKTOP DOCK TOOLBAR MENU NORMAL UTILITY SPLASH"
    COMBO=407
    DESKTOP=396
    DIALOG=402
    DND=408
    DOCK=397
    DROPDOWN_MENU=403
    MENU=399
    NORMAL=409
    NOTIFICATION=406
    POPUP_MENU=404
    SPLASH=401
    TOOLBAR=398
    UTILITY=400

class WindowViewState(Enum):
    WithdrawnState = 0
    NormalState = 1
    IconicState = 3

class WindowStateAction(Enum):
    REMOVE=0
    ADD=1
    TOGGLE=2

class WindowState(str, Enum):
    MODAL="_NET_WM_STATE_MODAL"
    STICKY="_NET_WM_STATE_STICKY"
    MAXIMIZED_VERT="_NET_WM_STATE_MAXIMIZED_VERT"
    MAXIMIZED_HORZ="_NET_WM_STATE_MAXIMIZED_HORZ"
    SHADED="_NET_WM_STATE_SHADED"
    SKIP_TASKBAR="_NET_WM_STATE_SKIP_TASKBAR"
    SKIP_PAGER="_NET_WM_STATE_SKIP_PAGER"
    HIDDEN="_NET_WM_STATE_HIDDEN"
    FULLSCREEN="_NET_WM_STATE_FULLSCREEN"
    ABOVE="_NET_WM_STATE_ABOVE"
    BELOW="_NET_WM_STATE_BELOW"
    DEMANDS_ATTENTION="_NET_WM_STATE_DEMANDS_ATTENTION"

class Atom(str, Enum):
    ACTIVE_WINDOW="_NET_ACTIVE_WINDOW"
    CLIENT_LIST="_NET_CLIENT_LIST"
    CLIENT_LIST_STACKING="_NET_CLIENT_LIST_STACKING"
    CLOSE_WINDOW="_NET_CLOSE_WINDOW"
    CURRENT_DESKTOP="_NET_CURRENT_DESKTOP"
    DESKTOP_GEOMETRY="_NET_DESKTOP_GEOMETRY"
    DESKTOP_VIEWPORT="_NET_DESKTOP_VIEWPORT"
    MOVERESIZE_WINDOW="_NET_MOVERESIZE_WINDOW"
    NUMBER_OF_DESKTOPS="_NET_NUMBER_OF_DESKTOPS"
    SHOWING_DESKTOP="_NET_SHOWING_DESKTOP"
    WM_ACTION_ABOVE="_NET_WM_ACTION_ABOVE"
    WM_ACTION_BELOW="_NET_WM_ACTION_BELOW"
    WM_ACTION_CHANGE_DESKTOP="_NET_WM_ACTION_CHANGE_DESKTOP"
    WM_ACTION_CLOSE="_NET_WM_ACTION_CLOSE"
    WM_ACTION_FULLSCREEN="_NET_WM_ACTION_FULLSCREEN"
    WM_ACTION_MAXIMIZE_HORZ="_NET_WM_ACTION_MAXIMIZE_HORZ"
    WM_ACTION_MAXIMIZE_VERT="_NET_WM_ACTION_MAXIMIZE_VERT"
    WM_ACTION_MINIMIZE="_NET_WM_ACTION_MINIMIZE"
    WM_ACTION_MOVE="_NET_WM_ACTION_MOVE"
    WM_ACTION_RESIZE="_NET_WM_ACTION_RESIZE"
    WM_ACTION_SHADE="_NET_WM_ACTION_SHADE"
    WM_ACTION_STICK="_NET_WM_ACTION_STICK"
    WM_ALLOWED_ACTIONS="_NET_WM_ALLOWED_ACTIONS"
    WM_DESKTOP="_NET_WM_DESKTOP"
    WM_NAME="_NET_WM_NAME"
    WM_PID="_NET_WM_PID"
    WM_STATE="_NET_WM_STATE"
    WM_STATE_ABOVE="_NET_WM_STATE_ABOVE"
    WM_STATE_BELOW="_NET_WM_STATE_BELOW"
    WM_STATE_DEMANDS_ATTENTION="_NET_WM_STATE_DEMANDS_ATTENTION"
    WM_STATE_FOCUSED="_NET_WM_STATE_FOCUSED"
    WM_STATE_FULLSCREEN="_NET_WM_STATE_FULLSCREEN"
    WM_STATE_HIDDEN="_NET_WM_STATE_HIDDEN"
    WM_STATE_MAXIMIZED_HORZ="_NET_WM_STATE_MAXIMIZED_HORZ"
    WM_STATE_MAXIMIZED_VERT="_NET_WM_STATE_MAXIMIZED_VERT"
    WM_STATE_MODAL="_NET_WM_STATE_MODAL"
    WM_STATE_SHADED="_NET_WM_STATE_SHADED"
    WM_STATE_SKIP_PAGER="_NET_WM_STATE_SKIP_PAGER"
    WM_STATE_SKIP_TASKBAR="_NET_WM_STATE_SKIP_TASKBAR"
    WM_STATE_STICKY="_NET_WM_STATE_STICKY"
    WM_VISIBLE_NAME="_NET_WM_VISIBLE_NAME"
    WM_WINDOW_TYPE="_NET_WM_WINDOW_TYPE"
    WORKAREA="_NET_WORKAREA"

class XlibHelpers():
    def __init__(self, display:Display|None=None, root:Window|None=None) -> None:
        self.display:Display
        if display is None:
            self.display=Display()
        else:
            self.display=display

        self.root:Window
        if root is None:
            self.root=self.display.screen().root
        else:
            self.root=root

    def focus_window(self, hex_id:str):
        self.set_active_window(hex_to_int(hex_id))

    def close(self, hex_id:str):
        xwin=self.get_window_from_hex_id(hex_id)
        if xwin is not None:
            self.set_prop("_NET_CLOSE_WINDOW", [int(time.mktime(time.localtime())), 1], xwin)

    def minimize(self, hex_id:str):
        xwin=self.get_window_from_hex_id(hex_id)
        if xwin is not None:
            self.set_wm_state(action=WindowStateAction.ADD, state=WindowState.HIDDEN, xwin=xwin)

    def select(self) -> Window:
        hex_id:str|None=None
        for line in cmd_filter_bad_window("xwininfo").splitlines():
            hex_id_raw=re.match(r".*Window id: ([^\s]+)", line)
            if hex_id_raw is not None:
                hex_id=hex(int(hex_id_raw.group(1), 16))

        if hex_id is None:
            raise Exception(f"Can't get id from selected window")
        
        xwin=self.get_window_from_hex_id(hex_id)
        if xwin is None:
            raise Exception(f"Can't get xlib window from hex id {hex_id}")\

        return xwin
    
    def get_parent(self, xwin:Window) -> Window:
        tmp_xwin=xwin
        g=tmp_xwin.get_geometry()
        root=g.root
        while True:
            parent=tmp_xwin.query_tree().parent
            if parent == root:
                break
            else:
                tmp_xwin=parent
        return tmp_xwin
    
    def get_geometry(self, xwin:Window, show_frame=False)-> GetGeometry:
        """
            grab the parent window before root it allows to get accurate coordinates from get_geometry at least on KDE
        """
        tmp_xwin=xwin
        g=tmp_xwin.get_geometry()
        root=g.root
        index=1
        if show_frame is True:
            print(f"### GET_GEOMETRY WITH ROOT {root}")
            print(f"### FRAME {index}: {tmp_xwin} x:{g.x} y:{g.y} w:{g.width} h:{g.height}")
        while True:
            parent=tmp_xwin.query_tree().parent
            index+=1
            if parent == root:
                if show_frame is True:
                    g=tmp_xwin.get_geometry()
                    print(f"### FRAME R: {tmp_xwin} x:{g.x} y:{g.y} w:{g.width} h:{g.height}")
                break
            else:
                tmp_xwin=parent
                if show_frame is True:
                    g=tmp_xwin.get_geometry()
                    print(f"### FRAME {index}: {tmp_xwin} x:{g.x} y:{g.y} w:{g.width} h:{g.height}")

        return tmp_xwin.get_geometry()

    def get_window_hex_id_from_pid(self, pid:int, wait_ms:int|None=None):
        wait_s:float=5
        if wait_ms is not None:
            wait_s=wait_ms/1000
            
        timer=TimeOut(wait_s).start()
        while True:
            prop = self.root.get_full_property(self.display.get_atom("_NET_CLIENT_LIST"), property_type=AnyPropertyType)
            if prop is None:
                raise NotImplementedError()
            client_list=prop.value
            for window_id in client_list:
                xwin = self.display.create_resource_object('window', window_id)
                prop=xwin.get_full_property(self.display.get_atom("_NET_WM_PID"), property_type=AnyPropertyType)
                if prop is not None:
                    if pid == prop.value[0]:
                        return hex(window_id)
            if timer.has_ended(pause=.001):
                break
        return None
    
    def get_recent_window_from_class(self, class_name:str)->Window|None:
        prop = self.root.get_full_property(self.display.get_atom("_NET_CLIENT_LIST_STACKING"), property_type=AnyPropertyType)
        if prop is None:
            raise NotImplementedError()
        for window_id in reversed(prop.value):
            xwin = self.display.create_resource_object('window', window_id)
            class_info=xwin.get_wm_class()
            if class_info is not None:
                if class_name == class_info[-1]:
                    return xwin
        return None
    
    def window_exists(self, hex_id:str):
        prop = self.root.get_full_property(self.display.get_atom("_NET_CLIENT_LIST"), property_type=AnyPropertyType)
        if prop is None:
            raise NotImplementedError()
        client_list=prop.value
        for window_id in client_list:
            if hex(window_id) == hex_id:
                return True
        return False
    
    def get_active_xwindow(self):
        dec_id=self.get_active_window_dec_id()
        if dec_id is None:
            return None
        else:
            return self.get_window_from_dec_id(dec_id=dec_id)
        
    def set_active_window(self, win_dec_id:int):
        current_dec_id=self.get_active_window_dec_id()
        if current_dec_id is None:
            current_dec_id=0
        xwin=self.get_window_from_dec_id(win_dec_id)
        self.set_prop(Atom.ACTIVE_WINDOW, [0, X.CurrentTime, current_dec_id], xwin)
        
    def get_active_window_dec_id(self)->int|None:
        prop = self.root.get_full_property(self.display.get_atom("_NET_ACTIVE_WINDOW"), property_type=AnyPropertyType)
        if prop is None:
            return None
        else:
            return prop.value[0]
        
    def get_active_window_hex_id(self):
        dec_id=self.get_active_window_dec_id()
        if dec_id is None:
            return None
        else:
            return hex(dec_id)
        
    def get_window_from_dec_id(self, dec_id:int):
        try:
            xwin = self.display.create_resource_object('window', dec_id)
            return xwin
        except:
            return None
        
    def get_window_from_hex_id(self, hex_id:str):
        return self.get_window_from_dec_id(dec_id=hex_to_int(hex_id))
    
    def get_show_desktop(self) -> bool|None:
        prop=self.get_prop("_NET_SHOWING_DESKTOP")
        if prop is not None:
            if prop[0] == 0:
                return False
            elif prop[0] == 1:
                return True
        return None

    def set_show_desktop(self, show=True):
        self.set_prop(prop_name="_NET_SHOWING_DESKTOP", data=[int(show)])

    def get_window_view_state(self, xwin:Window) -> WindowViewState:
        state=xwin.get_wm_state()
        if state is None:
            raise NotImplementedError()
        return WindowViewState(state["state"])
    
    def set_window_view_state(self, xwin:Window, view_state:WindowViewState, wait_ms:int|None=None):
        current_view_state=self.get_window_view_state(xwin=xwin)
        if current_view_state != view_state:
            self.set_prop("WM_CHANGE_STATE", [view_state.value], xwin)
            if wait_ms is not None:
                timer=TimeOut(wait_ms/1000).start()
                while True:
                    if self.get_window_view_state(xwin=xwin) == view_state:
                        break
                    if timer.has_ended(pause=.001):
                        raise Exception(f"For window {hex(xwin.id)} couldn't set state {view_state.name}.")

    def get_prop(self, prop_name:str, xwin:Window|None=None)-> tuple[int]|str|None:
        if xwin is None:
            xwin = self.root
        atom = xwin.get_full_property(self.display.get_atom(prop_name),X.AnyPropertyType)
        if atom is None:
            return None
        else:
            return atom.value
        
   

    def set_prop(self, prop_name:str, data:str|list[int], xwin:Window|None=None, mask:int|None=None, flush:bool=True) -> None:
        if xwin is None:
            xwin = self.root
        data_size:int
        ev:ClientMessage
        if isinstance(data, str):
            # Couldn't set a string property with ClientMessage it seems that part of the code has a bug
            xwin.change_property(self.display.intern_atom(prop_name), STRING, 8, data.encode("UTF-8"))
            xwin.get_wm_state() # that is needed to apply the property (but why?, display.flush or sync not doing anything)
        else:
            data = (data+[0]*(5-len(data)))[:5]
            data_size = 32

            ev = ClientMessage(
                window=xwin, 
                client_type=self.display.get_atom(prop_name), 
                data=(data_size, data),
            )
   
            if mask is None:
                mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
            self.root.send_event(ev, event_mask=mask)
            if flush is True:
                self.display.flush()

    def has_wm_state(self, state:WindowState|Atom, xwin:Window|None=None):
        state_id=self.display.get_atom(state)
        states = self.get_prop("_NET_WM_STATE", xwin)
        if states is not None:
            for atom_id in states:
                if atom_id == state_id:
                    return True
        return False

    def get_wm_state(self, xwin:Window|None=None):
        states = self.get_prop("_NET_WM_STATE", xwin)
        dy_states:dict[int, str]=dict()
        if states is not None:
            for atom in states:
                dy_states[cast(int, atom)]=self.display.get_atom_name(cast(int, atom))
        return dy_states
    
    def wait_for_state(self, wait_ms:int, state:WindowState|Atom, need_state:bool, xwin:Window, action:WindowStateAction|None=None,):
        timer=TimeOut(wait_ms/1000).start()
        while True:
            if self.has_wm_state(state=state, xwin=xwin) == need_state:
                break
            if timer.has_ended(pause=.001):
                if action is None:
                    if need_state is True:
                        raise Exception(f"For window {hex(xwin.id)} state {state.value} is not SET.")
                    else:
                        raise Exception(f"For window {hex(xwin.id)} state {state.value} is still SET.")
                else:
                    raise Exception(f"For window {hex(xwin.id)} couldn't {action.name} state {state.value}.")

    def set_wm_state(
        self, 
        action:WindowStateAction, 
        state:WindowState|Atom, 
        xwin:Window|None=None, 
        extra_state:WindowState|None=None,
        wait_ms:int|None=None,
    ):
        """
            wait_ms: if provided wait in milliseconds until the state has been added, removed, or toggled. It raises en Exception if operation fails.
        """
        has_state=False
        has_extra_state=False
        if wait_ms is not None:
            if action == WindowStateAction.TOGGLE:
                has_state=self.has_wm_state(state=state, xwin=xwin)
                if extra_state is not None:
                    has_extra_state=self.has_wm_state(state=extra_state, xwin=xwin)
            
        state_value:int = self.display.get_atom(state.value, True)
        extra_state_value:int
        if extra_state is None:
            extra_state_value=0
        else:
            extra_state_value = self.display.get_atom(extra_state.value, True)
        self.set_prop("_NET_WM_STATE", [action.value, state_value, extra_state_value, 1], xwin)

        if xwin is None:
            xwin=self.root

        if wait_ms is not None:
            need_state:bool
            need_extra_state:bool
            if action == WindowStateAction.ADD:
                need_state=True
                if has_extra_state:
                    need_extra_state=True
            elif action == WindowStateAction.REMOVE:
                need_state=False
                if has_extra_state:
                    need_extra_state=False
            elif action == WindowStateAction.TOGGLE:
                need_state=not has_state
                if has_extra_state:
                    need_extra_state=not has_extra_state
            else:
                raise NotImplementedError()

            self.wait_for_state(wait_ms=wait_ms, state=state, action=action, need_state=need_state, xwin=xwin)
            if has_extra_state is True:
                self.wait_for_state(wait_ms=wait_ms, state=state, action=action, need_state=need_extra_state, xwin=xwin)
