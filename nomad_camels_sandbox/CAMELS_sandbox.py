# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 15:03:22 2024

@author: Michael Krieger (lapmk)
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs

# import platform
from PySide6.QtCore import QThread

# from .digitaltwins import heater, diode, semiconductor_resistor, smu, dmm
from .digitaltwins import experiment

import time

# def is_arm():
#     try:
#         machine_type = platform.machine().lower()
#         if "arm" in machine_type or "aarch" in machine_type:
#             return True
#     except:
#         return False


class SandboxForCAMELS(BaseHTTPRequestHandler):
    # # Setup experiment
    # # arm = is_arm()
    # # heater1 = heater.heater("heater", simplephysics=arm)
    # # diode1 = diode.diode("diode", simplephysics=arm)
    # heater1 = heater.heater("heater")
    # diode1 = diode.diode("diode")
    # semiconductor_resistor1 = semiconductor_resistor.semiconductor_resistor('semiconductor_resistor')

    # # Setup instruments
    # smu1 = smu.smu("smu_heater", heater1)
    # dmm1 = dmm.dmm("dmm_pt1000", heater1)
    # smu2 = smu.smu("smu_sample", diode1)
    experiment1 = experiment.experiment("experiment")

    def log_message(self, format, *args):
        return

    def do_GET(self):
        global NPLC, U, R
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query, keep_blank_values=True)
        returnvalue = ""
        if len(params) == 0:
            returncode = 200
            returnvalue = "This is SandboxForCAMELS."
            # print("Send hello!")
        elif len(params) == 1:
            returncode = 400
            command = list(params.keys())[0]
            if "." in command:
                value = params[command][0]
                # print("Execute: " + command + " = " + value)

                result = SandboxForCAMELS.experiment1.execute_command(command, value)
                if result is not None:
                    if result[0] == True:
                        returncode = 200
                        if result[1] is not None:
                            returnvalue = str(result[1])

                # # Set experiment to current temperature
                # SandboxForCAMELS.diode1.set_temperature(
                #     SandboxForCAMELS.heater1.get_temperature()
                # )
                # # Execute commands
                # for instrument in [
                #     SandboxForCAMELS.smu1,
                #     SandboxForCAMELS.smu2,
                #     SandboxForCAMELS.dmm1,
                #     SandboxForCAMELS.heater1,
                #     SandboxForCAMELS.diode1,
                #     SandboxForCAMELS.semiconductor_resistor1
                # ]:
                #     result = instrument.execute_command(command, value)
                #     if result is not None:
                #         if result[0] == True:
                #             returncode = 200
                #             if result[1] is not None:
                #                 returnvalue = str(result[1])
        else:
            # print("Two many commands received; please send only one.")
            returncode = 400

        # if returncode == 200:
        #     if returnvalue != "":
        #         print("--> " + returnvalue + ", OK")
        #     else:
        #         print("--> OK")
        # else:
        #     print("--> Error")

        self.send_response(returncode)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(returnvalue, "utf-8"))


class ServerThread(QThread):
    def __init__(self, host, port):
        QThread.__init__(self)
        self.host = host
        self.port = port
        self.server = HTTPServer((self.host, self.port), SandboxForCAMELS)

    def run(self):
        print("This is SandboxForCAMELS.")
        print("Local server started http://%s:%s" % (self.host, self.port))
        # if is_arm():
        #     print("Running on ARM CPU, using simplified physics")
        self.server.serve_forever()

    def stop(self):
        # wait for 5 seconds to prevent errors if something still tries to connect
        time.sleep(5)
        self.server.shutdown()
        self.server.server_close()
        print("SandboxForCAMELS server stopped.")


class SandboxServer:
    def __init__(self, host, port):
        self.server_thread = ServerThread(host, port)
        self.n_using_instruments = 0

    def add_using_instrument(self):
        self.n_using_instruments += 1
        if self.n_using_instruments == 1:
            self.server_thread.start()

    def remove_using_instrument(self):
        self.n_using_instruments -= 1
        if self.n_using_instruments == 0:
            self.server_thread.stop()

    # def start(self):
    #     print("This is SandboxForCAMELS.")
    #     print("Local server started http://%s:%s" % (self.host, self.port))
    #     if is_arm():
    #         print("Running on ARM CPU, using simplified physics")
    #     # print("Press Ctrl-C to terminate")
    #     self.server_thread = threading.Thread(target=self.server.serve_forever)
    #     self.server_thread.start()

    # def stop(self):
    #     self.server.shutdown()
    #     self.server_thread.join()  # Wait for the server thread to finish
    #     self.server.server_close()
    #     print("SandboxForCAMELS server stopped.")
