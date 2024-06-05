# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:11:55 2024

@author: Michael Krieger (lapmk)
"""

import time
import numpy as np


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


class dmm:
    def __init__(self, name: str, connecteddevice):
        self.name = name
        self.device = connecteddevice
        self.NPLC = 10

    def get_voltage(self):
        time.sleep(self.NPLC * 0.02)
        return self.device.get_voltage() + np.random.normal(0, 0.001 / self.NPLC)

    def get_current(self):
        time.sleep(self.NPLC * 0.02)
        return self.device.get_current() + np.random.normal(0, 0.001 / self.NPLC)

    def get_resistance(self):
        time.sleep(self.NPLC * 0.02)
        return self.device.get_resistance() + np.random.normal(0, 0.01 / self.NPLC)

    def set_nplc(self, value):
        self.NPLC = value

    def execute_command(self, command: str, value):
        command = command.split(".")
        if command[0] == self.name:
            if command[1] == "U":
                if value == "":
                    return (True, self.get_voltage())
                else:
                    return (False, None)
            elif command[1] == "I":
                if value == "":
                    return (True, self.get_current())
                else:
                    return (False, None)
            elif command[1] == "R":
                if value == "":
                    return (True, self.get_resistance())
                else:
                    return (False, None)
            elif command[1] == "NPLC":
                if value == "":
                    return (True, self.NPLC)
                elif is_float(value):
                    self.set_nplc(float(value))
                    return (True, None)
                else:
                    return (False, None)
            else:
                return (False, None)
        else:
            return None
