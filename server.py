# from flask import Flask, request, jsonify
import omnipyrig
# import threading

# lock = threading.Lock()

# app = Flask(__name__)

# # Define available modes
# available_modes = ['USB', 'CW', 'LSB']

# global client

# def getOmnirig():
#     print("starting")
#     omniClient = omnipyrig.OmniRigWrapper()
#     print("set rig")
#     omniClient.setActiveRig(1)
#     print(omniClient.getParam("RigType"))
#     return omniClient
# client = getOmnirig()
# # app.config['omnirigclient'] = getOmnirig()

# @app.route('/mode/', methods=['GET'])
# def set_mode():
#     with lock:
#         # client = app.config['omnirigclient']
#         active_mode = client.getParam("RigType")
#         mode = request.args.get('set')
#         if mode is None:
#             return jsonify({"active_mode": active_mode})
        
#         mode = mode.upper()
#         if mode in available_modes:
#             return jsonify({"mode": mode, "status": "success"})
#         else:
#             return jsonify({"error": f"Invalid mode. Available modes are: {available_modes}"})

# if __name__ == '__main__':
#     app.run(debug=True,use_reloader=False)

from http.server import BaseHTTPRequestHandler, HTTPServer
from omnirignew import OmniRigWrapper

PORT = 5001

def getOmnirig():
    client = OmniRigWrapper()
    client.setActiveRig(1)
    print(client.getParam("RigType"))
    return client

global omniClient
omniClient = getOmnirig()

class RigCommand():

    @staticmethod
    def setMode(mode):
        omniClient.setMode(mode)

    @staticmethod
    def toggleSplit():
        split = omniClient.getParam("Split")
        if split == omniClient.SPLIT_OFF:
            omniClient.setSplit(omniClient.SPLIT_ON)
        elif split == omniClient.SPLIT_ON:
            omniClient.setSplit(omniClient.SPLIT_OFF)

    @staticmethod
    def setSplit(splitValue):
        currentFreq = omniClient.getParam("Freq")
        currentVfo = omniClient.getParam("Vfo")
        if currentVfo == omniClient.VF
        
        

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            rig = omniClient.getParam("RigType")
            test="12"
            print("trying get mode")
            mode = "test"
            mode = omniClient.getParam("Mode")
            print(mode)
            # Freq =      omniClient.getParam("Freq")
            # print(frequency)
            self.wfile.write(b'Hello, !' + mode.encode('utf-8'))
            self.wfile.write(b'\nHello, !' + rig.encode('utf-8'))
        elif self.path == '/mode/cw':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            # omniClient.setMode(omniClient.MODE_CW_U)
            RigCommand.setMode(omniClient.CW_U)
            
            self.wfile.write(b'mode CW set')
        elif self.path == '/mode/usb':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            RigCommand.setMode(omniClient.MODE_SSB_U)
            
        elif self.path == '/mode/lsb':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            RigCommand.setMode(omniClient.MODE_SSB_L)
            
        elif self.path == '/mode/split':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            RigCommand.toggleSplit()
        
        elif self.path == '/mode/split/1':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            RigCommand.setSplit(1)
            
        else:
            self.send_error(404, 'File not found')

# def run_server():
#     server_address = ('', PORT)
#     httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
#     print(f"Serving on port {PORT}")
#     httpd.serve_forever()

# if __name__ == '__main__':
#     run_server()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        httpd.server_close()
        print("Server closed.")

if __name__ == '__main__':
    run_server()
