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

# Częstotliwości dla pasm krótkofalarskich (w Hz)
HAM_BANDS = {
    '160m': {
        'FT8': 1840000,
        'CW': 1800000,
        'SSB': 1830000
    },
    '80m': {
        'FT8': 3573000,
        'CW': 3500000,
        'SSB': 3600000
    },
    '40m': {
        'FT8': 7074000,
        'CW': 7000000,
        'SSB': 7200000
    },
    '30m': {
        'FT8': 10136000,
        'CW': 10100000,
        'SSB': 10100000
    },
    '20m': {
        'FT8': 14074000,
        'CW': 14000000,
        'SSB': 14200000
    },
    '17m': {
        'FT8': 18100000,
        'CW': 18068000,
        'SSB': 18168000
    },
    '15m': {
        'FT8': 21074000,
        'CW': 21000000,
        'SSB': 21200000
    },
    '12m': {
        'FT8': 24915000,
        'CW': 24890000,
        'SSB': 24990000
    },
    '10m': {
        'FT8': 28074000,
        'CW': 28000000,
        'SSB': 28500000
    },
    '6m': {
        'FT8': 5074000,
        'CW': 5000000,
        'SSB': 5200000
    }
}

# Kolejność pasm od najniższego do najwyższego
BAND_ORDER = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m']

