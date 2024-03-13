# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 15:03:22 2024

@author: Michael Krieger (lapmk)
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
import threading

from .digitaltwins import heater, diode, smu, dmm


class SandboxForCAMELS(BaseHTTPRequestHandler):
    # Setup experiment
    heater1 = heater.heater()
    diode1 = diode.diode()

    # Setup instruments
    smu1 = smu.smu("smu_heater", heater1)
    dmm1 = dmm.dmm("dmm_pt1000", heater1)
    smu2 = smu.smu("smu_diode", diode1)

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
            command = list(params.keys())[0]
            value = params[command][0]
            # print("Execute: " + command + " = " + value)
            returncode = 400
            # Set experiment to current temperature
            SandboxForCAMELS.diode1.set_temperature(
                SandboxForCAMELS.heater1.get_temperature()
            )
            # Execute commands
            for instrument in [
                SandboxForCAMELS.smu1,
                SandboxForCAMELS.smu2,
                SandboxForCAMELS.dmm1,
            ]:
                result = instrument.execute_command(command, value)
                if result is not None:
                    if result[0] == True:
                        returncode = 200
                        if result[1] is not None:
                            returnvalue = str(result[1])
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


class SandboxServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = HTTPServer((self.host, self.port), SandboxForCAMELS)
        self.n_using_instruments = 0

    def add_using_instrument(self):
        self.n_using_instruments += 1
        if self.n_using_instruments == 1:
            self.start()

    def remove_using_instrument(self):
        self.n_using_instruments -= 1
        if self.n_using_instruments == 0:
            self.stop()

    def start(self):
        print("This is SandboxForCAMELS.")
        print("Server started http://%s:%s" % (self.host, self.port))
        print("Press Ctrl-C to terminate")
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server_thread.join()  # Wait for the server thread to finish
        self.server.server_close()
        print("Server stopped.")
