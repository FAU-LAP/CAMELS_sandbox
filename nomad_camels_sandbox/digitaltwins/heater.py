# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 12:09:31 2024

@author: mpap00kp
"""

from datetime import datetime
import numpy as np
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
    
    
    def _calc_convection_heatpower_coefficients(self):
        c = self.heat_transfer_coefficient * self.area
        return (c * self.temperature_environment, -c)


    def _calc_radiation_heatpower(self, temperature: float):
        return (
            self.emissivity
            * constants.sigma
            * self.area
            * (self.temperature_environment**4 - temperature**4)
        )
    

    def _calc_temperature_change(self):
        c = self.specific_heat_capacity
        m = self.area * self.thickness * self.density
        Te = self.temperature_environment
        t1 = (datetime.now() - self.lastchange).total_seconds()
        if not self.simplephysics:
            # more realistic model:
            # involves numerical solution of differential equation
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
            result = result[1, 0]
        else:
            # simple physics:
            # we neglect heat radiation and solve the differential equation
            # analytically
            c_tec = self.tec.heatpower_coefficients(self.current, Te)
            c_conv = self._calc_convection_heatpower_coefficients()
            a = (c_tec[1] + c_conv[1]) / c / m
            b = (c_tec[0] + c_conv[0]) / c / m
            result = ((self.temperatureatchange + b / a) * np.exp(a * t1) 
                      - b / a)
        return result
    

    def __init__(self, name: str, temperature_environment: float = 295,
                 simplephysics: bool = False):
        # init values
        self.name = name
        self.simplephysics = simplephysics
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
        self.temperature = self._calc_temperature_change()
        return self.temperature


    def get_resistance(self):
        return self.pt1000.get_resistance(self.get_temperature())
    
    
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
