#!/usr/bin/env python3
# author: Gabriel Auger
# version: 5.1.0
# name: shell_helpers
# license: MIT

import platform
import shutil
import subprocess
import sys
import shlex
import inspect

import sys, os

from ..gpkgs import message as msg

def get_split_cmd(command):
    split_cmd=command
    if isinstance(command, str):
        split_cmd=shlex.split(command)
    if platform.system() == "Windows":
        # if shutil.which(split_cmd[0]) is None:
        split_cmd.insert(0, "cmd")
        split_cmd.insert(1, "/c")
    return split_cmd

def cmd_devnull(command):
    try:
        return subprocess.check_call(get_split_cmd(command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as proc:
        return proc.returncode

# ideal for any command with prompt
def cmd(command):
    try:
        return subprocess.call(get_split_cmd(command), shell=False)
    except subprocess.CalledProcessError as proc:
        return proc.returncode

def cmd_get_value(command, none_on_error=False, no_err_if_std=False):
    try:
        process = subprocess.Popen(get_split_cmd(command), 
                                    shell=False, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        ( stdout, stderr ) = process.communicate()
        if stderr:
            if no_err_if_std is True:
                if stdout:
                    return stdout.decode("utf-8").rstrip()

            if none_on_error is True:
                return None
            else:
                frame,filename,line_number,function_name,lines,index=inspect.stack()[1]
                print("\t"+str(line_number)+": "+filename)
                msg.error("Command: '"+get_cmd_str(command)+"', err: "+stderr.decode("utf-8"))
                sys.exit(1)

        if stdout:
            return stdout.decode("utf-8").rstrip()
        else:
            return None
    except Exception as e:
        frame,filename,line_number,function_name,lines,index=inspect.stack()[1]
        print(e)
        print("\t"+str(line_number)+": "+filename)
        msg.error("Command: '"+get_cmd_str(command))
        sys.exit(1)

def cmd_prompt(cmd_txt, 
    error=True,
    fail_exit=1, 
    info=False, 
    success=True, 
):
    if info is True:
        msg.info(get_cmd_str(cmd_txt))

    if cmd(cmd_txt) == 0:
        if success is True:
            msg.success(get_cmd_str(cmd_txt))
    else:
        if error is True:
            msg.error(get_cmd_str(cmd_txt) +" failed!")
        if fail_exit is not None:
            sys.exit(fail_exit)

def get_cmd_str(command):
    if isinstance(command, str):
        return command
    else:
        cmd_string=""
        for e, elem in enumerate(command):
            if " " in elem:
                elem='"{}"'.format(elem)
            if e == 0:
                cmd_string=elem
            else:
                cmd_string+=" {}".format(elem)

        return cmd_string

def rmtree(path, pfm=None):
    if pfm is None:
        pfm=platform.system()
    if pfm == "Windows":
        os.system('rmdir /S /Q "{}"'.format(path))
    elif pfm == "Linux":
        shutil.rmtree(path)
    else:
        msg.error("platform '{}' not supported".format(pfm), trace=True, exit=1)
