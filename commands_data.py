# -*- coding: utf-8 -*-
"""
Database comandi di riparazione e manutenzione per Windows 11
Ispirato all'interfaccia HUD Cyberpunk '10 Comandi di Riparazione di Windows'
con estensione completa a coltellino svizzero di sistema.
"""

CATEGORIES = [
    {"id": "all", "name": "Tutti i 30 Comandi", "icon": "fa-th-large"},
    {"id": "boot", "name": "Avvio, BCD & WinRE", "icon": "fa-power-off"},
    {"id": "integrity", "name": "Integrità File & DISM", "icon": "fa-shield-halved"},
    {"id": "network", "name": "Rete & Connettività", "icon": "fa-network-wired"},
    {"id": "disk", "name": "Dischi, FS & Storage", "icon": "fa-hard-drive"},
    {"id": "update", "name": "Windows Update & Servizi", "icon": "fa-arrows-rotate"},
    {"id": "shell", "name": "Shell Win 11 & App Store", "icon": "fa-window-restore"},
    {"id": "diag", "name": "Diagnostica & Hardware", "icon": "fa-microchip"}
]

COMMANDS = [
    # --- I 30 COMANDI DI RIPARAZIONE WINDOWS 11 ---
    {
        "id": "cmd-1",
        "num": 1,
        "is_original": True,
        "category": "boot",
        "name": "startuprepair",
        "command": "powershell -Command \"Start-Process -FilePath 'shutdown.exe' -ArgumentList '/r /o /t 0'\" -Wait",
        "display_cmd": "startuprepair",
        "icon": "desktop-gear",
        "short_desc": "Avvia la riparazione automatica all'avvio di Windows.",
        "full_desc": "Invoca l'ambiente di ripristino di Windows (WinRE) programmando l'avvio nel menu di Riparazione Automatica. Windows analizzerà i file di boot, le voci di registro corrotte, i driver difettosi e i settori di avvio tentando un ripristino automatico senza perdita di dati.",
        "pros": [
            "Completamente automatizzato: analizza e corregge file BCD, MBR e file di avvio critici mancanti.",
            "Non intacca i file personali, documenti o applicazioni installate.",
            "Ideale come primo tentativo quando Windows impiega troppo tempo ad avviarsi o va in crash durante il boot."
        ],
        "cons": [
            "Richiede il riavvio immediato del computer.",
            "Se il problema è dovuto a un guasto hardware fisico (SSD/HDD danneggiato) non risolverà l'errore.",
            "In casi rari può entrare in un loop di diagnosi se il registro di sistema è gravemente compromesso."
        ],
        "risk": "medium",
        "risk_label": "Richiede Riavvio",
        "requires_admin": True,
        "needs_reboot": True,
        "interactive": False
    },
    {
        "id": "cmd-2",
        "num": 2,
        "is_original": True,
        "category": "boot",
        "name": "bcdedit",
        "command": "bcdedit",
        "display_cmd": "bcdedit",
        "icon": "chip-bcd",
        "short_desc": "Visualizza e gestisce i dati di configurazione dell'avvio (Boot Configuration Data).",
        "full_desc": "Mostra le impostazioni attuali del Boot Configuration Data (BCD). Elenca il Windows Boot Manager, il Windows Boot Loader attivo, identificatori GUID ({bootmgr}, {current}), percorsi dei file winload.efi/winload.exe e parametri del kernel.",
        "pros": [
            "Fornisce una panoramica immediata e precisa della configurazione di avvio UEFI/BIOS.",
            "Operazione in sola lettura se eseguita senza parametri: sicura al 100% da visualizzare.",
            "Permette di diagnosticare problemi di dual-boot, percorsi di avvio errati e modalità provvisoria."
        ],
        "cons": [
            "L'output contiene identificatori GUID complessi non banali per utenti inesperti.",
            "Se modificato con parametri errati può rendere il sistema non avviabile."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Lettura)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-3",
        "num": 3,
        "is_original": True,
        "category": "boot",
        "name": "bcdedit /enum",
        "command": "bcdedit /enum all",
        "display_cmd": "bcdedit /enum",
        "icon": "list-enum",
        "short_desc": "Mostra tutte le voci dettagliate di avvio nel BCD store.",
        "full_desc": "Esegue una scansione ed enumerazione completa di tutte le voci memorizzate nel repository BCD: caricatori di avvio, applicazioni di ripristino RAM, strumenti di test della memoria e configurazioni di resume da ibernazione.",
        "pros": [
            "Mostra ogni singola voce nascosta, inclusi i sistemi operativi secondari e le immagini WinRE.",
            "Non apporta alcuna modifica: sicuro da eseguire in qualsiasi momento.",
            "Indispensabile per verificare se il percorso di WinRE (`device ramdisk=[...]`) è intatto."
        ],
        "cons": [
            "Produce un output testuale lungo che richiede competenze tecniche per essere interpretato."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Lettura)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-4",
        "num": 4,
        "is_original": True,
        "category": "boot",
        "name": "bcdedit /set {default} recoveryenabled Yes",
        "command": "bcdedit /set {default} recoveryenabled Yes",
        "display_cmd": "bcdedit /set {default} recoveryenabled Yes",
        "icon": "shield-check",
        "short_desc": "Abilita l'ambiente di ripristino automatico nel Boot Loader predefinito.",
        "full_desc": "Forza Windows ad attivare la schermata di ripristino e troubleshooting automatico (WinRE) in caso di mancato avvio consecutivo. Evita che il sistema rimanga bloccato in una sequenza infinita di schermate blu senza dare opzioni di recupero.",
        "pros": [
            "Garantisce che Windows offra il menu di avvio avanzato (Modalità provvisoria, Prompt comandi, Disinstallazione aggiornamenti) in caso di crash.",
            "Risolve le situazioni in cui il menu di emergenza era stato disattivato da malware o script di ottimizzazione aggressivi.",
            "Esecuzione istantanea senza bloccare il sistema."
        ],
        "cons": [
            "Se l'immagine WinRE è fisicamente mancante o corrotta, potrebbe visualizzare un errore 0xc000000e all'avvio."
        ],
        "risk": "safe",
        "risk_label": "Raccomandato",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-5",
        "num": 5,
        "is_original": True,
        "category": "boot",
        "name": "bootsect /nt60 sys",
        "command": "bootsect /nt60 sys /force",
        "display_cmd": "bootsect /nt60 sys",
        "icon": "lifebuoy",
        "short_desc": "Ripara e riscrive il settore di avvio compatibile con BOOTMGR.",
        "full_desc": "Aggiorna il codice del settore di avvio principale (Master Boot Code) per le partizioni di sistema, rendendole compatibili con BOOTMGR (l'architettura di avvio introdotta da Vista e usata fino a Windows 11). Ripara il volume di sistema ripristinando il codice di boot.",
        "pros": [
            "Risolve errori del tipo 'BOOTMGR is missing', 'Operating System not found' o partizione di sistema non riconosciuta.",
            "Non tocca le tabelle delle partizioni né i file utente, sovrascrive solo il boot sector binario standard.",
            "Velocissimo (meno di 2 secondi)."
        ],
        "cons": [
            "In sistemi UEFI puri moderni con partizione EFI (ESP) e schema GPT, il problema di boot potrebbe richiedere `bcdboot` anziché solo `bootsect`.",
            "L'argomento `/force` smonta temporaneamente il volume per un istante."
        ],
        "risk": "medium",
        "risk_label": "Intervento Boot",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-6",
        "num": 6,
        "is_original": True,
        "category": "boot",
        "name": "reagentc /info",
        "command": "reagentc /info",
        "display_cmd": "reagentc /info",
        "icon": "refresh-circle",
        "short_desc": "Controlla lo stato e la posizione dell'ambiente di ripristino di Windows (WinRE).",
        "full_desc": "Interroga lo strumento di configurazione dell'ambiente di ripristino Windows. Fornisce: stato di WinRE (Enabled/Disabled), percorso fisico del file Winre.wim (`\\\\?\\GLOBALROOT\\device\\harddiskX\\partitionY`), indice immagine e identificatore BCD.",
        "pros": [
            "Diagnostica immediata per verificare se gli aggiornamenti di sicurezza WinRE (es. KB5034441) possono essere installati con successo.",
            "Completamente privo di rischi (operazione di sola lettura).",
            "Permette di verificare subito se la partizione di recovery è attiva o disattivata."
        ],
        "cons": [
            "Nessun contro. È una query informativa indispensabile."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Diagnostico)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-7",
        "num": 7,
        "is_original": True,
        "category": "boot",
        "name": "reagentc /enable",
        "command": "reagentc /enable",
        "display_cmd": "reagentc /enable",
        "icon": "checkbox-checked",
        "short_desc": "Abilita e registra l'ambiente di ripristino di Windows (WinRE).",
        "full_desc": "Attiva l'ambiente di ripristino Windows ricercando il file `Winre.wim` sia nella partizione riservata sia in `C:\\Windows\\System32\\Recovery`, registrandolo nel BCD. Risolve il noto problema 'Windows Recovery Environment disabilitato'.",
        "pros": [
            "Ripristina la capacità di usare 'Ripristino del PC', 'Ritorna alla build precedente' e gli strumenti avanzati di avvio.",
            "Risolve errori di fallimento aggiornamento Windows Update collegati alla partizione di recovery.",
            "Non causa rallentamenti o disservizi durante l'attivazione."
        ],
        "cons": [
            "Se la partizione di ripristino è troppo piccola (meno di 250 MB liberi) o il file Winre.wim è corrotto/assente, il comando fallirà con errore 2 o 'Impossibile trovare il file specificato'."
        ],
        "risk": "safe",
        "risk_label": "Raccomandato",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-8",
        "num": 8,
        "is_original": True,
        "category": "boot",
        "name": "shutdown /r /fw /t 0",
        "command": "shutdown /r /fw /t 2",
        "display_cmd": "shutdown /r /fw /t 0",
        "icon": "chip-bios",
        "short_desc": "Riavvia direttamente nel firmware BIOS/UEFI della scheda madre.",
        "full_desc": "Invia un segnale ACPI / EFI al firmware della scheda madre e forza un riavvio istantaneo bypassando la schermata di caricamento di Windows per entrare direttamente nel setup del BIOS/UEFI. Non serve premere forsennatamente Canc, F2 o F12 all'avvio.",
        "pros": [
            "Comodissimo su computer moderni con Fast Boot abilitato o tastiere Bluetooth che non rispondono prima del caricamento del sistema operativo.",
            "Elimina il tempismo manuale dei tasti funzione (F2/Del).",
            "Metodo ufficiale e pulito raccomandato da Microsoft."
        ],
        "cons": [
            "Riavvia il computer immediatamente: tutti i programmi aperti non salvati andranno persi.",
            "Funziona solo su schede madri UEFI native; su vecchi sistemi Legacy BIOS restituisce l'errore 'L'opzione di accesso al firmware non è supportata'."
        ],
        "risk": "medium",
        "risk_label": "Riavvio Diretto BIOS",
        "requires_admin": True,
        "needs_reboot": True,
        "interactive": False
    },
    {
        "id": "cmd-9",
        "num": 9,
        "is_original": True,
        "category": "diag",
        "name": "systeminfo",
        "command": "systeminfo",
        "display_cmd": "systeminfo",
        "icon": "info-circle",
        "short_desc": "Visualizza informazioni dettagliate e complete su hardware, SO e hotfix.",
        "full_desc": "Interroga le interfacce WMI ed esporta una panoramica esaustiva del PC: Versione build esatta di Windows 11, Data installazione, Tempo di attività (Uptime), Modello processore, BIOS date/version, Memoria RAM totale/disponibile, Schede di rete con MAC e IP, e la lista completa degli aggiornamenti Hotfix KB installati.",
        "pros": [
            "Nessuna modifica al sistema, 100% sicuro.",
            "Permette ai tecnici di identificare istantaneamente se una determinata patch di Windows Update è installata.",
            "Rileva se Hyper-V e la sicurezza basata sulla virtualizzazione (VBS) sono abilitate."
        ],
        "cons": [
            "Può impiegare da 5 a 15 secondi per enumerare tutti i componenti e gli hotfix."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Info)",
        "requires_admin": False,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-10",
        "num": 10,
        "is_original": True,
        "category": "diag",
        "name": "verifier",
        "command": "verifier /querysettings",
        "display_cmd": "verifier",
        "icon": "gears",
        "short_desc": "Esegue Verifica driver (Driver Verifier) per diagnosticare BSOD e driver instabili.",
        "full_desc": "Driver Verifier è lo strumento di debug kernel di Windows progettato per stressare i driver di terze parti e rilevare accessi illeciti alla memoria (Memory Leaks, IRQL not less or equal, buffer overflow), provocando un BSOD controllato con codice esatto per identificare il file .sys colpevole.",
        "pros": [
            "L'arma definitiva per trovare la causa esatta di schermate blu casuali (BSOD) causate da driver audio, GPU o periferiche nascoste.",
            "Strumento integrato nativo in Windows senza bisogno di software esterni."
        ],
        "cons": [
            "ATTENZIONE: Se impostato in modo troppo aggressivo, può causare un loop di riavvii BSOD che richiede l'avvio in modalità provvisoria per digitare `verifier /reset`.",
            "Rallenta leggermente le performance del sistema finché è attivo.",
            "Da usare con cautela solo durante sessioni di diagnosi mirata."
        ],
        "risk": "warning",
        "risk_label": "Avanzato / Con Cautela",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": True
    },

    # --- COMANDI EXTRA PER IL COLTELLINO SVIZZERO WINDOWS 11 ---

    # Categoria: Integrità File & DISM
    {
        "id": "cmd-11",
        "num": 11,
        "is_original": False,
        "category": "integrity",
        "name": "sfc /scannow",
        "command": "sfc /scannow",
        "display_cmd": "sfc /scannow",
        "icon": "shield-virus",
        "short_desc": "Scansiona e ripristina automaticamente i file di sistema corrotti o mancanti.",
        "full_desc": "System File Checker (SFC) scansiona tutti i file protetti del sistema operativo e sostituisce le versioni danneggiate o modificate con una copia cache valida memorizzata nella cartella compressa `%WinDir%\\System32\\dllcache` o nel WinSxS repository.",
        "pros": [
            "Risolve crash inspiegabili, errori di librerie DLL mancanti, malfunzionamenti del menu Start e crash di Explorer.",
            "Non altera le configurazioni personali o i documenti.",
            "Genera un report dettagliato in `C:\\Windows\\Logs\\CBS\\CBS.log`."
        ],
        "cons": [
            "La scansione richiede da 5 a 15 minuti a seconda della velocità del disco e della CPU.",
            "Se l'archivio dei componenti di origine (WinSxS) è anch'esso corrotto, SFC fallirà con messaggio 'Impossibile ripristinare alcuni file' (in tal caso occorre eseguire prima DISM)."
        ],
        "risk": "safe",
        "risk_label": "Fondamentale",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-12",
        "num": 12,
        "is_original": False,
        "category": "integrity",
        "name": "DISM RestoreHealth",
        "command": "DISM /Online /Cleanup-Image /RestoreHealth",
        "display_cmd": "DISM /Online /Cleanup-Image /RestoreHealth",
        "icon": "wrench-screwdriver",
        "short_desc": "Ripara l'archivio componenti di Windows scaricando copie sane da Windows Update.",
        "full_desc": "Deployment Image Servicing and Management (DISM) controlla il Component Store (cartella WinSxS). In caso di file corrotti, contatta i server ufficiali di Microsoft Windows Update per scaricare i pacchetti sani e riparare l'immagine di Windows attiva.",
        "pros": [
            "Risolve le corruzioni profonde del sistema operativo che SFC non riesce a correggere da solo.",
            "Ripara la base su cui si poggiano tutti gli aggiornamenti di Windows.",
            "Fornisce la massima affidabilità prima di eseguire un successivo `sfc /scannow`."
        ],
        "cons": [
            "Richiede una connessione Internet attiva e stabile per scaricare i file sostitutivi da Microsoft.",
            "Può impiegare dai 10 ai 25 minuti e sembrare bloccato al 62.3% per alcuni minuti (comportamento normale)."
        ],
        "risk": "safe",
        "risk_label": "Fondamentale",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-13",
        "num": 13,
        "is_original": False,
        "category": "integrity",
        "name": "DISM CheckHealth",
        "command": "DISM /Online /Cleanup-Image /CheckHealth",
        "display_cmd": "DISM /Online /Cleanup-Image /CheckHealth",
        "icon": "heart-pulse",
        "short_desc": "Verifica rapida dello stato di corruzione dell'immagine senza modifiche.",
        "full_desc": "Esegue un controllo istantaneo del flag di corruzione dell'immagine di Windows registrato nel registro di sistema. Non effettua una scansione esaustiva di ogni byte ma riporta subito se l'immagine è contrassegnata come danneggiata o riparabile.",
        "pros": [
            "Istantaneo: richiede meno di 5 secondi.",
            "Nessuna scrittura su disco o rischio per il sistema.",
            "Ottimo pre-check per sapere se serve RestoreHealth."
        ],
        "cons": [
            "Non rileva corruzioni recenti non ancora registrate nei log di manutenzione di sistema."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Rapido)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-14",
        "num": 14,
        "is_original": False,
        "category": "integrity",
        "name": "DISM ComponentCleanup",
        "command": "DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase",
        "display_cmd": "DISM /Cleanup-Image /StartComponentCleanup /ResetBase",
        "icon": "trash-can",
        "short_desc": "Pulisce l'archivio WinSxS eliminando versioni precedenti e obsolete dei componenti.",
        "full_desc": "Rimuove tutte le versioni precedenti dei componenti di sistema rimpiazzati da nuovi aggiornamenti cumulativi. Il parametro `/ResetBase` rimuove le basi di ripristino intermedie liberando molteplici Gigabyte di spazio su disco su Windows 11.",
        "pros": [
            "Libera tipicamente da 3 a 10 GB di spazio prezioso sulla partizione C:.",
            "Velocizza i controlli futuri di SFC e DISM riducendo la dimensione di WinSxS.",
            "Elimina file orfani accumulati da mesi di aggiornamenti."
        ],
        "cons": [
            "Non sarà più possibile disinstallare gli aggiornamenti di Windows installati precedentemente alla pulizia.",
            "Operazione con elevato I/O su disco (può richiedere 10-20 minuti)."
        ],
        "risk": "medium",
        "risk_label": "Pulizia Profonda",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },

    # Categoria: Rete & Connettività
    {
        "id": "cmd-15",
        "num": 15,
        "is_original": False,
        "category": "network",
        "name": "netsh winsock reset",
        "command": "netsh winsock reset",
        "display_cmd": "netsh winsock reset",
        "icon": "plug-circle-bolt",
        "short_desc": "Ripristina il catalogo Winsock allo stato originale pulito.",
        "full_desc": "Reimposta la configurazione delle API Windows Sockets (Winsock). Spesso software VPN di terze parti, antivirus disinstallati male o malware inseriscono Layered Service Provider (LSP) corrotti nel catalogo di rete impedendo a qualsiasi browser o applicazione di comunicare con Internet.",
        "pros": [
            "Risolve il classico errore 'Connesso senza Internet', crash delle connessioni DNS e problemi di socket non validi.",
            "Risolve conflitti causati da vecchi client VPN, proxy o firewall di terze parti.",
            "Operazione quasi istantanea."
        ],
        "cons": [
            "Richiede il riavvio del PC per rendere effettivo il nuovo catalogo.",
            "Se si utilizzano VPN aziendali o software di cattura pacchetti (Wireshark), potrebbe essere necessario reinstallare o riparare i rispettivi adattatori virtuali."
        ],
        "risk": "medium",
        "risk_label": "Reset Rete (Riavvio)",
        "requires_admin": True,
        "needs_reboot": True,
        "interactive": False
    },
    {
        "id": "cmd-16",
        "num": 16,
        "is_original": False,
        "category": "network",
        "name": "netsh int ip reset",
        "command": "netsh int ip reset",
        "display_cmd": "netsh int ip reset",
        "icon": "network-wired",
        "short_desc": "Reimposta completamente lo stack TCP/IPv4 e TCP/IPv6.",
        "full_desc": "Riscrive le chiavi di registro di sistema relative ai protocolli TCP/IP (`SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters`). Ripristina le tabelle di routing corrotte e azzera le configurazioni anomale della scheda di rete.",
        "pros": [
            "Risolve mancata assegnazione IP (es. indirizzi autoconfigurati 169.254.x.x).",
            "Ripara la navigazione se il computer non riesce più a comunicare con il gateway predefinito del router.",
            "Pulisce impostazioni di rete compromesse da driver malfunzionanti."
        ],
        "cons": [
            "Reimposta eventuali indirizzi IP statici manuali in DHCP automatico.",
            "Richiede il riavvio della macchina."
        ],
        "risk": "medium",
        "risk_label": "Reset IP (Riavvio)",
        "requires_admin": True,
        "needs_reboot": True,
        "interactive": False
    },
    {
        "id": "cmd-17",
        "num": 17,
        "is_original": False,
        "category": "network",
        "name": "ipconfig /flushdns",
        "command": "ipconfig /flushdns",
        "display_cmd": "ipconfig /flushdns",
        "icon": "broom",
        "short_desc": "Svuota e ricostruisce la cache del resolver DNS di Windows.",
        "full_desc": "Cancella tutte le voci memorizzate nella cache del servizio client DNS locale. Forza il sistema a interrogare nuovamente i server DNS configurati per ottenere i record IP aggiornati dei siti web e dei server.",
        "pros": [
            "Risolve errori di 'Sito non raggiungibile' o 'DNS_PROBE_FINISHED_NXDOMAIN' quando un sito ha cambiato server o indirizzo IP.",
            "Non interrompe i download o le connessioni aperte.",
            "Esecuzione immediata (frazioni di secondo)."
        ],
        "cons": [
            "Nessun effetto collaterale: è una delle operazioni di manutenzione più innocue e sicure in assoluto."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Istantaneo)",
        "requires_admin": False,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-18",
        "num": 18,
        "is_original": False,
        "category": "network",
        "name": "Rilascio e Rinnovo DHCP IP",
        "command": "powershell -Command \"ipconfig /release; ipconfig /renew\"",
        "display_cmd": "ipconfig /release & renew",
        "icon": "arrows-rotate",
        "short_desc": "Rilascia e richiede una nuova configurazione IP al router DHCP.",
        "full_desc": "Invia una notifica DHCPRELEASE per liberare l'indirizzo IP assegnato sulla scheda di rete corrente, quindi esegue DHCPREQUEST per richiedere un lease pulito al modem/router locale.",
        "pros": [
            "Risolve conflitti di indirizzi IP doppi sulla rete locale LAN o Wi-Fi.",
            "Riassegna gateway e server DNS corretti se il router è stato appena riavviato."
        ],
        "cons": [
            "Interrompe brevemente (per 3-5 secondi) la connessione a Internet prima di ripristinarla."
        ],
        "risk": "safe",
        "risk_label": "Sicuro",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },

    # Categoria: Dischi, FS & Storage
    {
        "id": "cmd-19",
        "num": 19,
        "is_original": False,
        "category": "disk",
        "name": "chkdsk C: /scan",
        "command": "chkdsk C: /scan",
        "display_cmd": "chkdsk C: /scan",
        "icon": "magnifying-glass-chart",
        "short_desc": "Scansione del file system NTFS/ReFS in tempo reale senza smontare il volume.",
        "full_desc": "Esegue un controllo diagnostico online del file system del disco C:. Rileva descrittori di sicurezza non validi, record di file orfani e indici non sincronizzati senza richiedere il riavvio o il blocco dell'accesso ai file.",
        "pros": [
            "Funziona a caldo mentre continui a usare Windows 11.",
            "Non richiede riavvio a differenza di chkdsk /f /r.",
            "Se trova problemi riparabili online, li corregge istantaneamente."
        ],
        "cons": [
            "Se rileva corruzioni gravi richiederà una successiva scansione offline `/spotfix` o `/f` al riavvio."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Online)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-20",
        "num": 20,
        "is_original": False,
        "category": "disk",
        "name": "defrag C: /O",
        "command": "defrag C: /O /U /V",
        "display_cmd": "defrag C: /O",
        "icon": "bolt-lightning",
        "short_desc": "Esegue l'ottimizzazione ideale per il supporto: TRIM su SSD o deframmentazione su HDD.",
        "full_desc": "Rileva automaticamente la tipologia del disco. Per le unità a stato solido SSD (NVMe / SATA) invia i comandi TRIM per notificare al controller i blocchi di memoria non più in uso, ripristinando le massime velocità di scrittura; per gli Hard Disk tradizionali esegue la deframmentazione e compattazione dei file.",
        "pros": [
            "Allunga la vita degli SSD e previene il degrado delle prestazioni di scrittura sequenziale e casuale.",
            "Usa il motore di ottimizzazione nativo certificato Microsoft.",
            "Sicuro da eseguire anche settimanalmente."
        ],
        "cons": [
            "Non deframmenta gli SSD (perché li usurerebbe), applica invece giustamente solo TRIM."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Consigliato)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-21",
        "num": 21,
        "is_original": False,
        "category": "disk",
        "name": "compact /compactos:query",
        "command": "compact /compactos:query",
        "display_cmd": "compact /compactos:query",
        "icon": "compress",
        "short_desc": "Verifica se la compressione di sistema CompactOS è attiva su Windows 11.",
        "full_desc": "Interroga lo stato di CompactOS. Questa funzionalità comprime i binari del sistema operativo e le librerie con algoritmi XPRESS/LZX trasparenti, permettendo di recuperare da 2 a 4 GB di spazio senza impattare la velocità su CPU moderne.",
        "pros": [
            "Permette di capire subito se si può risparmiare spazio su disco sul drive di sistema.",
            "Nessun rischio, lettura immediata."
        ],
        "cons": [
            "Nessuno per la query."
        ],
        "risk": "safe",
        "risk_label": "Sicuro",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },

    # Categoria: Windows Update & Servizi
    {
        "id": "cmd-22",
        "num": 22,
        "is_original": False,
        "category": "update",
        "name": "Reset Windows Update Completo",
        "command": "powershell -Command \"Stop-Service -Name wuauserv, cryptSvc, bits, msiserver -Force -ErrorAction SilentlyContinue; if (Test-Path C:\\Windows\\SoftwareDistribution) { Rename-Item C:\\Windows\\SoftwareDistribution SoftwareDistribution.bak -Force -ErrorAction SilentlyContinue }; if (Test-Path C:\\Windows\\System32\\catroot2) { Rename-Item C:\\Windows\\System32\\catroot2 catroot2.bak -Force -ErrorAction SilentlyContinue }; Start-Service -Name wuauserv, cryptSvc, bits, msiserver; Write-Host 'Windows Update e Catroot2 resettati con successo!'\"",
        "display_cmd": "Reset-WindowsUpdate",
        "icon": "arrows-spin",
        "short_desc": "Risolve errori di Windows Update (0x80070002, 0x80240034) arrestando i servizi e azzerando la cache.",
        "full_desc": "Arresta i servizi Windows Update, Servizio di trasferimento intelligente in background (BITS), Servizi di crittografia e Windows Installer. Rinomina la cartella `SoftwareDistribution` (dove risiedono i download temporanei corrotti) e `catroot2`, riavviando infine i servizi puliti.",
        "pros": [
            "La soluzione definitiva quando gli aggiornamenti di Windows 11 rimangono bloccati allo 0%, falliscono con codici di errore criptici o tentano di riscaricarsi continuamente.",
            "Non elimina i file personali né i programmi.",
            "Crea un backup automatico .bak delle vecchie cartelle."
        ],
        "cons": [
            "La cronologia degli aggiornamenti installati nella schermata Impostazioni verrà azzerata (gli aggiornamenti rimangono comunque installati nel sistema).",
            "La successiva ricerca aggiornamenti potrebbe impiegare qualche minuto in più per ricaricare l'indice da Microsoft."
        ],
        "risk": "medium",
        "risk_label": "Riparazione Servizi",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-23",
        "num": 23,
        "is_original": False,
        "category": "update",
        "name": "USOClient StartScan",
        "command": "usoclient StartScan",
        "display_cmd": "usoclient StartScan",
        "icon": "magnifying-glass-arrow-right",
        "short_desc": "Forza Windows 11 a scansionare immediatamente i server per nuovi aggiornamenti.",
        "full_desc": "Comunica con l'Update Session Orchestrator (USO) per avviare una scansione attiva in background di nuovi aggiornamenti di sicurezza, driver e patch per Windows 11.",
        "pros": [
            "Avvia la verifica anche senza aprire la schermata Impostazioni di Windows.",
            "Silenzioso, non disturba le applicazioni in primo piano."
        ],
        "cons": [
            "Non fornisce output dettagliato a riga di comando (lavora come demone di sistema in background)."
        ],
        "risk": "safe",
        "risk_label": "Sicuro",
        "requires_admin": False,
        "needs_reboot": False,
        "interactive": False
    },

    # Categoria: Shell Win 11 & App Store
    {
        "id": "cmd-24",
        "num": 24,
        "is_original": False,
        "category": "shell",
        "name": "Riavvio Windows Explorer",
        "command": "powershell -Command \"Stop-Process -Name explorer -Force; Start-Process explorer\"",
        "display_cmd": "taskkill /f /im explorer.exe",
        "icon": "window-restore",
        "short_desc": "Riavvia la shell grafica di Windows: Barra delle applicazioni, Menu Start e Desktop.",
        "full_desc": "Termina forzatamente il processo `explorer.exe` e lo rilancia immediatamente. Risolve blocchi improvvisi della barra delle applicazioni di Windows 11, menu Start che non si apre, icone di notifica bloccate o finestre fantasma.",
        "pros": [
            "Risolve il 90% dei blocchi grafici dell'interfaccia senza dover riavviare l'intero PC.",
            "Istantaneo (impiega meno di 2 secondi).",
            "Mantiene aperte le altre applicazioni (browser, documenti Word, ecc.)."
        ],
        "cons": [
            "Le finestre di Esplora File precedentemente aperte verranno chiuse.",
            "Lo schermo lampeggerà per una frazione di secondo durante il riavvio della shell."
        ],
        "risk": "safe",
        "risk_label": "Riavvio Rapido GUI",
        "requires_admin": False,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-25",
        "num": 25,
        "is_original": False,
        "category": "shell",
        "name": "wsreset.exe",
        "command": "wsreset.exe",
        "display_cmd": "wsreset.exe",
        "icon": "bag-shopping",
        "short_desc": "Pulisce e reimposta la cache di Microsoft Store senza toccare le app installate.",
        "full_desc": "Apre una sessione di ripristino per svuotare il database temporaneo delle licenze e la cache del Microsoft Store di Windows 11. Risolve problemi di app bloccate in download o errori di aggiornamento delle applicazioni Store.",
        "pros": [
            "Risolve problemi di avvio o chiusura inaspettata del Microsoft Store.",
            "Non disinstalla alcuna applicazione o gioco precedentemente scaricato.",
            "Procedura ufficiale e sicura fornita direttamente da Microsoft."
        ],
        "cons": [
            "Apre una finestra di prompt nera temporanea per circa 15-30 secondi prima di avviare il nuovo Store."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Store)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-26",
        "num": 26,
        "is_original": False,
        "category": "shell",
        "name": "Re-registra App di Sistema Win 11",
        "command": "powershell -ExecutionPolicy Bypass -Command \"Get-AppXPackage -AllUsers | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register \\\"$($_.InstallLocation)\\AppXManifest.xml\\\" -ErrorAction SilentlyContinue}; Write-Host 'Ripristino App completato!'\"",
        "display_cmd": "Get-AppxPackage (Re-Register)",
        "icon": "boxes-stacked",
        "short_desc": "Reinstalla e registra tutte le applicazioni integrate di Windows 11 e il Menu Start.",
        "full_desc": "Effettua una re-registrazione forzata dei manifest XML di tutte le Universal Windows Platform (UWP) apps installate per tutti gli utenti: Impostazioni, Sicurezza di Windows, Calcolatrice, Foto, Menu Start, Centro notifiche e Widget.",
        "pros": [
            "Risolve casi gravi in cui le app native di Windows 11 o l'app Impostazioni non si aprono più o crashano all'istante.",
            "Non cancella i dati o le credenziali degli account.",
            "Ripristina i pacchetti corrotti ai percorsi di installazione predefiniti."
        ],
        "cons": [
            "Può impiegare 3-6 minuti per completare tutti i package.",
            "Durante l'esecuzione possono apparire messaggi di avviso non critici per app attualmente in uso."
        ],
        "risk": "medium",
        "risk_label": "Riparazione App UWP",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },

    # Categoria: Diagnostica & Hardware
    {
        "id": "cmd-27",
        "num": 27,
        "is_original": False,
        "category": "diag",
        "name": "Report Batteria PowerCFG",
        "command": "powershell -Command \"powercfg /batteryreport /output C:\\battery-report.html; Write-Host 'Report generato in C:\\battery-report.html'; Start-Process C:\\battery-report.html\"",
        "display_cmd": "powercfg /batteryreport",
        "icon": "battery-three-quarters",
        "short_desc": "Genera un report HTML completo sullo stato di salute della batteria del portatile.",
        "full_desc": "Analizza i dati storici del controller ACPI della batteria del portatile e genera un documento HTML dettagliato: Capacità di progetto (Design Capacity), Capacità a piena carica attuale (Full Charge Capacity), Conteggio cicli di ricarica e cronologia di utilizzo delle ultime settimane.",
        "pros": [
            "Permette di calcolare con precisione millimetrica l'usura reale (Battery Wear Level) della batteria.",
            "Genera una comoda pagina web HTML aperta in automatico nel browser.",
            "Indispensabile per diagnosticare laptop che si spengono all'improvviso o perdono carica rapidamente."
        ],
        "cons": [
            "Utile principalmente su computer portatili o tablet (sui PC desktop fissi senza gruppo di continuità WMI restituirà un avviso di assenza batteria)."
        ],
        "risk": "safe",
        "risk_label": "Sicuro (Report)",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-28",
        "num": 28,
        "is_original": False,
        "category": "diag",
        "name": "mdsched (Diagnostica Memoria RAM)",
        "command": "powershell -Command \"Start-Process mdsched.exe\"",
        "display_cmd": "mdsched.exe",
        "icon": "memory",
        "short_desc": "Pianifica il test hardware della memoria RAM al prossimo riavvio del PC.",
        "full_desc": "Apre lo Strumento Diagnostica Memoria Windows per effettuare una verifica a basso livello dei moduli RAM (test con pattern estesi, LRAND, MATS+) prima del caricamento di Windows.",
        "pros": [
            "Rileva banchi di memoria RAM difettosi o instabili che causano crash irreversibili, BSOD 'MEMORY_MANAGEMENT' o freeze casuali.",
            "Strumento ufficiale ad alta affidabilità integrato in Windows.",
            "Mostra i risultati dettagliati nel Visualizzatore Eventi al riavvio."
        ],
        "cons": [
            "Richiede il riavvio del sistema ed esegue il test fuori da Windows per 15-45 minuti durante i quali il PC non può essere utilizzato."
        ],
        "risk": "medium",
        "risk_label": "Test Hardware (Riavvio)",
        "requires_admin": True,
        "needs_reboot": True,
        "interactive": True
    },
    {
        "id": "cmd-29",
        "num": 29,
        "is_original": False,
        "category": "diag",
        "name": "gpupdate /force",
        "command": "gpupdate /force",
        "display_cmd": "gpupdate /force",
        "icon": "gears",
        "short_desc": "Aggiorna forzatamente tutti i Criteri di Gruppo locali e di dominio (GPO).",
        "full_desc": "Riapplica immediatamente tutti i criteri di gruppo (User Configuration e Computer Configuration). Risolve discrepanze di permessi, criteri di sicurezza bloccati o policy aziendali non allineate.",
        "pros": [
            "Evita di attendere l'intervallo di polling automatico di Windows (90-120 minuti).",
            "Risolve blocchi di accesso o impostazioni di sistema che 'non vogliono salvarsi'.",
            "Completamente non distruttivo."
        ],
        "cons": [
            "Se un criterio richiede la disconnessione o il riavvio per essere applicato (es. installazione software GPO), potrebbe chiederlo alla fine."
        ],
        "risk": "safe",
        "risk_label": "Sicuro",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    },
    {
        "id": "cmd-30",
        "num": 30,
        "is_original": False,
        "category": "boot",
        "name": "Riavvia in WinRE Subito",
        "command": "reagentc /boottore",
        "display_cmd": "reagentc /boottore",
        "icon": "arrows-turn-to-dots",
        "short_desc": "Configura il sistema per entrare direttamente nell'Ambiente di Ripristino (WinRE) al prossimo riavvio.",
        "full_desc": "Imposta un flag nel firmware e nel BCD per fare in modo che il prossimo avvio del computer salti il caricamento standard di Windows 11 e si avvii direttamente nella console WinRE, dove sono disponibili Ripristino immagine, Prompt CMD avanzato e Ripristino di sistema.",
        "pros": [
            "Soluzione perfetta per accedere alla console di ripristino senza dover tenere premuto Shift mentre si clicca Riavvia.",
            "Non riavvia subito la macchina ma prepara il riavvio quando l'utente è pronto.",
            "Garantisce l'accesso a WinRE anche se la tastiera non risponde nella schermata di login."
        ],
        "cons": [
            "Richiede che WinRE sia attivo e abilitato (`reagentc /info` abilitato)."
        ],
        "risk": "safe",
        "risk_label": "Preparazione WinRE",
        "requires_admin": True,
        "needs_reboot": False,
        "interactive": False
    }
]
