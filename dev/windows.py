#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1545343677
# name: guitools
# license: MIT

import re
import subprocess, shlex, inspect
from pprint import pprint
import time

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import modules.shell_helpers.shell_helpers as shell
import modules.message.message as msg
from modules.timeout.timeout import Timeout
import shutil
del sys.path[0:2]

def get_exe_paths_from_pid(pid):
    exe_name, command=shell.cmd_get_value("ps -q {} -o \"%c\" -o \":%a\" --no-headers".format(pid)).split(":")
    exe_name=exe_name.strip()
    command=command.strip()
    filenpa_exe=""
    # this loop does not take in account path with spaces.
    for c in command:
        if c == " ":
            break
        filenpa_exe+=c

    if filenpa_exe[0] != os.sep:
        filenpa_exe=shutil.which(filenpa_exe)

    return exe_name, command, filenpa_exe

class Regular_windows(object):
    def __init__(self):
        self.windows=[]
        self.get_windows()
        self.sorted_by_exe_names()

    def get_windows(self):
        command="wmctrl -lp"
        timer=Timeout(1.5)
        while True:
            stderr=""
            process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ( stdout, stderr ) = process.communicate()
            if stderr:
                if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8"):
                    msg.app_error("cmd: '{}' failed".format(command))
                    sys.exit(1)

            if stdout:
                break

            if timer.has_passed():
                msg.user_error("Can't get window list from wmctrl")
                sys.exit(1)

        window_ids=stdout.decode("utf-8").rstrip()

        for line in window_ids.splitlines():
            tmp_line=re.sub(' +', ' ', line.strip()).split(" ")
            hex_id=hex(int(tmp_line[0], 16))
            xprop_fields=output=shell.cmd_get_value("xprop -id {} _NET_WM_WINDOW_TYPE".format(hex_id))
            if "_NET_WM_WINDOW_TYPE_NORMAL" in xprop_fields or "not found" in xprop_fields:
                window=dict(
                    hex_id=hex_id,
                    pid=int(tmp_line[2]),
                    name=" ".join(tmp_line[4:]),
                )

                exe_name, command, filenpa_exe = get_exe_paths_from_pid(window["pid"])

                window.update(
                    exe_name=exe_name,
                    command=command,
                    filenpa_exe=filenpa_exe
                )

                self.windows.append(window)
        
    @staticmethod
    def focus(hex_id):
        shell.cmd("wmctrl -i -a {}".format(hex_id))

    def print(self):
        for window in self.windows:
            pprint(window)

    def sorted_by_exe_names(self):
        exe_names=[]
        for window in self.windows:
            exe_names.append(window["exe_name"].lower())

        exe_names=sorted(set(exe_names))

        tmp_windows=[]
        for exe_name in exe_names:
            tmp_names=[]
            tmp_indexes=[]
            for w, window in enumerate(self.windows):
                if window["exe_name"].lower() == exe_name:
                    tmp_indexes.append(w)                        
                    tmp_names.append(window["name"].lower())

            for index in bubble_sort_array(tmp_names, len(tmp_names)):
                tmp_windows.append(self.windows[tmp_indexes[index]])

        self.windows=tmp_windows

        return self

def bubble_sort_array(array, size):
    temp="" # int
    swap=True # boolean
    index_array=[]

    for i in range(0, size):
        index_array.append(i)

    index_order=[]

    while swap:
        swap=False
        count2=0
        for count in range(0, size-1):
            if array[count] > array[count + 1]:
                temp = array[count]
                array[count] = array[count + 1]
                array[count + 1] = temp

                temp_index = index_array[count]
                index_array[count] = index_array[count+1]
                index_array[count +1] = temp_index

                swap = True

    return index_array
    
class Taskbar(object):
    def __init__(self):
        self.upper_left_x=""
        self.upper_left_y=""
        self.width=""
        self.height=""

