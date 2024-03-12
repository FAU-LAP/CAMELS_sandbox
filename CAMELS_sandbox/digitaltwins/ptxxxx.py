# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 16:55:33 2024

@author: Michael Krieger (lapmk)
"""

from scipy.optimize import fsolve

class ptxxxx:
    a: float = 3.9083e-3
    b: float = -5.775e-7
    c: float = -4.183e-12
    
    
    def __init__(self, R0: float=100, temperature: float=295):
        self.R0 = R0
        self.temperature = temperature
    
    
    def set_temperature(self, temperature: float):
        self.temperature = temperature
    
                  
    def get_resistance(self, temperature=None):
        if temperature is None:
            degc = self.temperature - 273.15
        else:
            degc = temperature - 273.15
            
        resist = self.R0 * (1 + self.a * degc + self.b * (degc**2))
        
        if degc >= 0:
            return resist
        else:
            return resist + self.c * (degc - 100) * (degc**3)

        
    def get_temperature(self, resistance: float):
        func = lambda temp: self.get_resistance(temp) - resistance
        result = fsolve(func, 295)
        return result[0]
        

if __name__ == '__main__':
    pt1000 = ptxxxx(1000)
