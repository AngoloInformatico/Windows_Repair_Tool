# -*- coding: utf-8 -*-
"""
Windows Repair Tool
Server Flask con API di esecuzione live per comandi di sistema,
streaming console e controllo privilegi amministrativi.
Avvio diretto in finestra applicazione dedicata (modalità standalone senza chrome del browser).
"""

import os
import sys
import ctypes
import platform
import subprocess
import threading
import queue
import time
import json
import webbrowser
import socket
from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from commands_data import COMMANDS, CATEGORIES
from version_manager import get_or_update_version

# Evita eccezioni su print() quando compilato con PyInstaller in modalità --noconsole
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

def get_resource_path(relative_path):
    """Restituisce il percorso assoluto a una risorsa sia in sviluppo che con PyInstaller."""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', None)
        if base_dir and os.path.exists(os.path.join(base_dir, relative_path)):
            return os.path.join(base_dir, relative_path)
            
        exe_dir = os.path.dirname(sys.executable)
        internal_dir = os.path.join(exe_dir, "_internal")
        if os.path.exists(os.path.join(internal_dir, relative_path)):
            return os.path.join(internal_dir, relative_path)
            
        if os.path.exists(os.path.join(exe_dir, relative_path)):
            return os.path.join(exe_dir, relative_path)
            
        return os.path.join(base_dir or exe_dir, relative_path)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, relative_path)

templates_path = get_resource_path("templates")
static_path = get_resource_path("static")

app = Flask(__name__, template_folder=templates_path, static_folder=static_path)

# Porta attiva del server (default 5000, con fallback dinamico a 5001, 5002...)
CURRENT_PORT = 5000

# Memoria dei task in streaming
TASKS = {}
TASKS_LOCK = threading.Lock()

def is_admin():
    """Verifica se il processo è in esecuzione con privilegi di Amministratore."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def get_system_info():
    """Recupera informazioni di base sul sistema operativo e sulla versione dell'app."""
    try:
        uname = platform.uname()
        os_name = f"{uname.system} {uname.release}"
        win_ver = platform.version()
        node_name = uname.node
        machine = uname.machine
    except Exception:
        os_name = "Windows"
        win_ver = "Sconosciuta"
        node_name = "PC"
        machine = "x64"

    ver, bld, upd = get_or_update_version()

    return {
        "os_name": os_name,
        "win_version": win_ver,
        "hostname": node_name,
        "arch": machine,
        "is_admin": is_admin(),
        "python_version": platform.python_version(),
        "version": ver,
        "build": bld,
        "updated_at": upd,
        "port": CURRENT_PORT
    }

@app.route("/")
def index():
    """Pagina principale della WebApp."""
    sys_info = get_system_info()
    return render_template("index.html", 
                           commands=COMMANDS, 
                           categories=CATEGORIES,
                           sys_info=sys_info)

@app.route("/favicon.ico")
def favicon():
    """Restituisce l'icona favicon della WebApp."""
    return send_from_directory(app.static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/api/system-status")
def api_system_status():
    """Restituisce le informazioni di sistema e lo stato dei privilegi."""
    return jsonify(get_system_info())

@app.route("/api/commands")
def api_commands():
    """Restituisce la lista di categorie e comandi."""
    return jsonify({
        "categories": CATEGORIES,
        "commands": COMMANDS
    })

def relaunch_as_admin(port=None):
    """
    Rilancia l'applicazione richiedendo i privilegi di Amministratore tramite UAC (runas).
    Funziona nativamente sia per l'eseguibile compilato (.exe) sia per lo script Python.
    Passa l'argomento --relaunch-port per preservare la stessa porta nel processo elevato.
    """
    target_port = port if port else CURRENT_PORT
    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        executable = sys.executable
        params = f"--relaunch-port {target_port}"
        work_dir = os.path.dirname(executable)
    else:
        executable = sys.executable
        main_script = os.path.abspath(__file__)
        params = f'"{main_script}" --relaunch-port {target_port}'
        work_dir = os.path.dirname(main_script)

    try:
        # 1 = SW_SHOWNORMAL
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            params,
            work_dir,
            1
        )
        return ret > 32
    except Exception as e:
        print(f"[ERROR] ShellExecuteW fallita: {e}")
        return False