class Taskbars(object):
    def __init__(self):
        self.taskbars=[]
        command="wmctrl -lGpx"
        stderr="start"
        while stderr:
            stderr=""
            process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ( stdout, stderr ) = process.communicate()
            if stderr:
                if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8"):
                    msg.app_error("cmd: '{}' failed".format(command))
                    sys.exit(1)

        window_ids=stdout.decode("utf-8").rstrip()
        for line in window_ids.splitlines():
            line=re.sub(r" +", " ", line.strip()).split(" ")
            hex_id=hex(int(line[0], 16))
            xprop_fields=output=shell.cmd_get_value("xprop -id {} _NET_WM_WINDOW_TYPE".format(hex_id))
            if "_NET_WM_WINDOW_TYPE_DOCK" in xprop_fields:
                taskbar=Taskbar()
                taskbar.upper_left_x=int(line[3])
                taskbar.upper_left_y=int(line[4])
                taskbar.width=int(line[5])
                taskbar.height=int(line[6])
                self.taskbars.append(taskbar)

class Window(object):
    def __init__(self, hex_id=""):
        self.type=""
        self.hex_id=""
        self.dec_id=""
        self.pid=""
        self.upper_left_x=""
        self.upper_left_y=""
        self.width=""
        self.height=""
        self.class_long=""
        self._class=""
        self.name=""
        self.border_left=0
        self.border_right=0
        self.border_bottom=0
        self.border_top=0
        self.frame_width=""
        self.frame_height=""
        self.frame_upper_left_x=""
        self.frame_upper_left_y=""
        self.command=""
        self.exe_name=""
        self.monitor=""
        self.monitors=self.get_monitors()
        self.min_width=50
        self.min_height=50

        if hex_id:
            self.hex_id=hex(int(hex_id, 16))
            self.update_fields()

    def update_fields(self, hex_id="", monitor=""):
        if hex_id:
            self.hex_id=hex(int(hex_id, 16))
        else:
            if not self.hex_id:
                msg.user_error("Window hex_id '{}' has not been defined, thus update_fields can't run.")
                sys.exit(1)

        window=""
        timer=Timeout(2)
        while True:
            wmctrl_fields=shell.cmd_get_value("wmctrl -lGpx")
            for line in wmctrl_fields.splitlines():
                hex_id=hex(int(line.split(" ")[0].strip(),16))
                if hex_id == self.hex_id:
                    window=line
                    break
            
            if window:
                break
            
            if timer.has_ended():
                msg.user_error("Window with id '{}' not found.".format(self.hex_id))
                sys.exit(1)

        divider=True
        field=""
        fields=[]
        num_fields=10
        field_num=1
        last_field_started=False
        for i, c in enumerate(window):
            if i == 0:
                field+=c
            elif i < len(window)-1:
                if field_num < num_fields:
                    if c == " ":
                        if not window[i-1] == " ":
                            fields.append(field)
                            field_num+=1
                            field=""
                    else:

                        field+=c
                else:
                    if last_field_started:
                        field+=c
                    else:
                        if c != " ":
                            last_field_started=True
                            field+=c
            else:
                field+=c
                fields.append(field)
                field_num+=1
                field=""

        self.hex_id=hex(int(fields[0],16))
        self.dec_id=int(fields[0], 16)
        self.sticky=True if fields[1] == "-1" else False
        self.pid=int(fields[2])
        self.upper_left_x=int(fields[3])
        self.upper_left_y=int(fields[4])
        self.width=int(fields[5])
        self.height=int(fields[6])
        self.class_long=fields[7]
        self._class=fields[7].split(".")[0]
        self.hostname=fields[8]
        self.name=fields[9]

        xprop_fields=output=shell.cmd_get_value("xprop -id {} _NET_FRAME_EXTENTS _NET_WM_WINDOW_TYPE".format(self.hex_id))
        for line in xprop_fields.splitlines():
            line=line.replace(":", "=")
            if "=" in line:
                field, value = line.split("=")
                value=value.strip()
                if "_NET_FRAME_EXTENTS" in field:
                    if value != "not found.":
                        borders=value.replace(" ","").split(",")
                        borders=list(map(int, borders))
                        self.border_left, self.border_right, self.border_top, self.border_bottom = borders
                elif "_NET_WM_WINDOW_TYPE" in field:
                    if value != "not found.":
                        self.type= value
                    else:
                        self.type="UNKNOWN"

        self.frame_width=self.width+self.border_left+self.border_right
        self.frame_height=self.height+self.border_top+self.border_bottom
        self.frame_upper_left_x=self.upper_left_x-self.border_left
        self.frame_upper_left_y=self.upper_left_y-self.border_top

        if self.pid != 0 and self.pid != "":
            self.exe_name, self.command, self.filenpa_exe = get_exe_paths_from_pid(self.pid)

        if not monitor:
            self.monitor=self.monitors.get_monitor_from_coords(self.upper_left_x, self.upper_left_y)
            if not self.monitor:
                self.monitor=self.monitors.monitors[0]
        else:
            self.monitor=monitor

        xwininfo_minimum_size=shell.cmd_get_value("xwininfo -id {} -size".format(self.hex_id))
        for line in xwininfo_minimum_size.splitlines():
            if "Program supplied minimum size:" in line:
                min_width, min_height = line.split(":")[1].strip().split(" by ")
                self.min_width=int(min_width)
                self.min_height=int(min_height)

        return self

    def print(self):
        pprint(vars(self))
        return self

    def focus(self):
        shell.cmd("wmctrl -i -a {}".format(self.hex_id))
        return self

    def set_above(self):
        shell.cmd("wmctrl -i -r {} -b add,above".format(self.hex_id))
        return self
    
    def unset_above(self):
        shell.cmd("wmctrl -i -r {} -b remove,above".format(self.hex_id))
        return self

    def get_center_coords(self, monitor=""):
        if not monitor:
            if not self.monitors:
                self.monitors=self.get_monitors()
            monitor=self.monitors.get_active()

        mid_width=int(monitor.width/2)
        mid_height=int(monitor.height/2)
        center_x=monitor.range_x[0]+mid_width
        center_y=monitor.range_y[0]+mid_height

        mid_window_width=int((self.width+self.border_left+self.border_right)/2)
        mid_window_height=int((self.height+self.border_top+self.border_bottom)/2)

        x=center_x-mid_window_width
        y=center_y-mid_window_height
        
        return [x, y]

    def map(self):
        os.system("xdotool windowmap --sync {dec_id}".format(dec_id=self.dec_id))
        return self

    def unmap(self):
        os.system("xdotool windowunmap --sync {dec_id}".format(dec_id=self.dec_id))
        return self

    def exists(self):
        command="wmctrl -l"
        stderr="start"
        while stderr:
            stderr=""
            process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ( stdout, stderr ) = process.communicate()
            if stderr:
                if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8"):
                    msg.app_error("cmd: '{}' failed".format(command))
                    sys.exit(1)

        window_ids=stdout.decode("utf-8").rstrip()
        for line in window_ids.splitlines():
            hex_id=hex(int(line.split(" ")[0].strip(), 16))
            if self.hex_id == hex_id:
                return True
        
        return False

    def release_edges(self):
        os.system("xdotool windowunmap --sync {dec_id}; xdotool windowsize {dec_id} {resize_x} {resize_y}; xdotool windowmap --sync {dec_id}".format(
            dec_id=self.dec_id,
            resize_x=100,
            resize_y=100
        ))
        return self

    def set_geometry(self, obj_geometry):
        x = self.upper_left_x
        y = self.upper_left_y
        width = self.width
        height = self.height

        width_ok=True
        height_ok=True
        x_ok=True
        y_ok=True

        if obj_geometry:
            if "x" in obj_geometry:
                x=obj_geometry["x"]+self.border_left
                x_ok=False
            if "y" in obj_geometry:
                y=obj_geometry["y"]+self.border_top
                y_ok=False
            if "width" in obj_geometry:
                width=obj_geometry["width"]-self.border_left-self.border_right
                width_ok=False
            if "height" in obj_geometry:
                height=obj_geometry["height"]-self.border_top-self.border_bottom
                height_ok=False


        timer=Timeout(1.5)
        tolerance=10
        pass_counter=0
        while True:
            os.system("wmctrl -i -r {hex_id} -e 0,{x},{y},{width},{height}".format(
                hex_id=self.hex_id,
                x=x,
                y=y,
                width=width,
                height=height,
            ))

            self.update_fields()
            
            if timer.has_ended():
                print("# Timer Ended for set geometry #")
                break

            if not width_ok:
                if abs(self.width - width) > tolerance:
                    if self.width <= self.min_width:
                        width_ok=True
                else:
                    width_ok=True
            
            if not height_ok:
                if abs(self.height - height) > tolerance:
                    if self.height <= self.min_height:
                        height_ok=True
                else:
                    height_ok=True

            if not x_ok:
                if abs(self.upper_left_x - x) <= tolerance:
                    x_ok=True

            if not y_ok:
                if abs(self.upper_left_y - y) <= tolerance:
                    y_ok=True

            if width_ok and height_ok and x_ok and y_ok:
                break
            else:
                pass_counter+=1
                self.release_edges()
            
        return self

    def move(self, x, y):
        self.set_geometry(dict(x=x, y=y))
        return self

    def resize(self, width, height):
        self.set_geometry(dict(width=width, height=height))
        return self

    def get_monitors(self):
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        from monitors import Monitors
        del sys.path[0:1]

        return Monitors()

    def get_overlapped_area(self, tile):
        r1={}
        r2={}
        l1={}
        l2={}

        l1["x"]=self.frame_upper_left_x
        l1["y"]=self.frame_upper_left_y

        r1["x"]=self.frame_upper_left_x+self.frame_width
        r1["y"]=self.frame_upper_left_y+self.frame_height
        
        l2["x"]=tile.upper_left_x
        l2["y"]=tile.upper_left_y
        
        r2["x"]=tile.upper_left_x+tile.width
        r2["y"]=tile.upper_left_y+tile.height

        area1 = abs(l1["x"] - r1["x"]) * abs(l1["y"] - r1["y"]) 
  
        area2 = abs(l2["x"] - r2["x"]) * abs(l2["y"] - r2["y"]) 

        areaI = (min(r1["x"], r2["x"]) - max(l1["x"], l2["x"])) * (min(r1["y"], r2["y"]) - max(l1["y"], l2["y"])) 

        surface_union= area1+area2-areaI

        ratio= int(areaI/surface_union * 100)

        if ratio < 0:
            ratio=0

        return ratio

    def tile(self, direction, monitor_index=None): # left, right
        monitors=[]
        
        if monitor_index is None:
            monitors=self.monitors.monitors
        else:
            if monitor_index in range(0, len(self.monitors.monitors)):
                monitors.append(self.monitors.monitors[monitor_index])
            else:
                monitors.append(self.monitors.monitors[0])
            
        tiles=[]
        for monitor in monitors:
            tiles.extend(monitor.get_tiles(2, 1, True))

        selected_tile=""
        tile_num=0
        stop=""
        tolerance=10
        ratios_overlap=[]
        for tile in tiles:
            ratios_overlap.append(self.get_overlapped_area(tile))

        max_ratio=max(ratios_overlap)
        
        if max_ratio == 0:
            if direction == "left":
                selected_tile=tiles[0]
                stop=True
            elif direction == "right":
                selected_tile=tiles[-1]
                stop=True
        else:
            ratio_index_duplicates=[]

            for r, ratio in enumerate(ratios_overlap):
                if ratio == max_ratio:
                    ratio_index_duplicates.append(r)

            if direction == "left":
                tile_index=ratio_index_duplicates[0]

                if tile_index == 0:
                    if max_ratio >= 98:
                        return True
                    else:
                        selected_tile=tiles[tile_index]
                        stop=True
                else:
                    selected_tile=tiles[tile_index-1]
                    if tile_index-1 == 0:
                        stop=True
                    else:
                        stop=False
            elif direction == "right":
                tile_index=ratio_index_duplicates[-1]

                if tile_index==(len(tiles)-1):
                    if max_ratio >= 98:
                        return True
                    else:
                        selected_tile=tiles[len(tiles)-1]
                        stop=True
                else:
                    selected_tile=tiles[tile_index+1]
                    if tile_index+1 == (len(tiles)-1):
                        stop=True
                    else:
                        stop=False

        self.set_geometry(dict(
            x=selected_tile.upper_left_x, 
            y=selected_tile.upper_left_y, 
            width=selected_tile.width, 
            height=selected_tile.height)
        )

        return stop

    def get_tile(self):
        tiles=[]
        tiles_labels=[]
        for monitor in self.monitors.monitors:
            tiles.extend(monitor.get_tiles(2, 1, True))
            tiles_labels.extend(["left", "right"])

        window_area=self.width * self.height
        for t, tile in enumerate(tiles):
            tile_area=tile.width * tile.height
            if tile.contains(self.upper_left_x, self.upper_left_y):
                if window_area > tile_area:
                    return "maximize"
                else:
                    return tiles_labels[t]

        return "maximize"


    def minimize(self):
        os.system("xdotool windowminimize {}".format(self.dec_id))
        self.update_fields()

    def maximize(self, monitor_index=None):
        monitor=""
        if monitor_index is None:
            monitor=self.monitors.get_active()
        else:
            if monitor_index in range(0, len(self.monitors.monitors)):
                monitor=self.monitors.monitors[monitor_index]
            else:
                monitor=self.monitors.monitors[0]

        if monitor.index != self.monitor.index:
            self.move(monitor.upper_left_x, monitor.upper_left_y)
        os.system("wmctrl -i -r {} -b add,maximized_vert,maximized_horz".format(self.hex_id))
        self.update_fields()

    def center(self, monitor=""):
        x, y =self.get_center_coords()
        self.move(x, y)

    def close(self):
        os.system("wmctrl -i -c {}".format(self.hex_id))

