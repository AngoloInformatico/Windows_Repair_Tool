# -*- coding: utf-8 -*-
"""
===============================================================================
GENERATORE ESEGUIBILE (.EXE) - WINDOWS REPAIR TOOL
===============================================================================
Questo script automatizza la compilazione dell'eseguibile standalone per Windows.
- Cancella completamente la cartella 'dist' e 'build' prima di ogni compilazione.
- Imposta la modalità --noconsole per non mostrare alcuna finestra di terminale.
- Associa l'icona ufficiale 'icona/icon.ico'.
- Include tutte le risorse necessarie (templates, static, database comandi, version).
- Supporta sia la modalità directory (--onedir predefinita, avvio istantaneo) 
  sia la modalità file singolo (--onefile).
===============================================================================
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from version_manager import get_or_update_version

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")
ICON_PATH = os.path.join(BASE_DIR, "icona", "icon.ico")
APP_SCRIPT = os.path.join(BASE_DIR, "app.py")
APP_NAME = "Windows Repair Tool"

def print_banner(version, build):
    print("=" * 72)
    print("   WINDOWS REPAIR TOOL - COMPILATORE ESEGUIBILE NATIVO (.EXE)")
    print(f"   Versione: v{version} (Build #{build})")
    print(f"   Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 72)

def clean_folders():
    """Cancella completamente dist, build e file spec per ricreare tutto da zero."""
    print("\n[1/5] Pulizia ambiente di compilazione...")
    
    if os.path.exists(DIST_DIR):
        print(f"  -> Eliminazione cartella precedente: {DIST_DIR}")
        try:
            shutil.rmtree(DIST_DIR, ignore_errors=False)
        except Exception:
            # Fallback se qualche file è in uso
            shutil.rmtree(DIST_DIR, ignore_errors=True)
            
    if os.path.exists(BUILD_DIR):
        print(f"  -> Eliminazione cartella temporanea: {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    # Elimina eventuali file .spec rimasti
    for item in os.listdir(BASE_DIR):
        if item.endswith(".spec"):
            try:
                os.remove(os.path.join(BASE_DIR, item))
                print(f"  -> Rimosso file di specifica: {item}")
            except Exception:
                pass

    # Ricrea la cartella dist pulita
    os.makedirs(DIST_DIR, exist_ok=True)
    print("  [OK] Pulizia completata con successo.")

def check_requirements():
    """Verifica che PyInstaller e l'icona siano disponibili."""
    print("\n[2/5] Verifica requisiti e dipendenze...")
    
    try:
        import PyInstaller
        print(f"  -> PyInstaller rilevato: v{PyInstaller.__version__}")
    except ImportError:
        print("  [!] PyInstaller non installato. Installazione automatica in corso...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    if not os.path.exists(ICON_PATH):
        print("  [!] Icona non trovata in 'icona/icon.ico'. Generazione automatica in corso...")
        # Lancia script di rigenerazione icona se necessario
        try:
            subprocess.run([sys.executable, "-c", "import create_icon"], cwd=BASE_DIR)
        except Exception:
            pass

    if os.path.exists(ICON_PATH):
        print(f"  -> Icona confermata: {ICON_PATH}")
    else:
        print("  [!] Attenzione: icona non presente, verrà usata l'icona predefinita.")

def build_executable(onefile=False):
    """Esegue PyInstaller con configurazione ottimizzata per Windows Repair Tool."""
    print("\n[3/5] Compilazione eseguibile con PyInstaller...")
    mode_str = "File Singolo (--onefile)" if onefile else "Cartella Applicazione (--onedir)"
    print(f"  -> Modalità di compilazione: {mode_str}")
    print("  -> Finestra console terminale: DISABILITATA (--noconsole)")

    # Separatore per add-data su Windows è ';'
    data_separator = ";" if os.name == "nt" else ":"

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--clean",
        f"--name={APP_NAME}",
        f"--icon={ICON_PATH}" if os.path.exists(ICON_PATH) else "",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--add-data=templates{data_separator}templates",
        f"--add-data=static{data_separator}static",
        f"--add-data=commands_data.py{data_separator}.",
        f"--add-data=version.json{data_separator}.",
        f"--add-data=version_manager.py{data_separator}.",
        f"--add-data=icona{data_separator}icona",
        "--onefile" if onefile else "--onedir",
        APP_SCRIPT
    ]

    # Rimuove argomenti vuoti
    cmd = [arg for arg in cmd if arg]

    print("  -> Avvio processo PyInstaller...")
    result = subprocess.run(cmd, cwd=BASE_DIR)

    if result.returncode != 0:
        print(f"\n[ERRORE] La compilazione è fallita con codice di uscita: {result.returncode}")
        sys.exit(result.returncode)

    print("  [OK] Compilazione PyInstaller terminata con successo.")

def cleanup_build():
    """Rimuove la cartella temporanea build per lasciare solo dist pulita."""
    print("\n[4/5] Pulizia file temporanei di compilazione...")
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        print("  -> Cartella build rimossa.")
        
    for item in os.listdir(BASE_DIR):
        if item.endswith(".spec"):
            try:
                os.remove(os.path.join(BASE_DIR, item))
            except Exception:
                pass
    print("  [OK] Cartella dist pronta.")

def print_summary(onefile=False):
    """Mostra il riepilogo finale e la posizione del file eseguibile."""
    print("\n[5/5] RIEPILOGO FINALE:")
    print("=" * 72)
    if onefile:
        exe_path = os.path.join(DIST_DIR, f"{APP_NAME}.exe")
        print(f"  Eseguibile generato: {exe_path}")
    else:
        app_folder = os.path.join(DIST_DIR, APP_NAME)
        exe_path = os.path.join(app_folder, f"{APP_NAME}.exe")
        print(f"  Cartella Distribuzione: {app_folder}")
        print(f"  Eseguibile principale:  {exe_path}")

    print("\n  CARATTERISTICHE ESEGUIBILE:")
    print("  - Icona applicazione incorporata: icona/icon.ico")
    print("  - Nessuna console nera/terminale all'avvio (--noconsole)")
    print("  - WebApp avviata direttamente in finestra desktop centrata")
    print("  - Chiusura sincronizzata istantanea di tutti i processi")
    print("=" * 72)

def main():
    # Verifica parametri da riga di comando (es. python GeneraExe.py --onefile)
    onefile_mode = "--onefile" in sys.argv

    # Aggiorna versione
    ver, bld, upd = get_or_update_version()
    print_banner(ver, bld)

    # Esegui passaggi
    clean_folders()
    check_requirements()
    build_executable(onefile=onefile_mode)
    cleanup_build()
    print_summary(onefile=onefile_mode)

if __name__ == "__main__":
    main()
