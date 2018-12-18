#!/usr/bin/env python3
# author: Gabriel Auger
# version: 1.0.0-alpha-1545139369
# name: guitools
# license: MIT

import re
import subprocess, shlex, inspect
from pprint import pprint

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import modules.shell_helpers.shell_helpers as shell
import modules.message.message as msg
import time

del sys.path[0:2]

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
        self.monitors=""
        self.command=""
        self.exe_name=""

        if hex_id:
            self.hex_id=hex(int(hex_id, 16))
            self.update_fields()

    def update_fields(self, hex_id=""):
        if hex_id:
            self.hex_id=hex(int(hex_id, 16))
        else:
            if not self.hex_id:
                msg.user_error("Window hex_id '{}' has not been defined, thus update_fields can't run.")
                sys.exit(1)

        window=""
        wmctrl_fields=shell.cmd_get_value("wmctrl -lGpx")
        for line in wmctrl_fields.splitlines():
            hex_id=hex(int(line.split(" ")[0].strip(),16))
            if hex_id == self.hex_id:
                window=line
                break
        
        if not window:
            time.sleep(.5)
            wmctrl_fields=shell.cmd_get_value("wmctrl -lGpx")
            for line in wmctrl_fields.splitlines():
                hex_id=hex(int(line.split(" ")[0].strip(),16))
                if hex_id == self.hex_id:
                    window=line
                    break

            if not window:
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
            self.command=shell.cmd_get_value("ps -p {} -f -o cmd=".format(self.pid))
            self.exe_name=shell.cmd_get_value("ps -p {} -o comm=".format(self.pid))

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
        if obj_geometry:
            if "x" in obj_geometry:
                x=obj_geometry["x"]+self.border_left
            if "y" in obj_geometry:
                y=obj_geometry["y"]+self.border_top
            if "width" in obj_geometry:
                width=obj_geometry["width"]-self.border_left-self.border_right
            if "height" in obj_geometry:
                height=obj_geometry["height"]-self.border_top-self.border_bottom
        
        self.release_edges()
        os.system("wmctrl -i -r {hex_id} -e 0,{x},{y},{width},{height}".format(
            hex_id=self.hex_id,
            x=x,
            y=y,
            width=width,
            height=height,
        ))

        # then update geometry
        self.update_fields()


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

    def tile(self, direction, monitor_num=""): # left or right
        monitors=[]
        if not self.monitors:
            self.monitors=self.get_monitors()

        if monitor_num:
            monitors.append(self.monitors.monitors[monitor_num-1])
        else:
            monitors=self.monitors.monitors

        tiles=[]
        for monitor in monitors:
            tiles.extend(monitor.get_tiles(2, 1, True))

        selected_tile=""
        tile_num=0
        stop=False
        tolerance=10 # I had to put a tolerance because the snap function of kwin just increase the window border with 4 pixels all around
        for tile in tiles:
            if tile.contains(self.upper_left_x, self.upper_left_y):
                if  (self.frame_upper_left_x >= (tile.upper_left_x - tolerance) and self.frame_upper_left_x <= (tile.upper_left_x + tolerance)) and (self.frame_upper_left_y >= (tile.upper_left_y - tolerance) and self.frame_upper_left_y <= (tile.upper_left_y + tolerance)):
                # if tile.contains(self.frame_upper_left_x, self.frame_upper_left_y):
                    # if self.frame_width == tile.width and self.frame_height == tile.height:
                    if  (self.frame_width >= (tile.width - tolerance) and self.frame_width <= (tile.width + tolerance)) and (self.frame_height >= (tile.height - tolerance) and self.frame_height <= (tile.height + tolerance)):
                        if direction == "left":
                            if tile_num == 0:
                                return True
                            else:
                                selected_tile=tiles[tile_num-1]
                                if tile_num-1 == 0:
                                    stop=True
                        elif direction == "right":
                            if tile_num == (len(tiles) -1):
                                return True
                            else:
                                selected_tile=tiles[tile_num+1]
                                if tile_num+1 == len(tiles)-1:
                                    stop=True
                    else:
                        selected_tile=tile
                else:
                    selected_tile=tile

            tile_num+=1

        if not selected_tile:
            if direction == "left":
                selected_tile=tiles[0]
            elif direction == "right":
                selected_tile=tiles[-1]

        self.set_geometry(dict(
            x=selected_tile.upper_left_x, 
            y=selected_tile.upper_left_y, 
            width=selected_tile.width, 
            height=selected_tile.height)
        )

        self.update_fields()

        return stop

    def minimize(self):
        os.system("xdotool windowminimize {}".format(self.dec_id))
        self.update_fields()

    def maximize(self):
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
            tmp_line=re.sub(' +', ' ', line.strip())
            tmp_line=tmp_line.split(" ")
            hex_id=hex(int(tmp_line[0], 16))
            line_pid=int(tmp_line[2])
            if pid == line_pid:
                return hex_id      
        
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
        names=[]
        for window in self.windows:
            classes.append(window._class)
            names.append(window.name)

        classes=sorted(set(classes))
        names=sorted(set(names))

        indices=[]
        for window in self.windows:
            num=int(str(classes.index(window._class)+1)+""+str(names.index(window.name)+1))
            indices.append(num)
        
        tmp_windows=[]
        for index in bubble_sort_array(indices, len(indices)):
            tmp_windows.append(self.windows[index])

        self.windows=tmp_windows

        return self

    def print(self):
        for window in self.windows:
            window.print()
