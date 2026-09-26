# -*- coding: utf-8 -*-
"""
Modulo di gestione versione automatica per Windows Repair Tool.
Incrementa automaticamente il numero di build ad ogni modifica rilevata nei file sorgenti.
"""

import os
import sys
import json
import hashlib
from datetime import datetime

def get_base_dir():
    """Restituisce la cartella base sia in modalità sorgente che PyInstaller."""
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass and os.path.exists(os.path.join(meipass, "version.json")):
            return meipass
        exe_dir = os.path.dirname(sys.executable)
        internal_dir = os.path.join(exe_dir, "_internal")
        if os.path.exists(os.path.join(internal_dir, "version.json")):
            return internal_dir
        return exe_dir
    return os.path.dirname(os.path.abspath(__file__))

WATCHED_FILES = [
    "app.py",
    "commands_data.py",
    "version_manager.py",
    os.path.join("templates", "index.html"),
    os.path.join("static", "css", "style.css"),
    os.path.join("static", "js", "app.js")
]

def calculate_checksum(base_dir):
    """Calcola un hash combinato di tutti i file sorgente monitorati."""
    hasher = hashlib.md5()
    for rel_path in WATCHED_FILES:
        full_path = os.path.join(base_dir, rel_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "rb") as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
            except Exception:
                pass
    return hasher.hexdigest()

def get_or_update_version():
    """
    Legge la versione corrente. Se rileva modifiche nei file sorgenti rispetto
    all'ultimo hash salvato, incrementa automaticamente la build.
    """
    base_dir = get_base_dir()
    version_file = os.path.join(base_dir, "version.json")
    
    # Se eseguito dentro l'exe già compilato, leggi la versione fissa senza aggiornarla
    if getattr(sys, 'frozen', False):
        if os.path.exists(version_file):
            try:
                with open(version_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("version", "1.0.0"), data.get("build", 1), data.get("updated_at", "")
            except Exception:
                pass
        return "1.0.0", 1, ""

    current_hash = calculate_checksum(base_dir)
    
    data = {
        "major": 1,
        "minor": 0,
        "build": 1,
        "version": "1.0.1",
        "last_hash": "",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(version_file):
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    # Verifica se i sorgenti sono stati modificati
    if data.get("last_hash") != current_hash:
        data["build"] = data.get("build", 0) + 1
        data["version"] = f"{data.get('major', 1)}.{data.get('minor', 0)}.{data['build']}"
        data["last_hash"] = current_hash
        data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(version_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    return data["version"], data["build"], data["updated_at"]

if __name__ == "__main__":
    ver, bld, upd = get_or_update_version()
    print(f"Versione corrente: v{ver} (Build {bld}) - Ultimo aggiornamento: {upd}")
