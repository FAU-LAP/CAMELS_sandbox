# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 12:09:31 2024

@author: mpap00kp
"""

from datetime import datetime
import scipy.constants as constants
from scipy import integrate
from . import peltierelement
from . import ptxxxx


class heater:
    # The heater is an aluminum block mounted on top of a peltier element.
    # Thermometer (PT1000) and DUT are in thermal contact to the block.
    # The other side of the peltier element is coupled to a larger
    # heat reservoir.

    # block parameters (assumption: thickness << length, width)
    area: float = 1.44e-4  # m^2
    thickness: float = 3e-3  # m
    emissivity = 0.04  # (Aluminium)
    specific_heat_capacity = 900  # J/kg/K (Aluminium)
    density = 2.7e3  # kg/m^3 (Aluminium)

    # convection
    heat_transfer_coefficient: float = 10  # W/m^2/K

    def _calc_convection_heatpower(self, temperature: float):
        return (
            self.heat_transfer_coefficient
            * self.area
            * (self.temperature_environment - temperature)
        )

    def _calc_radiation_heatpower(self, temperature: float):
        return (
            self.emissivity
            * constants.sigma
            * self.area
            * (self.temperature_environment**4 - temperature**4)
        )

    def _calc_total_heatpower(
        self,
    ):
        return (
            self.tec.heatpower(
                self.current, self.temperature, self.temperature_environment
            )
            + self._calc_convection_heatpower(self.temperature)
            + self._calc_radiation_heatpower(self.temperature)
        )

    def _calc_temperature_change(self):
        c = self.specific_heat_capacity
        m = self.area * self.thickness * self.density
        Te = self.temperature_environment
        t1 = (datetime.now() - self.lastchange).total_seconds()
        f = lambda temp, t: (
            (
                self.tec.heatpower(self.current, temp, Te)
                + self._calc_convection_heatpower(temp)
                + self._calc_radiation_heatpower(temp)
            )
            / c
            / m
        )
        result = integrate.odeint(f, self.temperatureatchange, [0, t1])
        return result

    def __init__(self, temperature_environment: float = 295):
        # init values
        self.temperature_environment = temperature_environment
        self.temperature = temperature_environment
        self.current = 0
        self.lastchange = datetime.now()
        self.temperatureatchange = temperature_environment
        # init peltier element (thermoelectric cooler = TEC)
        self.tec = peltierelement.peltierelement()
        # init pt1000
        self.pt1000 = ptxxxx.ptxxxx(1000)

    def set_current(self, current: float = 0):
        self.temperatureatchange = self.get_temperature()
        self.lastchange = datetime.now()
        self.current = current

    def get_temperature(self):
        deltaT = self._calc_temperature_change()
        self.temperature = deltaT[1, 0]
        return self.temperature

    def get_resistance(self):
        return self.pt1000.get_resistance(self.get_temperature())


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import time

    ht = heater()

    starttime = datetime.now()
    times = [0]
    temps = [ht.temperature]

    fig, ax = plt.subplots()

    i = 0

    while True:
        t = (datetime.now() - starttime).total_seconds()
        T = ht.get_temperature()
        # print(t, T, ht.get_pt1000resistance(),
        #       ht.tec.heatpower(ht.current, ht.temperature, ht.temperature_environment),
        #       ht._calc_convection_heatpower(ht.temperature),
        #       ht._calc_radiation_heatpower(ht.temperature))
        times.append(t)
        temps.append(T)

        ax.clear()
        ax.plot(times, temps)
        fig.canvas.draw()
        fig.canvas.flush_events()

        i = i + 1
        if i == 15:
            ht.set_current(1)

        if i == 900:
            ht.set_current(0.5)

        if i == 1800:
            ht.set_current(0)

        time.sleep(0.2)
