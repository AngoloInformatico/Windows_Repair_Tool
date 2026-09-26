@echo off
chcp 65001 >nul
title Windows Repair Tool - Avvio Launcher
cls

echo =======================================================================
echo          WINDOWS REPAIR TOOL - 30 COMANDI DI RIPARAZIONE
echo =======================================================================
echo.
echo Controllo privilegi di sistema...

:: Verifica se eseguito come amministratore
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Esecuzione con privilegi di Amministratore confermata!
) else (
    echo [!] AVVISO: Non sei attualmente in modalita Amministratore.
    echo 'Tasto destro -> Esegui come amministratore'.
    echo.
)

echo Avvio WebApp in finestra applicazione dedicata...
echo (Finestra standalone centrata sullo schermo).
echo Dalla barra superiore sara sempre possibile cliccare 'Apri nel Browser'.
echo.

:: Avvia l'applicazione in finestra dedicata
python app.py

exit /b 0
