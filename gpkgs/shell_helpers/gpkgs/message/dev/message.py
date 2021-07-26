#!/usr/bin/env python3
# author: Gabriel Auger
# version: 5.0.7
# name: message
# license: MIT

import logging
import platform
import traceback
import inspect, sys, os

from ..gpkgs.format_text import ft

if platform.system() == "Windows":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

opts=dict(
    exit=None,
    trace=False,
)

def error(*msgs, **options ):
    print_message("error", *msgs, **options)
        
def success(*msgs, **options):
    print_message("success", *msgs, **options)

def warning(*msgs, **options):
    print_message("warning", *msgs, **options)

def info(*msgs, **options):
    print_message("info", *msgs, **options)

def dbg(funct, *msgs, **options):
    if not "debug" in options:
        options["debug"]=False

    if options["debug"] is True:
        globals()[funct](*msgs, **options)

def print_message(log_type, *msgs, **options):
    if platform.system() == "Windows":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    for key in opts:
        if key not in options:
            options.update({key:opts[key]})

    text=""
    if len(msgs) == 1:
        text=ft.log(log_type, "".join(msgs))
    else:
        for m, msg in enumerate(msgs):
            end_line="\n"
            if m+1 == len(msgs):
                end_line=""
            text+="{}{}".format(ft.log(log_type, msg), end_line)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(format="")

    if log_type == "error":
        logging.error(text)
    elif log_type == "info":
        print(text)
    elif log_type == "success":
        print(text)
    elif log_type == "warning":
        logging.warning(text)

    if options["trace"] is True:
        printed_trace=False
        if hasattr(traceback, 'print_stack'):
            printed_trace=True
            traceback.print_stack()

        if printed_trace is False:
            if hasattr(traceback, 'format_exc'):
                text=traceback.format_exc()
                if text is not None:
                    if text.strip() != "NoneType: None":
                        printed_trace=True
                        print(text)

        if printed_trace is False:
            print("No stack to print")

    if options["exit"] is not None:
        sys.exit(options["exit"])
    