@app.route("/api/relaunch-admin", methods=["POST"])
def api_relaunch_admin():
    """
    Rilancia l'applicazione con privilegi elevati UAC e chiude l'istanza standard corrente
    non appena inviata la risposta per liberare la porta attiva al processo elevato.
    """
    try:
        if is_admin():
            return jsonify({
                "success": True, 
                "is_admin": True,
                "port": CURRENT_PORT,
                "message": "L'applicazione è già in esecuzione con privilegi di Amministratore."
            })

        success = relaunch_as_admin(CURRENT_PORT)
        if success:
            # Terminiamo l'istanza standard dopo 0.6s per liberare la porta al processo elevato
            def terminate_old_instance():
                time.sleep(0.6)
                os._exit(0)
            threading.Thread(target=terminate_old_instance, daemon=True).start()
            
            return jsonify({
                "success": True, 
                "port": CURRENT_PORT,
                "message": "Richiesta UAC inviata. L'applicazione si riavvia con privilegi di Amministratore..."
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Elevazione UAC annullata o non consentita dall'utente."
            }), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/open-external-browser", methods=["POST"])
def api_open_external_browser():
    """Apre la WebApp nel browser predefinito completo dell'utente sulla porta attualmente attiva."""
    try:
        url = request.host_url.rstrip('/') if request.host_url else f"http://127.0.0.1:{CURRENT_PORT}"
        webbrowser.open(url)
        return jsonify({"success": True, "url": url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Variabili di stato per il monitoraggio chiusura finestra
LAST_HEARTBEAT = time.time()
HEARTBEAT_ACTIVE = False

@app.route("/api/heartbeat", methods=["POST"])
def api_heartbeat():
    """Riceve il battito periodico dalla WebApp per confermare che la finestra è attiva."""
    global LAST_HEARTBEAT, HEARTBEAT_ACTIVE
    LAST_HEARTBEAT = time.time()
    HEARTBEAT_ACTIVE = True
    return jsonify({"status": "alive"})

@app.route("/api/shutdown", methods=["POST", "GET"])
def api_shutdown():
    """Arresta immediatamente l'applicazione e tutti i processi quando l'utente chiude la finestra."""
    def kill_now():
        time.sleep(0.3)
        os._exit(0)
    threading.Thread(target=kill_now, daemon=True).start()
    return jsonify({"success": True, "message": "Arresto completato."})

def heartbeat_watchdog():
    """Watchdog: se non riceve heartbeat per oltre 5 secondi, arresta l'intero programma."""
    time.sleep(6.0)
    while True:
        time.sleep(1.5)
        if HEARTBEAT_ACTIVE and (time.time() - LAST_HEARTBEAT > 5.0):
            print("\n[INFO] Finestra dell'applicazione chiusa. Arresto completato di tutti i processi.")
            os._exit(0)

def run_command_worker(task_id, cmd_string):
    """Esegue il comando in un subprocess catturando l'output riga per riga per lo streaming SSE."""
    q = TASKS[task_id]["queue"]
    
    q.put(f"[START] Inizio esecuzione: {cmd_string}\n")
    if not is_admin():
        q.put("[WARN] NOTA: Il server non è in esecuzione come Amministratore. I comandi di basso livello (DISM, SFC, BCDEDIT) potrebbero fallire con errore di accesso negato.\n")
    
    start_time = time.time()
    try:
        process = subprocess.Popen(
            cmd_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            text=True,
            encoding="cp850",
            errors="replace",
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            if line:
                q.put(line)
        
        process.stdout.close()
        return_code = process.wait()
        elapsed = round(time.time() - start_time, 2)
        
        if return_code == 0:
            q.put(f"\n[SUCCESS] Comando completato con successo (Codice uscita 0) in {elapsed}s\n")
        else:
            q.put(f"\n[EXIT] Processo terminato con codice {return_code} in {elapsed}s\n")
            
    except Exception as e:
        q.put(f"\n[ERROR] Eccezione durante l'esecuzione del comando: {str(e)}\n")
    finally:
        q.put("[DONE]")

@app.route("/api/execute", methods=["POST"])
def api_execute():
    """Inizializza un task di esecuzione comando e restituisce il task_id per lo streaming."""
    data = request.json or {}
    cmd_id = data.get("id")
    custom_cmd = data.get("custom_cmd")
    
    selected_cmd = None
    if cmd_id:
        for c in COMMANDS:
            if c["id"] == cmd_id:
                selected_cmd = c["command"]
                break
                
    if custom_cmd:
        selected_cmd = custom_cmd
        
    if not selected_cmd:
        return jsonify({"error": "Nessun comando valido fornito"}), 400
        
    task_id = f"task_{int(time.time() * 1000)}"
    q = queue.Queue()
    
    with TASKS_LOCK:
        TASKS[task_id] = {
            "queue": q,
            "created": time.time(),
            "cmd": selected_cmd
        }
        
    t = threading.Thread(target=run_command_worker, args=(task_id, selected_cmd), daemon=True)
    t.start()
    
    return jsonify({
        "task_id": task_id,
        "command": selected_cmd
    })

@app.route("/api/stream/<task_id>")
def api_stream(task_id):
    """Endpoint SSE per lo streaming in tempo reale dei log della console."""
    with TASKS_LOCK:
        task = TASKS.get(task_id)
        
    if not task:
        return Response("data: [ERROR] Task non trovato o scaduto\n\n", mimetype="text/event-stream")
        
    q = task["queue"]
    
    def generate():
        while True:
            try:
                line = q.get(timeout=30)
                if line == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                payload = json.dumps({"text": line})
                yield f"data: {payload}\n\n"
            except queue.Empty:
                yield "data: {\"ping\": true}\n\n"
            except GeneratorExit:
                break
                
        with TASKS_LOCK:
            if task_id in TASKS:
                del TASKS[task_id]
                
    return Response(generate(), mimetype="text/event-stream")

@app.route("/api/export-script", methods=["POST"])
def api_export_script():
    """Genera e restituisce uno script .bat o .ps1 con i 30 comandi pronti all'uso con controllo UAC."""
    data = request.json or {}
    script_format = data.get("format", "bat")
    
    selected_commands = COMMANDS
        
    if script_format == "ps1":
        content = [
            "# ================================================================",
            "# WINDOWS REPAIR TOOL - TUTTI I 30 COMANDI (POWERSHELL)",
            "# Created by Alex Lignola - © 2026 WINDOWS REPAIR",
            "# ================================================================",
            "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {",
            "    Write-Warning 'Questo script richiede privilegi di Amministratore. Rilancio UAC in corso...'",
            "    Start-Process powershell.exe -ArgumentList \"-NoProfile -ExecutionPolicy Bypass -File `\"$PSCommandPath`\"\" -Verb RunAs",
            "    exit",
            "}",
            "Clear-Host",
            "Write-Host '====================================================' -ForegroundColor Cyan",
            "Write-Host '  WINDOWS 11 REPAIR SUITE - 30 COMANDI DI RIPARAZIONE' -ForegroundColor Yellow",
            "Write-Host '====================================================' -ForegroundColor Cyan",
            ""
        ]
        for c in selected_commands:
            content.append(f"Write-Host '>>> [{c['num']}/30] Esecuzione: {c['name']} ({c['display_cmd']})' -ForegroundColor Green")
            content.append(f"Write-Host 'Descrizione: {c['short_desc']}' -ForegroundColor DarkGray")
            content.append(c["command"])
            content.append("Start-Sleep -Seconds 1")
            content.append("")
        content.append("Write-Host 'Tutti i 30 comandi sono stati completati!' -ForegroundColor Cyan")
        content.append("pause")
        filename = "Windows11_Repair_Suite_30Comandi.ps1"
        mimetype = "text/plain"
    else:
        content = [
            "@echo off",
            ":: ================================================================",
            ":: WINDOWS REPAIR TOOL - TUTTI I 30 COMANDI (BATCH)",
            ":: Created by Alex Lignola - © 2026 WINDOWS REPAIR",
            ":: ================================================================",
            "chcp 65001 >nul",
            "title Windows 11 Repair Assistant - 30 Comandi",
            "cls",
            ":: Controllo Amministratore",
            "net session >nul 2>&1",
            "if %errorLevel% neq 0 (",
            "    echo [!] ERRORE: Questo script deve essere eseguito come Amministratore!",
            "    echo Fai clic destro sul file e seleziona 'Esegui come amministratore'.",
            "    pause",
            "    exit /b 1",
            ")",
            "echo ====================================================",
            "echo   WINDOWS 11 REPAIR SUITE - 30 COMANDI DI RIPARAZIONE",
            "echo ====================================================",
            "echo.",
        ]
        for c in selected_commands:
            content.append(f"echo [>] [{c['num']}/30] Esecuzione: {c['name']}")
            content.append(f"echo    {c['short_desc']}")
            content.append(c["command"])
            content.append("echo.")
        content.append("echo [OK] Tutti i 30 comandi sono stati eseguiti con successo.")
        content.append("pause")
        filename = "Windows11_Repair_Suite_30Comandi.bat"
        mimetype = "text/plain"
        
    return Response("\n".join(content), mimetype=mimetype, headers={"Content-Disposition": f"attachment; filename={filename}"})

# =========================================================================
# GESTIONE AVVIO IN FINESTRA DEDICATA STANDALONE (SENZA INTERFACCIA BROWSER)
# =========================================================================
def find_app_browser():
    """Rileva Microsoft Edge o Google Chrome per l'avvio in modalità app window (senza barre, schede o URL)."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None

def get_centered_window_geometry(preferred_w=1560, preferred_h=960):
    """Calcola dimensioni e coordinate X,Y per posizionare la finestra esattamente al centro dello schermo."""
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screen_w = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_h = user32.GetSystemMetrics(1)  # SM_CYSCREEN
    except Exception:
        screen_w, screen_h = 1920, 1080

    # Adatta le dimensioni proporzionalmente se lo schermo è più compatto
    win_w = min(preferred_w, max(1000, int(screen_w * 0.90)))
    win_h = min(preferred_h, max(680, int(screen_h * 0.90)))

    # Coordinate precise per il centro geometrico
    pos_x = max(0, (screen_w - win_w) // 2)
    pos_y = max(0, (screen_h - win_h) // 2)

    return win_w, win_h, pos_x, pos_y

def launch_app_window(url):
    """
    Apre direttamente l'intera WebApp in una finestra applicazione dedicata
    posizionata sempre esattamente al centro dello schermo.
    """
    browser_exe = find_app_browser()
    win_w, win_h, pos_x, pos_y = get_centered_window_geometry(1560, 960)

    if browser_exe:
        cmd = [
            browser_exe,
            f"--app={url}",
            f"--window-size={win_w},{win_h}",
            f"--window-position={pos_x},{pos_y}"
        ]

        # Thread di rinforzo Win32 per garantire il posizionamento centrale anche in caso di sessioni precedenti memorizzate
        def enforce_center():
            for _ in range(5):
                time.sleep(0.5)
                try:
                    user32 = ctypes.windll.user32
                    def enum_handler(hwnd, _):
                        if user32.IsWindowVisible(hwnd):
                            length = user32.GetWindowTextLengthW(hwnd)
                            if length > 0:
                                buff = ctypes.create_unicode_buffer(length + 1)
                                user32.GetWindowTextW(hwnd, buff, length + 1)
                                txt = buff.value.lower()
                                if "windows repair" in txt or "console di riparazione" in txt:
                                    user32.SetWindowPos(hwnd, 0, pos_x, pos_y, win_w, win_h, 0x0044)
                        return True
                    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(enum_handler)
                    user32.EnumWindows(cb, 0)
                except Exception:
                    pass

        threading.Thread(target=enforce_center, daemon=True).start()
        # Avvia il watchdog dell'heartbeat per arrestare il server appena la finestra si chiude
        threading.Thread(target=heartbeat_watchdog, daemon=True).start()

        try:
            proc = subprocess.Popen(cmd)
            # Attendiamo per verificare se il processo è rimasto agganciato alla finestra dedicata
            time.sleep(2.0)
            if proc.poll() is None:
                # Il processo monitora attivamente la finestra dedicata: attendi la chiusura
                proc.wait()
                os._exit(0)
            else:
                # Il browser ha aperto la finestra standalone delegando a un'istanza in esecuzione.
                # Il watchdog e il beacon beforeunload chiuderanno automaticamente tutto non appena la finestra si chiude.
                try:
                    while True:
                        time.sleep(1.0)
                except KeyboardInterrupt:
                    os._exit(0)
        except KeyboardInterrupt:
            os._exit(0)
        except Exception:
            webbrowser.open(url)
    else:
        webbrowser.open(url)

def find_free_port(preferred_port=5000, max_port=5100, host="127.0.0.1", wait_seconds=0):
    """
    Trova una porta TCP libera per il server.
    Se preferred_port (default 5000) è occupata, passa automaticamente
    alla prima porta libera successiva (5001, 5002, 5003, ...).
    Se wait_seconds > 0 (es. durante un passaggio UAC), attende prima brevemente
    nel caso preferred_port venga liberata dall'istanza precedente.
    """
    # Se indicato un tempo di attesa (handover UAC), prova prima a riutilizzare la porta richiesta
    if wait_seconds > 0:
        start_time = time.time()
        while time.time() - start_time < wait_seconds:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((host, preferred_port))
                    return preferred_port
            except OSError:
                time.sleep(0.15)

    # Scansione dinamica da preferred_port fino a max_port
    for p in range(preferred_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((host, p))
                return p
        except OSError:
            continue

    # Fallback estremo: lascia che il sistema operativo assegni qualsiasi porta effimera libera
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]

def run_flask_server(host, port):
    """
    Avvia il server Flask sulla porta assegnata.
    Se si verifica un ritardo temporaneo nel rilascio della porta, esegue brevi tentativi.
    """
    for attempt in range(10):
        try:
            app.run(host=host, port=port, debug=False, use_reloader=False)
            break
        except OSError:
            time.sleep(0.25)

if __name__ == "__main__":
    host = "127.0.0.1"

    # Gestione argomento opzionale di rilancio porta (es. --relaunch-port 5000)
    relaunch_port = None
    if "--relaunch-port" in sys.argv:
        try:
            idx = sys.argv.index("--relaunch-port")
            if idx + 1 < len(sys.argv):
                relaunch_port = int(sys.argv[idx + 1])
        except Exception:
            relaunch_port = None

    # Se rilanciato da processo precedente, attendi fino a 1.5s la sua porta
    wait_time = 1.5 if relaunch_port else 0
    start_port = relaunch_port if relaunch_port else 5000

    # Rilevamento automatico: se 5000 è occupata, passa automaticamente a un'altra porta libera (5001, 5002, ...)
    port = find_free_port(preferred_port=start_port, max_port=5100, host=host, wait_seconds=wait_time)
    CURRENT_PORT = port
    url = f"http://{host}:{port}"

    # Aggiorna o calcola la versione automatica
    current_version, current_build, _ = get_or_update_version()
    
    # Avvia il server Flask in background (thread demone con porta assegnata)
    flask_thread = threading.Thread(
        target=lambda: run_flask_server(host, port),
        daemon=True
    )
    flask_thread.start()

    # Attende che il server Flask sia effettivamente in ascolto e pronto prima di lanciare la finestra
    for _ in range(50):
        try:
            with socket.create_connection((host, port), timeout=0.2):
                break
        except Exception:
            time.sleep(0.2)

    print("=" * 68)
    print("  WINDOWS REPAIR TOOL - 30 COMANDI DI RIPARAZIONE")
    print(f"  Versione: v{current_version} (Build {current_build})")
    if port != 5000 and not relaunch_port:
        print(f"  [INFO] Porta 5000 occupata. Assegnata automaticamente la porta libera: {port}")
    print(f"  Server Web Locale attivo su: {url}")
    print(f"  Amministratore: {'SI (Privilegi Pieni)' if is_admin() else 'NO (Rilanciare come Admin)'}")
    print("  Apertura finestra applicazione dedicata in corso...")
    print("=" * 68)

    # Se passato l'argomento --no-gui (es. per test o server puro)
    if "--no-gui" in sys.argv:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nChiusura server...")
            sys.exit(0)
    else:
        # Apre direttamente l'intera WebApp in una finestra dedicata senza mostrare l'intero browser
        launch_app_window(url)
        # Chiusura pulita al termine della sessione finestra
        os._exit(0)