PORT = 5973

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
        # Konwertuj splitValue z MHz na Hz i dodaj do aktualnej częstotliwości
        newFreq = currentFreq + (splitValue * 1000000)
        
        if currentVfo == omniClient.VFO_A:
            omniClient.setFrequency(omniClient.VFO_B, newFreq)
        elif currentVfo == omniClient.VFO_B:
            omniClient.setFrequency(omniClient.VFO_A, newFreq)
    
    @staticmethod
    def setFrequency(frequency):
        """Ustawia częstotliwość na aktualnym VFO"""
        omniClient.setFrequency(omniClient.getParam("Vfo"), frequency)
    
    @staticmethod
    def getBandFromFrequency(frequency):
        """Określa pasmo na podstawie częstotliwości"""
        # Definicja zakresów pasm (w Hz)
        band_ranges = {
            '160m': (1800000, 2000000),
            '80m': (3500000, 4000000),
            '40m': (7000000, 7300000),
            '30m': (10100000, 10150000),
            '20m': (14000000, 14350000),
            '17m': (18068000, 18168000),
            '15m': (21000000, 21450000),
            '12m': (24890000, 24990000),
            '10m': (28000000, 29700000),
            '6m': (5000000, 5400000)
        }
        
        for band, (min_freq, max_freq) in band_ranges.items():
            if min_freq <= frequency <= max_freq:
                return band
        return None


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    # Słownik do przechowywania endpointów
    _endpoints = {}
    
    @classmethod
    def route(cls, path, methods=None):
        """Dekorator do rejestracji endpointów"""
        if methods is None:
            methods = ['GET']
        
        def decorator(func):
            if path not in cls._endpoints:
                cls._endpoints[path] = {}
            for method in methods:
                cls._endpoints[path][method] = func
            return func
        return decorator
    
    @classmethod
    def route_startswith(cls, path_prefix, methods=None):
        """Dekorator do rejestracji endpointów z startswith"""
        if methods is None:
            methods = ['GET']
        
        def decorator(func):
            if path_prefix not in cls._endpoints:
                cls._endpoints[path_prefix] = {}
            cls._endpoints[path_prefix]['_startswith'] = True
            for method in methods:
                cls._endpoints[path_prefix][method] = func
            return func
        return decorator
    
    def send_text_response(self, message):
        """Wysyła odpowiedź tekstową z kodem 200"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))
    
    def send_error_response(self, code, message):
        """Wysyła odpowiedź błędu"""
        self.send_error(code, message)
    
    def handle_request(self):
        """Obsługuje żądanie HTTP na podstawie zarejestrowanych endpointów"""
        method = self.command
        path = self.path
        
        # Sprawdź dokładne dopasowanie
        if path in self._endpoints and method in self._endpoints[path]:
            handler = self._endpoints[path][method]
            return handler(self)
        
        # Sprawdź startswith
        for prefix, handlers in self._endpoints.items():
            if '_startswith' in handlers and path.startswith(prefix):
                if method in handlers:
                    handler = handlers[method]
                    return handler(self)
        
        # Brak dopasowania
        self.send_error_response(404, 'File not found')
    
    def do_GET(self):
        """Obsługuje żądania GET"""
        self.handle_request()

# Endpointy
@SimpleHTTPRequestHandler.route('/')
def get_rig_info(self):
    """Zwraca informacje o aktualnym trybie i typie odbiornika"""
    rig = omniClient.getParam("RigType")
    print("trying get mode")
    mode = omniClient.getParam("Mode")
    print(mode)
    response = f'Hello, !{mode}\nHello, !{rig}'
    self.send_text_response(response)

@SimpleHTTPRequestHandler.route('/mode/cw')
def set_cw_mode(self):
    """Ustawia tryb CW"""
    RigCommand.setMode(omniClient.CW_U)
    self.send_text_response('mode CW set')

@SimpleHTTPRequestHandler.route('/mode/usb')
def set_usb_mode(self):
    """Ustawia tryb USB"""
    RigCommand.setMode(omniClient.MODE_SSB_U)
    self.send_text_response('mode USB set')

@SimpleHTTPRequestHandler.route('/mode/lsb')
def set_lsb_mode(self):
    """Ustawia tryb LSB"""
    RigCommand.setMode(omniClient.MODE_SSB_L)
    self.send_text_response('mode LSB set')

@SimpleHTTPRequestHandler.route('/mode/split')
def toggle_split(self):
    """Przełącza split ON/OFF"""
    RigCommand.toggleSplit()
    self.send_text_response('split toggled')

@SimpleHTTPRequestHandler.route_startswith('/mode/split/')
def set_split_value(self):
    """Ustawia split na określoną wartość w MHz"""
    try:
        splitValue = float(self.path.split('/')[-1])
        RigCommand.setSplit(splitValue)
        self.send_text_response(f'split {splitValue}MHz set')
    except ValueError:
        self.send_error_response(400, 'Invalid split value')

@SimpleHTTPRequestHandler.route_startswith('/mode/ft8/')
def set_ft8_mode(self):
    """Ustawia tryb USB + częstotliwość FT8 dla danego pasma"""
    try:
        band = self.path.split('/')[-1]
        if band in HAM_BANDS:
            # Ustaw tryb USB
            RigCommand.setMode(omniClient.MODE_SSB_U)
            # Ustaw częstotliwość FT8 dla danego pasma
            ft8_freq = HAM_BANDS[band]['FT8']
            RigCommand.setFrequency(ft8_freq)
            
            self.send_text_response(f'FT8 mode set for {band} at {ft8_freq}Hz')
        else:
            self.send_error_response(400, f'Invalid band. Available bands: {list(HAM_BANDS.keys())}')
    except Exception as e:
        self.send_error_response(500, f'Error setting FT8 mode: {str(e)}')

@SimpleHTTPRequestHandler.route_startswith('/mode/cw/')
def set_cw_band_mode(self):
    """Ustawia tryb CW + częstotliwość CW dla danego pasma"""
    try:
        band = self.path.split('/')[-1]
        if band in HAM_BANDS:
            # Ustaw tryb CW
            RigCommand.setMode(omniClient.CW_U)
            # Ustaw częstotliwość CW dla danego pasma
            cw_freq = HAM_BANDS[band]['CW']
            RigCommand.setFrequency(cw_freq)
            
            self.send_text_response(f'CW mode set for {band} at {cw_freq}Hz')
        else:
            self.send_error_response(400, f'Invalid band. Available bands: {list(HAM_BANDS.keys())}')
    except Exception as e:
        self.send_error_response(500, f'Error setting CW mode: {str(e)}')

@SimpleHTTPRequestHandler.route_startswith('/mode/ssb/')
def set_ssb_band_mode(self):
    """Ustawia tryb SSB (LSB/USB) + częstotliwość SSB dla danego pasma"""
    try:
        band = self.path.split('/')[-1]
        if band in HAM_BANDS:
            # Ustaw tryb SSB - LSB dla pasm 40m, 80m, 160m, USB dla pozostałych
            if band in ['40m', '80m', '160m']:
                RigCommand.setMode(omniClient.MODE_SSB_L)  # LSB
            else:
                RigCommand.setMode(omniClient.MODE_SSB_U)  # USB
            
            # Ustaw częstotliwość SSB dla danego pasma
            ssb_freq = HAM_BANDS[band]['SSB']
            RigCommand.setFrequency(ssb_freq)
            
            mode_type = "LSB" if band in ['40m', '80m', '160m'] else "USB"
            self.send_text_response(f'SSB ({mode_type}) mode set for {band} at {ssb_freq}Hz')
        else:
            self.send_error_response(400, f'Invalid band. Available bands: {list(HAM_BANDS.keys())}')
    except Exception as e:
        self.send_error_response(500, f'Error setting SSB mode: {str(e)}')

@SimpleHTTPRequestHandler.route('/mode/band/up')
def band_up(self):
    """Przechodzi na wyższe pasmo"""
    try:
        # Pobierz aktualną częstotliwość
        current_freq = omniClient.getParam("Freq")
        current_band = RigCommand.getBandFromFrequency(current_freq)
        
        if current_band is None:
            self.send_error_response(400, f'Cannot determine band for frequency {current_freq}Hz')
            return
        
        # Znajdź indeks aktualnego pasma
        try:
            current_index = BAND_ORDER.index(current_band)
            # Sprawdź czy nie jesteśmy na najwyższym paśmie
            if current_index >= len(BAND_ORDER) - 1:
                self.send_error_response(400, f'Already on highest band: {current_band}')
                return
            
            # Ustaw następne pasmo
            next_band = BAND_ORDER[current_index + 1]
            
            # Ustaw częstotliwość SSB dla nowego pasma
            ssb_freq = HAM_BANDS[next_band]['SSB']
            RigCommand.setFrequency(ssb_freq)
            
            # Ustaw odpowiedni tryb SSB
            if next_band in ['40m', '80m', '160m']:
                RigCommand.setMode(omniClient.MODE_SSB_L)  # LSB
            else:
                RigCommand.setMode(omniClient.MODE_SSB_U)  # USB
            
            mode_type = "LSB" if next_band in ['40m', '80m', '160m'] else "USB"
            self.send_text_response(f'Band changed from {current_band} to {next_band} at {ssb_freq}Hz ({mode_type})')
            
        except ValueError:
            self.send_error_response(400, f'Unknown band: {current_band}')
            
    except Exception as e:
        self.send_error_response(500, f'Error changing band: {str(e)}')

@SimpleHTTPRequestHandler.route('/mode/band/down')
def band_down(self):
    """Przechodzi na niższe pasmo"""
    try:
        # Pobierz aktualną częstotliwość
        current_freq = omniClient.getParam("Freq")
        current_band = RigCommand.getBandFromFrequency(current_freq)
        
        if current_band is None:
            self.send_error_response(400, f'Cannot determine band for frequency {current_freq}Hz')
            return
        
        # Znajdź indeks aktualnego pasma
        try:
            current_index = BAND_ORDER.index(current_band)
            # Sprawdź czy nie jesteśmy na najniższym paśmie
            if current_index <= 0:
                self.send_error_response(400, f'Already on lowest band: {current_band}')
                return
            
            # Ustaw poprzednie pasmo
            prev_band = BAND_ORDER[current_index - 1]
            
            # Ustaw częstotliwość SSB dla nowego pasma
            ssb_freq = HAM_BANDS[prev_band]['SSB']
            RigCommand.setFrequency(ssb_freq)
            
            # Ustaw odpowiedni tryb SSB
            if prev_band in ['40m', '80m', '160m']:
                RigCommand.setMode(omniClient.MODE_SSB_L)  # LSB
            else:
                RigCommand.setMode(omniClient.MODE_SSB_U)  # USB
            
            mode_type = "LSB" if prev_band in ['40m', '80m', '160m'] else "USB"
            self.send_text_response(f'Band changed from {current_band} to {prev_band} at {ssb_freq}Hz ({mode_type})')
            
        except ValueError:
            self.send_error_response(400, f'Unknown band: {current_band}')
            
    except Exception as e:
        self.send_error_response(500, f'Error changing band: {str(e)}')

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


