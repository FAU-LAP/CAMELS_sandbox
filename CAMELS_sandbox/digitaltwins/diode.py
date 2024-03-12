# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 17:45:38 2024

@author: Michael Krieger (lapmk)
"""

import numpy as np
from scipy.constants import k, e
from scipy.optimize import fsolve

class diode:
    def __init__(self, I0: float=5.77e-10, Egap: float=1.12, n: float=1., 
                 Rs:float = 0.1, temperature: float=295):
        self.I0 = I0
        self.Egap = Egap
        self.n = n
        self.Rs = Rs
        self.temperature = temperature
        self.voltage = 0
        self.current = 0
        
    
    def _calc_current(self, voltage: float, current: float):
        return (self.I0 * np.exp(-e * self.Egap / k / self.temperature) *
                (np.exp(e * (voltage - self.Rs * current) / 
                        k / self.temperature / self.n) - 1))
    
        
    def set_temperature(self, temperature: float):
        self.temperature = temperature
    

    def set_current(self, current: float):
        self.current = current


    def set_voltage(self, voltage: float):
        self.voltage = voltage

    
    def get_current(self, voltage=None):
        if voltage is None:
            voltage = self.voltage
            
        func = lambda current: self._calc_current(voltage, current)
        result = fsolve(func, 0)
        return result[0]
    
    
    def get_voltage(self, current=None):
        if current is None:
            current = self.current
            
        func = lambda voltage: self._calc_current(voltage, current)
        result = fsolve(func, 0)
        return result[0]
