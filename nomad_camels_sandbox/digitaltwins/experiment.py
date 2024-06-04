# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 17:45:38 2024

@author: Michael Krieger (lapmk)
"""

import json
from . import heater, diode, semiconductor_resistor, smu, dmm

all_experiments = ["diode_on_heater", "semiconductor_resistor_on_heater"]


class experiment:
    experiments = all_experiments

    def __init__(self, name: str, experiment: str = "diode_on_heater"):
        self.name = name
        self.experiment = experiment
        self.setup(experiment)

    def setup(self, experiment: str):
        self.experiment = experiment
        if experiment in self.experiments:
            func = getattr(self, "setup_" + experiment)
            func()
            return True
        else:
            return False

    def setup_diode_on_heater(self):
        heater1 = heater.heater("heater")
        diode1 = diode.diode("diode")
        self.objects = [
            heater1,
            diode1,
            smu.smu("smu_heater", heater1),
            dmm.dmm("dmm_pt1000", heater1),
            smu.smu("smu_diode", diode1),
        ]
        self.object_temperature_source = heater1
        self.object_samples = [diode1]

    def setup_semiconductor_resistor_on_heater(self):
        heater1 = heater.heater("heater")
        semiconductor_resistor1 = semiconductor_resistor.semiconductor_resistor(
            "semiconductor_resistor"
        )
        self.objects = [
            heater1,
            semiconductor_resistor1,
            smu.smu("smu_heater", heater1),
            dmm.dmm("dmm_pt1000", heater1),
            smu.smu("smu_sample", semiconductor_resistor1),
        ]
        self.object_temperature_source = heater1
        self.object_samples = [semiconductor_resistor1]

    def get_object(self, name: str):
        for obj in self.objects:
            if obj.name == name:
                return obj

    def set_temperature(self, temperature: float):
        for sample in self.object_samples:
            sample.set_temperature(temperature)

    def execute_command(self, command: str, value):
        if command.split(".")[0] == self.name:
            if command.split(".")[1] == "setup":
                if value == "":
                    return (True, self.experiment)
                else:
                    return (self.setup(value), None)
            elif command.split(".")[1] == "list_experiments":
                return (True, json.dumps(self.experiments))
            else:
                return (False, None)
        else:
            # Update temperatures of all samples
            # before any commands are executed
            if self.object_temperature_source is not None:
                self.set_temperature(self.object_temperature_source.get_temperature())

            # Execute commands of experiment parts
            for instrument in self.objects:
                result = instrument.execute_command(command, value)
                if result is not None:
                    break
            return result
