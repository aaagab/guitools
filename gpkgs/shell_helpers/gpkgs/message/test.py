#!/usr/bin/env python3
# author: Gabriel Auger
# version: 5.0.7
# name: message
# license: MIT

if __name__ == "__main__":
    import sys, os
    import importlib
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    msg = importlib.import_module(module_name)
    del sys.path[0]

    msg.ft.clear_scrolling_history()
    print("scrolling history has been erased")

    msg.ft.clear_screen()
    print("screen has been cleared")

    msg.info("This is a single line info")
    print()
    msg.info(
        "This is a multiline info",
        "This is a multiline info",
        "This is a multiline info"
        )
    print()
    msg.warning("This is a single line warning")
    print()
    msg.warning(
        "This is a multiline line warning",
        "This is a multiline line warning",
        "This is a multiline line warning"
        )
    print()

    msg.success("This is a single line success")
    print()
    msg.success(
        "This is a multiline line success",
        "This is a multiline line success",
        "This is a multiline line success"
        )
    print()

    msg.error("This is a single line error")
    print()
    msg.error(
        "This is a multiline error",
        "This is a multiline error",
        "This is a multiline error",
        )
    print()
    msg.error("This is a single error with traceback", trace=True)
    print()
    msg.error(
        "This is a multiline user error with traceback",
        "This is a multiline user error with traceback",
        "This is a multiline user error with traceback",
        trace=True
        )
    print()

    msg.dbg("info", "This is a debug info message", debug=True)
    msg.dbg("success", "This is a debug success, debug can apply to any msg type", debug=True)

    print()
    text="You can create custom messages too"
    print(msg.ft.lGreen("  @@@@ ")+msg.ft.bold(text)+msg.ft.lGreen(" @@@@"))
    print()
    ldeco="### "
    rdeco=""
    tmp_str=ldeco+text+rdeco;
    print("  "+msg.ft.lBlue(ldeco)+msg.ft.bold(text)+msg.ft.lCyan(rdeco))
    print()

    msg.error("This is an error with stack trace and system exit with code 1", code=1, trace=True)
