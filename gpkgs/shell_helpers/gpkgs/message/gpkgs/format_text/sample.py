#!/usr/bin/env python3
# author: Gabriel Auger
# version: 0.3.0
# name: format_text
# license: MIT

if __name__ == "__main__":
    import sys, os
    import importlib
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    print(module_name)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    pkg.ft.clear_screen()
    pkg.ft.clear_scrolling_history()

    print(pkg.ft.error("error message"))
    print(pkg.ft.info("info message"))
    print(pkg.ft.success("success message"))
    print(pkg.ft.warning("warning message"))

    print()

    print(pkg.ft.log("error", "error message as a known label"))
    print(pkg.ft.log("info", "info message as a known label"))
    print(pkg.ft.log("success", "success message as a known label"))
    print(pkg.ft.log("warning", "warning message as a known label"))

    print()
    for log_format in sorted(pkg.ft.get_logs()):
        print(pkg.ft.log(log_format, "log format as a dict"))

    print()
    for log_name in ["error", "info", "success", "warning"]:
        print(pkg.ft.log(log_name, "log format as a known label"))

    txt="color as a function"
    print(pkg.ft.black(txt))
    print(pkg.ft.red(txt))
    print(pkg.ft.green(txt))
    print(pkg.ft.brown(txt))
    print(pkg.ft.blue(txt))
    print(pkg.ft.magenta(txt))
    print(pkg.ft.cyan(txt))
    print(pkg.ft.lGray(txt))
    print(pkg.ft.dGray(txt))
    print(pkg.ft.lRed(txt))
    print(pkg.ft.lGreen(txt))
    print(pkg.ft.yellow(txt))
    print(pkg.ft.lBlue(txt))
    print(pkg.ft.lMagenta(txt))
    print(pkg.ft.lCyan(txt))
    print(pkg.ft.white(txt))
    txt="emphasize as a function"
    print(pkg.ft.uline(txt))
    print(pkg.ft.bold(txt))
    print(pkg.ft.iverse(txt))

    print()

    for color_name in sorted(pkg.ft.get_colors()):
        print(pkg.ft.color(color_name, "color as a dictionary key"))

    for mark_name in sorted(pkg.ft.get_marks()):
        print(pkg.ft.mark(mark_name, "emphasize as a dictionary key"))


