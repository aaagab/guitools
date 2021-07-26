#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.0.1
# name: timeout
# license: MIT

if __name__ == "__main__":
    import sys, os
    import importlib
    import time
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    timer=pkg.TimeOut(2).start()
    to_print=True
    while True:

        if timer.has_ended(pause=.001):
            print("Ended")
            break
        else:
            print(timer.elapsed_time)
            if timer.elapsed_time >= 1.995 and to_print:
                print("#### Almost ####")
                to_print=False

    print(timer.get_elapsed_time())
    print(timer.get_elapsed_time())

    timer.reset().start()
    time.sleep(1)
    print(timer.get_elapsed_time())
    print(timer.has_ended())
    timer.stop()
    time.sleep(1)
    timer.start()
    print(timer.get_elapsed_time())
    print(timer.has_ended())
