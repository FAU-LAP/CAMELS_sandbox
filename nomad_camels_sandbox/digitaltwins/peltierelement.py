# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 13:13:29 2024

@author: Michael Krieger (lapmk)
"""

import numpy as np


class peltierelement:
    # default values for QC-17-1.0-2.5AS
    peltier_current_max: float = 2.8                # A
    peltier_voltage_max: float = 1.9                # V
    peltier_delta_temp_max: float = 72              # K
    peltier_temp_hot: float = 298.15                # K
    peltier_power_max: float = 3.2                  # W
    
    
    def heatpower(self, current: float, 
                        temperature_a: float, temperature_e: float):
        # Model adapted from:
        # Simon, Lineykin, Sam Ben-Yaakov, Modeling and Analysis of 
        # Thermoelectric Modules, IEEE Transactions on Industry Applications
        # (2007), DOI: 10.1109/TIA.2006.889813
        #
        # with Ta = temperature_a and Te = temperature_e and I = current:
        # heat power cold side:
        #   qa = (Te - Ta) / theta_m + alpha_m * Ta * I + (I**2) * R_m / 2
        # heat power hot side:
        #   qe = -(Te - Ta) / theta_m - alpha_m * Te * I + (I**2) * R_m / 2
        #
        # operation as thermoelectric cooler (TEC):
        # temperature_a: cold side
        # temperature_e: hot side
        # current < 0
        # ==> heatpower = qa < 0 (heat removed from cold side)
        
        return ((temperature_e - temperature_a) / self.theta_m +
                self.alpha_m * temperature_a * current +
                (current**2) * self.R_m / 2)
    
    
    def heatpower_coefficients(self, current: float, temperature_e: float):
        c0 = temperature_e / self.theta_m + (current**2) * self.R_m / 2
        c1 = self.alpha_m * current - 1 / self.theta_m
        return (c0, c1)


    def _init_parameters(self, Th: float, dTmax: float, Umax: float, Imax: float, qamax: float):
        # calculation of model parameters from datasheet values
        self.alpha_m = (Umax * Imax + 2 * qamax) / ((2 * Th + dTmax) * Imax)
        self.theta_m = dTmax / (qamax - self.alpha_m * dTmax * Imax)
        self.R_m = 2 * (self.alpha_m * Th * Imax - qamax) / (Imax**2)

    
    def __init__(self):
        # init peltier model parameters
        self._init_parameters(self.peltier_temp_hot, 
                             self.peltier_delta_temp_max,
                             self.peltier_voltage_max,
                             self.peltier_current_max,
                             self.peltier_power_max)
        

# For testing, plot the qa-I diagrams of the peltier module 
# for Te = 25°C and Te = 50°C as shown in the datasheet of QC-17-1.0-2.5AS
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    
    ph = peltierelement()
    deltaT = np.linspace(-90, 0, 101)
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10,5))
    
    for i in [0, 1]:
        ax[i].set_ylim([0, 4])
        ax[i].set_title(['T = 25°C', 'T = 50°C'][i])
        
    for current in [0.6, 1.1, 1.7, 2.2, 2.8]:
        ax[0].plot(deltaT, -ph.heatpower(-current, 298.15 + deltaT, 298.15))    
        ax[1].plot(deltaT, -ph.heatpower(-current, 323.15 + deltaT, 323.15))    
