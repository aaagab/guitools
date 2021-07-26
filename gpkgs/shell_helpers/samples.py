#!/usr/bin/env python3
# author: Gabriel Auger
# version: 5.4.1
# name: shell_helpers
# license: MIT

import sys, os
import importlib
direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, direpa_script_parent)
shell = importlib.import_module(module_name)
del sys.path[0]

cmd='echo "assembly_language"'

shell.msg.info("execute command '{}' WITH output.".format(cmd))
shell.cmd(cmd)
print()

shell.msg.info("execute command '{}' WITHOUT output.".format(cmd))
shell.cmd_devnull(cmd)
print()

shell.msg.info("command returns exit code '{}'".format(cmd))
print(shell.cmd_devnull(cmd))
print()

shell.msg.info("get command '{}' output in variable.".format(cmd))
output=shell.cmd_get_value(cmd)
print(output)
print()

shell.msg.info("verbose command '{}' mode.".format(cmd))
shell.cmd_prompt(cmd, info=True)
print()

cmd=[
    "echo",
    "'assembly_language'"
]

shell.msg.info("verbose list command '{}' mode.".format(cmd))
shell.cmd_prompt(cmd, info=True)
print()
