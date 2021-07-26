#!/usr/bin/env python3
from pprint import pprint
import os
import platform
import re
import sys
import traceback

if platform.system() == "Windows":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def error(
    msgs, 
    exit=None,
    heredoc=False,
    prefix=None,
    pretty=True,
    keys=[],
    trace=False,
):
    print_message(
        "error",
        msgs,
        exit=exit,
        heredoc=heredoc,
        prefix=prefix,
        pretty=pretty,
        keys=keys,
        trace=trace,
    )

def info(
    msgs, 
    exit=None,
    heredoc=False,
    prefix=None,
    pretty=True,
    keys=[],
    trace=False,
):
    print_message(
        "info",
        msgs,
        exit=exit,
        heredoc=heredoc,
        prefix=prefix,
        pretty=pretty,
        keys=keys,
        trace=trace,
    ) 

def success(
    msgs, 
    exit=None,
    heredoc=False,
    prefix=None,
    pretty=True,
    keys=[],
    trace=False,
):
    print_message(
        "success",
        msgs,
        exit=exit,
        heredoc=heredoc,
        prefix=prefix,
        pretty=pretty,
        keys=keys,
        trace=trace,
    )

def warning(
    msgs, 
    exit=None,
    heredoc=False,
    prefix=None,
    pretty=True,
    keys=[],
    trace=False,
):
    print_message(
        "warning",
        msgs,
        exit=exit,
        heredoc=heredoc,
        prefix=prefix,
        pretty=pretty,
        keys=keys,
        trace=trace,
    )

def clear(scroll=False):
    if scroll is False:
        print("\x1b[2J\x1b[H", end="")
    else:
        print("\x1b[2J\x1b[H\x1b[3J", end="")

def get_heredoc(text, indent=0, prefix=None):
    first_line=True
    main_indent=0
    lines=[]
    text_lines=text.splitlines()
    for l, line in enumerate(text_lines):
        if l == len(text_lines) - 1:
            if line.strip() != "":
                lines.append("{}{}".format(indent*" ", line[main_indent:]))
        else:
            if first_line is True:
                if line.strip() != "":
                    first_line=False
                    main_indent=len(line)-len(line.lstrip())
                    if prefix is None:
                        lines.append("{}{}".format(indent*" ", line.lstrip()))
                    else:
                        lines.append("{}{}: {}".format(indent*" ", prefix, line.lstrip()))
            else:
                lines.append("{}{}".format(indent*" ", line[main_indent:]))
    return "\n".join(lines)

def print_message(msg_type, 
    msgs, 
    exit=None,
    heredoc=False,
    prefix=None,
    pretty=True,
    keys=[],
    trace=False,
):
    if sys.stdout.isatty() is False:
        pretty=False

    log_msgs=[]
    indent=2
    if isinstance(msgs, str):
        msgs=[msgs]
    for msg in msgs:
        tmp_msg=None
        if heredoc is True:
            if pretty is True:
                if prefix is None:
                    tmp_msg=get_heredoc(msg, indent=indent+2)
                else:
                    tmp_msg=get_heredoc(msg, indent=indent+2, prefix=prefix)
                    prefix=None
            else:
                if prefix is None:
                    tmp_msg=get_heredoc(msg)
                else:
                    tmp_msg=get_heredoc(msg, prefix=prefix)
                    prefix=None
        else:
            if prefix is None:
                tmp_msg=msg
            else:
                tmp_msg="{}: {}".format(prefix, msg)
                prefix=None
        log_msgs.append(tmp_msg)

    if pretty is True:
        bullet=None
        if msg_type == "error":
            bullet="\x1b[1m\x1b[91m\u00D7\x1b[39m\x1b[22m"
        elif msg_type == "info":
            bullet="\x1b[1m\x1b[96m*\x1b[39m\x1b[22m"
        elif msg_type == "success":
            bullet="\x1b[1m\x1b[92m\u221A\x1b[39m\x1b[22m"
        elif msg_type == "warning":
            bullet="\x1b[1m\x1b[93m\u2206\x1b[39m\x1b[22m"

    print_msgs=[]
    first_line=True
    for msg in log_msgs:
        if pretty is True:
            tmp_indent=" "
            if heredoc is True:
                msg=msg[indent+1:]
                tmp_indent=""
            if msg_type == "error":
                msg="\x1b[91m{}\x1b[39m".format(msg)
            line_start=(indent+1)*" "
            if first_line is True:
                first_line=False
                line_start="{}{}".format(indent*" ", bullet)
            tmp_msg="{}{}{}".format(line_start, tmp_indent, msg)

            print_msgs.append(tmp_msg)
        else:
            print_msgs.append(msg)

    print_msgs="\n".join(print_msgs)
    if pretty is True:
        print_msgs="\x1b[0m{}".format(print_msgs)

    if len(keys) > 0:
        if isinstance(keys, list):
            print_msgs=print_msgs.format(*keys)
        elif isinstance(keys, dict):
            print_msgs=print_msgs.format(**keys)
    
    printed_stack=None
    if trace is True:
        print_msgs="STACK TRACE:\n{}".format("".join(traceback.format_stack()[:-2]))+print_msgs

    prefix_type=""
    if pretty is False:
        if msg_type == "error":
            prefix_type="ERROR: "
        elif msg_type == "info":
            prefix_type="INFO: "
        elif msg_type == "success":
            prefix_type="SUCCESS: "
        elif msg_type == "warning":
            prefix_type="WARNING: "

    if msg_type in ["error", "warning"]:
        print("{}{}".format(prefix_type, print_msgs), file=sys.stderr)
    else:
        print("{}{}".format(prefix_type, print_msgs))

    if exit is not None:
        sys.exit(exit)
