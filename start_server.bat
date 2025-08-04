@echo off
echo Starting HamDeck Server...
echo.
echo Server will be available at: http://localhost:5973
echo Press Ctrl+C to stop the server
echo.

REM Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Sprawdź czy wymagane pliki istnieją
if not exist "server.py" (
    echo ERROR: server.py not found in current directory
    echo Please make sure you are in the correct directory
    pause
    exit /b 1
)

REM Sprawdź czy omnirignew.py istnieje
if not exist "omnirignew.py" (
    echo ERROR: omnirignew.py not found in current directory
    echo Please make sure you are in the correct directory
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

echo Starting server...
python server.py

REM Jeśli serwer się zatrzyma, poczekaj na naciśnięcie klawisza
echo.
echo Server stopped.
pause 