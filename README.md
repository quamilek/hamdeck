# HamDeck Server

Serwer HTTP do sterowania odbiornikiem krótkofalarskim przez OmniRig.

## Wymagania

- Python 3.6+
- OmniRig zainstalowany i skonfigurowany
- Plik `omnirignew.py` (wrapper dla OmniRig)

## Uruchamianie w Windows

### Opcja 1: Plik batch (prosty)
```cmd
start_server.bat
```

### Opcja 2: PowerShell (zaawansowany)
```powershell
.\start_server.ps1
```

Z opcjami:
```powershell
.\start_server.ps1 -Verbose    # Szczegółowe informacje
.\start_server.ps1 -Help       # Pomoc
```

## Uruchamianie w Linux/macOS
```bash
python3 server.py
```

## Dostępne endpointy

### Informacje o odbiorniku
- `GET /` - informacje o aktualnym trybie i typie odbiornika

### Podstawowe tryby
- `GET /mode/cw` - tryb CW
- `GET /mode/usb` - tryb USB
- `GET /mode/lsb` - tryb LSB

### Split (podział częstotliwości)
- `GET /mode/split` - przełącza split ON/OFF
- `GET /mode/split/{value}` - ustawia split na wartość w MHz (np. `/mode/split/1.5`)

### Tryby dla konkretnych pasm
- `GET /mode/ft8/{band}` - FT8 dla pasma (USB + częstotliwość FT8)
- `GET /mode/cw/{band}` - CW dla pasma (CW + częstotliwość CW)
- `GET /mode/ssb/{band}` - SSB dla pasma (LSB/USB + częstotliwość SSB)

### Nawigacja po pasmach
- `GET /mode/band/up` - przechodzi na wyższe pasmo
- `GET /mode/band/down` - przechodzi na niższe pasmo

## Dostępne pasma
- `160m`, `80m`, `40m`, `30m`, `20m`, `17m`, `15m`, `12m`, `10m`, `6m`

## Przykłady użycia

```bash
# FT8 na 20m
curl http://localhost:5973/mode/ft8/20m

# CW na 40m
curl http://localhost:5973/mode/cw/40m

# SSB na 80m (automatycznie LSB)
curl http://localhost:5973/mode/ssb/80m

# Split 2.5 MHz
curl http://localhost:5973/mode/split/2.5

# Przejście na wyższe pasmo
curl http://localhost:5973/mode/band/up
```

## Konfiguracja

Serwer domyślnie nasłuchuje na porcie 5973. Aby zmienić port, edytuj zmienną `PORT` w pliku `server.py`.

## Rozwiązywanie problemów

### Python nie jest znaleziony
- Zainstaluj Python z [python.org](https://www.python.org/downloads/)
- Upewnij się, że zaznaczono "Add Python to PATH" podczas instalacji

### Port 5973 jest zajęty
- Zmień port w pliku `server.py`
- Lub zatrzymaj inne aplikacje używające tego portu

### OmniRig nie odpowiada
- Sprawdź czy OmniRig jest uruchomiony
- Sprawdź konfigurację OmniRig
- Upewnij się, że odbiornik jest podłączony i włączony

## Struktura plików

```
hamdeck/
├── server.py              # Główny serwer
├── omnirignew.py          # Wrapper dla OmniRig
├── start_server.bat       # Skrypt uruchamiający (Windows)
├── start_server.ps1       # Skrypt PowerShell (Windows)
└── README.md              # Ten plik
``` 