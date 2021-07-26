#!/usr/bin/env python3
# author: Gabriel Auger
# version: 3.0.0
# name: timeout
# license: MIT
import sys
import time

class TimeOut():
    def __init__(self, value, unit="seconds"):
        self.waiting_time=None
        self.reset(value, unit)

    def convert_to_seconds(self, value, unit):
        units=dict(
            days=86400,
            hours=3600,
            minutes=60,
            seconds=1,
            milliseconds=0.001,
            microseconds=0.000001,
            nanoseconds=0.000000001,
        )
        if not unit in units:
            print("unknown unit '{}'.".format(unit))
            print("unit must be in {}".format(sorted(units)))
            sys.exit(1)

        return value * units[unit]

    def start(self):
        if self.elapsed_time is None:
            self.start_time=time.time()
        else:
            self.start_time=time.time()-self.elapsed_time
        return self

    def stop(self):
        self.elapsed_time=self.get_elapsed_time()
        self.start_time=None

    def reset(self, value=None, unit="seconds"):
        if value is not None:
            self.unit=unit
            self.waiting_time=self.convert_to_seconds(value, unit)
        self.start_time=None
        self.elapsed_time=None
        return self

    def has_ended(self, pause=None):
        if self.start_time is None:
            print("Start time is None, timer needs to be started.")
            sys.exit(1)
        else:
            self.elapsed_time = self.get_elapsed_time()
            if self.elapsed_time >= self.waiting_time:
                return True
            else:
                if pause is not None:
                    time.sleep(pause)
                return False

    def get_elapsed_time(self):
        if self.start_time is None:
            return None
        else:
            return time.time() - self.start_time
