#!/usr/bin/env python3
from pprint import pprint
import os
import shlex
import shutil
import subprocess
import sys
import time

from ..gpkgs.timeout import TimeOut
from ..gpkgs import message as msg

def get_exe_paths_from_pid(pid):
    values=subprocess.check_output([
        "ps",
        "-q",
        str(pid),
        "-o",
        "%c",
        "-o",
        ":%a",
        "--no-headers",
    ]).decode().rstrip().split(":")

    exe_name, command=values[0], "".join(values[1:])
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
        command=filenpa_exe+command[len(exe_name):]

    return exe_name, command, filenpa_exe

def cmd_filter_bad_window(command, get_stdout=True):
    timer=TimeOut(3).start()
    while True:
        if timer.has_ended(pause=.001):
            msg.error("Can't get output from cmd '{}'".format(command))
            sys.exit(1)

        stderr=""
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ( stdout, stderr ) = process.communicate()
        if stderr:
            if not "X Error of failed request:  BadWindow" in stderr.decode("utf-8"):
                msg.error("cmd: '{}' failed".format(command))
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