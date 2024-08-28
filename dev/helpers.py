#!/usr/bin/env python3
from pprint import pprint
import os
import shlex
import shutil
import subprocess
import sys
import time
import shlex

from ..gpkgs.timeout import TimeOut

class ExeInfo():
    def __init__(self, pid:int, command:str|list[str]|None=None)->None:
        self.pid=pid
        self.exe_name:str
        self.command:str
        self.filenpa_exe:str
        self.set(command=command)

    def set(self, command:str|list[str]|None=None):
        if self.pid == 0:
            self.exe_name="unknown"
            self.command="unknown"
            self.filenpa_exe="unknown"
        else:
            cmd=[
                "ps",
                # ww to have all the parameters with executable path
                # "-awxwe",
                "-q",
                str(self.pid),
                "-o",
                "%c",
                "-o",
                ":%a",
                "--no-headers",
            ]
            ps_values=subprocess.check_output(cmd).decode().rstrip().split(":")

            exe_name=ps_values[0]
            tmp_command="".join(ps_values[1:])

            cmd=[
                "ls",
                "-l",
                "/proc/{}/exe".format(self.pid),
            ]

            filenpa_exe=None
            try:
                # ls can provide full executable path without parameters
                #  it is better to grab executable path with spaces
                # however ls get permission denied on process owned by root so in that case ps is used but ps get full executable path with all arguments and then it is impossible to tell exactly the path of the executable if spaces are present in that path.
                ls_values=subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().rstrip()
                filenpa_exe=ls_values.split()[-1]
            except:
                filenpa_exe=tmp_command.split()[0]

            if filenpa_exe[0] != os.sep:
                tmp_filenpa_exe=shutil.which(filenpa_exe)
                if tmp_filenpa_exe is not None:
                    filenpa_exe=tmp_filenpa_exe

            if command is None:
                command=tmp_command

            self.exe_name=exe_name
            if isinstance(command, list):
                self.command=shlex.join(command)
            else:
                self.command=command
            self.filenpa_exe=filenpa_exe

def cmd_filter_bad_window(command, get_stdout=True):
    timer=TimeOut(3).start()
    while True:
        if timer.has_ended(pause=.001):
            raise Exception("Can't get output from cmd '{}'".format(command))

        stderr=""
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ( stdout, stderr ) = process.communicate()
        if stderr:
            if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8") and \
            not "xwininfo: error: Can't grab the mouse." in stderr.decode("utf-8"):
                raise Exception("cmd: '{}' failed".format(command))
                sys.exit(1)
            else:
                if "xprop -id" in command:
                    return "BadWindow"
                else:
                    continue
    
        if stdout:
            return stdout.decode("utf-8").rstrip()
        
        if not get_stdout:
            break

def bubble_sort_array(array, size):
    temp="" # int
    swap=True # boolean
    index_array=[]

    for i in range(0, size):
        index_array.append(i)

    while swap:
        swap=False
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

def hex_to_int(hex_id:str):
    if hex_id[:2] == "0x":
        return int(hex_id, 16)
    else:
        return int(hex_id, 0)