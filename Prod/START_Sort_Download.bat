@echo off
:: Überprüfen, ob die Pakete bereits installiert ist
python -m pip list | findstr /C:"watchdog" > nul

:: Wenn das Paket nicht gefunden wurde, führe die Installation aus
if errorlevel 1 (
    echo Pakete werden installiert...
    python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org watchdog
) else (
    echo Pakete sind bereits installiert.
)

:: Führen Sie Ihr Python-Skript aus. Ersetzen Sie 'APP.py' durch den Namen Ihres Skripts.
python Main.py

echo.
echo Skript wurde ausgeführt. Fenster schließen oder weitere Befehle eingeben.
pause