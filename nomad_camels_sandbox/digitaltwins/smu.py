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


class smu:
    def __init__(self, name: str, connecteddevice):
        self.name = name
        self.device = connecteddevice
        self.sourcemode = "V"
        self.voltage = 0
        self.current = 0
        self.NPLC = 10
        self.compliance = 1

    def set_voltage(self, voltage: float):
        self.voltage = voltage
        self.sourcemode = "V"
        self.device.set_voltage(voltage)

    def set_current(self, current: float):
        self.current = current
        self.sourcemode = "I"
        self.device.set_current(current)

    def get_voltage(self):
        time.sleep(self.NPLC * 0.02)
        if self.sourcemode == "V":
            return self.voltage
        else:
            voltage = self.device.get_voltage()
            for m_ran in [1e-3, 1e-2, 1e-1, 1, 10]:
                if np.abs(voltage) < m_ran:
                    voltage += np.random.normal(0, m_ran * 1e-3 / self.NPLC)
                    break
            if voltage > self.compliance:
                return self.compliance
            else:
                return voltage

    def get_current(self):
        time.sleep(self.NPLC * 0.02)
        if self.sourcemode == "I":
            return self.current
        else:
            current = self.device.get_current()
            for m_ran in [1e-3, 1e-2, 1e-1, 1, 10]:
                if np.abs(current) < m_ran:
                    current += np.random.normal(0, m_ran * 1e-3 / self.NPLC)
                    break
            if current > self.compliance:
                return self.compliance
            else:
                return current

    def execute_command(self, command: str, value):
        command = command.split(".")
        if command[0] == self.name:
            if command[1] == "U":
                if value == "":
                    return (True, self.get_voltage())
                elif is_float(value):
                    self.set_voltage(float(value))
                    return (True, None)
                else:
                    return (False, None)
            elif command[1] == "I":
                if value == "":
                    return (True, self.get_current())
                elif is_float(value):
                    self.set_current(float(value))
                    return (True, None)
                else:
                    return (False, None)
            elif command[1] == "NPLC":
                if value == "":
                    return (True, self.NPLC)
                elif is_float(value):
                    self.NPLC = float(value)
                    return (True, None)
                else:
                    return (False, None)
            elif command[1] == "COMPL":
                if value == "":
                    return (True, self.compliance)
                elif is_float(value):
                    self.compliance = float(value)
                    return (True, None)
                else:
                    return (False, None)
            else:
                return (False, None)
        else:
            return None
