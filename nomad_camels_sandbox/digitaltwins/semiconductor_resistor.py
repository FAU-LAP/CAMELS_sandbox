# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 17:45:38 2024

@author: Michael Krieger (lapmk)
"""

import numpy as np
from scipy.constants import k, e


class semiconductor_resistor:
    def __init__(
        self,
        name: str,
        R0: float = 100,
        eps3: float = 0.045,
        temperature: float = 295
    ):
        self.name = name
        self.R0 = R0
        self.eps3 = eps3
        self.temperature = temperature
        self.voltage = 0
        self.current = 0

    def _calc_R(self):
        return self.R0 * np.exp(self.eps3 * e / k / self.temperature)

    def set_temperature(self, temperature: float):
        self.temperature = temperature

    def set_current(self, current: float):
        self.current = current

    def set_voltage(self, voltage: float):
        self.voltage = voltage

    def get_current(self, voltage=None):
        if voltage is None:
            voltage = self.voltage

        return voltage / self._calc_R()

    def get_voltage(self, current=None):
        if current is None:
            current = self.current

        return current * self._calc_R()
    
    
    def execute_command(self, command: str, value):
        return None
    


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    semiconductor_resistor1 = semiconductor_resistor('semiconductor_resistor')

    semiconductor_resistor1.set_temperature(295)

    dataU = np.linspace(-1, 1, 21)

    dataI = np.array([])
    for voltage in dataU:
        dataI = np.append(dataI, semiconductor_resistor1.get_current(voltage))

    fig, ax = plt.subplots()
    ax.set_xlabel("Voltage (V)")
    ax.set_ylabel("Current (A)", color="g")

    ax.plot(dataU, dataI, color="g")
