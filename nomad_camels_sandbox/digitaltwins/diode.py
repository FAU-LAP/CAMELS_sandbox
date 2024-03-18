# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 17:45:38 2024

@author: Michael Krieger (lapmk)
"""

import numpy as np
from scipy.constants import k, e
from scipy.optimize import fsolve


class diode:
    def __init__(
        self,
        name: str,
        I0: float = 3.40e11,
        Egap: float = 1.12,
        n: float = 2.0,
        Rs: float = 35,
        temperature: float = 295,
        simplephysics: bool = False
    ):
        self.name = name
        self.I0 = I0
        self.Egap = Egap
        self.n = n
        self.Rs = Rs
        self.temperature = temperature
        self.voltage = 0
        self.current = 0
        self.simplephysics = simplephysics

    def _calc_current(self, voltage: float, current: float):
        x = e * (voltage - self.Rs * current) / k / self.temperature / self.n
        if x > 20:
            return np.exp(np.log(self.I0) - e * self.Egap / k / self.temperature + x)
        elif x > 0:
            return np.exp(
                np.log(self.I0)
                - e * self.Egap / k / self.temperature
                + np.log(np.exp(x) - 1)
            )
        else:
            return (
                self.I0
                * np.exp(-e * self.Egap / k / self.temperature)
                * (np.exp(x) - 1)
            )

    def set_temperature(self, temperature: float):
        self.temperature = temperature

    def set_current(self, current: float):
        self.current = current

    def set_voltage(self, voltage: float):
        self.voltage = voltage

    def get_current(self, voltage=None):
        if voltage is None:
            voltage = self.voltage

        if self.Rs > 0 and not self.simplephysics:
            # more realistic model including serial resistance:
            # requires numerical solution of implicit equation
            func = lambda current: (self._calc_current(voltage, current) - current)
            if voltage < 0:
                current0 = 0
            else:
                current0 = voltage / 2 / self.Rs
            result = fsolve(func, current0)
            return result[0]
        else:
            # simple physics:
            # we neglect the serial resistance and simply calculate
            # the Shockley equation
            return self._calc_current(voltage, 0)

    def get_voltage(self, current=None):
        if current is None:
            current = self.current

        return (
            self.n
            * k
            * self.temperature
            / e
            * np.log(
                1 + current / self.I0 / np.exp(-e * self.Egap / k / self.temperature)
            )
            + self.Rs * current
        )
    
    
    def execute_command(self, command: str, value):
        command = command.split(".")
        if command[0] == self.name:
            if command[1] == "simplephysics":
                if value == "":
                    return (True, 1 if self.simplephysics else 0)
                elif value == "0":
                    self.simplephysics = False
                    return (True, None)
                elif value == "1":
                    self.simplephysics = True
                    return (True, None)
                else:
                    return (False, None)
            else:
                return (False, None)
        else:
            return None
    


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    diode1 = diode()

    diode1.set_temperature(295)

    dataU = np.linspace(-2, 4, 101)

    dataI = np.array([])
    for voltage in dataU:
        dataI = np.append(dataI, diode1.get_current(voltage))

    dataU2 = np.array([])
    for current in dataI:
        dataU2 = np.append(dataU2, diode1.get_voltage(current))

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Voltage (V)")
    ax1.set_ylabel("Current (A)", color="g")
    ax2 = ax1.twinx()
    ax2.set_ylabel("Current (A)", color="b")
    ax2.set_yscale("log")

    ax1.plot(dataU, dataI, color="g")
    mask = dataI != 0
    ax2.plot(dataU[mask], np.abs(dataI[mask]), color="b")