class Windows(object):
    def __init__(self):
        self.windows=[]
        self.get_all_windows()

    def get_active(self):
        hex_id=self.get_active_hex_id()
        if not hex_id:
            return ""
        else:
            return Window().update_fields(hex_id)
    
    @staticmethod
    def get_window_hex_id_from_pid(pid):
        command="wmctrl -lp"
        timer=Timeout(2)
        while True:
            process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ( stdout, stderr ) = process.communicate()
            if stderr:
                if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8"):
                    msg.app_error("cmd: '{}' failed".format(command))
                    sys.exit(1)

            window_ids=stdout.decode("utf-8").rstrip()

            for line in window_ids.splitlines():
                tmp_line=re.sub(' +', ' ', line.strip())
                tmp_line=tmp_line.split(" ")
                hex_id=hex(int(tmp_line[0], 16))
                line_pid=int(tmp_line[2])
                if pid == line_pid:
                    return hex_id

            if timer.has_ended():
                msg.warning("Could not get an hex_id from pid {}".format(pid))
                break
   
        return ""

    @staticmethod
    def get_active_hex_id():
        hex_id=hex(int(shell.cmd_get_value("xdotool getactivewindow")))
        if not hex_id:
            return ""
        else:
            return hex_id

    @staticmethod
    def exists(hex_id):
        command="wmctrl -l"
        stderr="start"
        while stderr:
            stderr=""
            process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ( stdout, stderr ) = process.communicate()
            if stderr:
                if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8"):
                    msg.app_error("cmd: '{}' failed".format(command))
                    sys.exit(1)

        window_ids=stdout.decode("utf-8").rstrip()
        for line in window_ids.splitlines():
            line_hex_id=hex(int(line.split(" ")[0].strip(), 16))
            if hex_id == line_hex_id:
                return True
        
        return False

    def get_all_windows(self):
        command="wmctrl -l"
        stderr="start"
        while stderr:
            stderr=""
            process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ( stdout, stderr ) = process.communicate()
            if stderr:
                if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8"):
                    msg.app_error("cmd: '{}' failed".format(command))
                    sys.exit(1)

        window_ids=stdout.decode("utf-8").rstrip()

        for line in window_ids.splitlines():
            hex_id=hex(int(line.strip().split(" ")[0], 16))
            self.windows.append(Window().update_fields(hex_id))
        return self

    def filter_regular_type(self):
        tmp_windows=[]
        for window in self.windows:
            if window.type == "_NET_WM_WINDOW_TYPE_NORMAL" or window.type == "UNKNOWN":
                tmp_windows.append(window)

        self.windows=tmp_windows

        return self

    def get_taskbars(self):
        tmp_windows=[]
        for window in self.windows:
            if window.type == "_NET_WM_WINDOW_TYPE_DOCK":
                tmp_windows.append(window)

        return tmp_windows

    def sorted_by_class(self):
        classes=[]
        for window in self.windows:
            classes.append(window._class.lower())

        classes=sorted(set(classes))

        tmp_windows=[]
        for _class in classes:
            tmp_names=[]
            tmp_indexes=[]
            for w, window in enumerate(self.windows):
                if window._class.lower() == _class:
                    tmp_indexes.append(w)                        
                    tmp_names.append(window.name.lower())

            for index in bubble_sort_array(tmp_names, len(tmp_names)):
                tmp_windows.append(self.windows[tmp_indexes[index]])

        self.windows=tmp_windows

        return self

    def print(self):
        for window in self.windows:
            window.print()
