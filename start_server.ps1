# HamDeck Server Launcher for PowerShell
# Uruchom jako: .\start_server.ps1

param(
    [switch]$Verbose,
    [switch]$Help
)

if ($Help) {
    Write-Host "HamDeck Server Launcher" -ForegroundColor Green
    Write-Host "Usage: .\start_server.ps1 [-Verbose] [-Help]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -Verbose    Show detailed information" -ForegroundColor White
    Write-Host "  -Help       Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Server will be available at: http://localhost:5973" -ForegroundColor Green
    exit 0
}

Write-Host "Starting HamDeck Server..." -ForegroundColor Green
Write-Host ""

# Sprawdź czy Python jest zainstalowany
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Sprawdź czy wymagane pliki istnieją
$requiredFiles = @("server.py", "omnirignew.py")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "ERROR: $file not found in current directory" -ForegroundColor Red
        Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
        Write-Host "Please make sure you are in the correct directory" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

if ($Verbose) {
    Write-Host "Required files found:" -ForegroundColor Green
    foreach ($file in $requiredFiles) {
        $fileInfo = Get-Item $file
        Write-Host "  $file ($($fileInfo.Length) bytes, modified: $($fileInfo.LastWriteTime))" -ForegroundColor White
    }
    Write-Host ""
}

Write-Host "Server will be available at: http://localhost:5973" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Sprawdź czy port 5973 jest dostępny
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 5973)
    $tcpClient.Close()
    Write-Host "WARNING: Port 5973 is already in use!" -ForegroundColor Yellow
    Write-Host "The server might not start properly." -ForegroundColor Yellow
    Write-Host ""
} catch {
    if ($Verbose) {
        Write-Host "Port 5973 is available" -ForegroundColor Green
    }
}

Write-Host "Starting server..." -ForegroundColor Green
Write-Host ""

try {
    # Uruchom serwer
    python server.py
} catch {
    Write-Host "ERROR: Failed to start server" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
} 