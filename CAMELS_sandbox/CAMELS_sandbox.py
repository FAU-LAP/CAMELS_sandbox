# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 15:03:22 2024

@author: Michael Krieger (lapmk)
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs

from digitaltwins import heater, diode, smu, dmm


HOST = "localhost"
PORT = 8080


class SandboxForCAMELS(BaseHTTPRequestHandler):
    def do_GET(self):
        global NPLC, U, R
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query, keep_blank_values=True)
        returnvalue = ''
        if len(params) == 0:
            returncode = 200
            returnvalue = "This is SandboxForCAMELS."
            print("Send hello!")
        elif len(params) == 1:
            command = list(params.keys())[0]
            value = params[command][0]
            print('Execute: ' + command + ' = ' + value)
            returncode = 400
            # Set experiment to current temperature
            diode1.set_temperature(heater1.get_temperature())
            # Execute commands
            for instrument in [smu1, smu2, dmm1]:
                result = instrument.execute_command(command, value)
                if result is not None:
                    if result[0] == True:
                        returncode = 200
                        if result[1] is not None:
                            returnvalue = str(result[1])
        else:
            print('Two many commands received; please send only one.')
            returncode = 400
            
        if returncode == 200:
            if returnvalue != '':
                print('--> ' + returnvalue + ', OK')
            else:
                print('--> OK')
        else:
            print('--> Error')
            
        self.send_response(returncode)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(returnvalue, "utf-8"))
            

# Setup experiment
heater1 = heater.heater()
diode1 = diode.diode()

# Setup instruments
smu1 = smu.smu('smu_heater', heater1)
dmm1 = dmm.dmm('dmm_pt1000', heater1)
smu2 = smu.smu('smu_diode', diode1)


# Start server
webServer = HTTPServer((HOST, PORT), SandboxForCAMELS)
print("This is SandboxForCAMELS.")
print("Server started http://%s:%s" % (HOST, PORT))
print("Press Ctrl-C to terminate")

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")
