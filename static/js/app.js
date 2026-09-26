/**
 * WINDOWS 11 SWISS REPAIR TOOL - CLIENT JAVASCRIPT
 * Gestione interattiva categorie, ricerca, modali Pro & Contro,
 * streaming SSE della console terminale ed esportazione script.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Stato locale comandi
    let allCommands = [];
    let currentTaskEventSource = null;
    let activeModalCmdId = null;

    // Elementi DOM principali
    const searchInput = document.getElementById('searchInput');
    const btnClearSearch = document.getElementById('btnClearSearch');
    const categoryTabs = document.querySelectorAll('.cat-tab');
    const commandCards = document.querySelectorAll('.cmd-card');
    
    // Terminale
    const terminalPanel = document.getElementById('terminalPanel');
    const terminalHeader = document.getElementById('terminalHeader');
    const terminalOutput = document.getElementById('terminalOutput');
    const btnCloseTerminal = document.getElementById('btnCloseTerminal');
    const chevronIcon = document.getElementById('chevronIcon');
    const termToggleHint = document.getElementById('termToggleHint');
    const btnClearTerminal = document.getElementById('btnClearTerminal');
    const btnCopyTerminal = document.getElementById('btnCopyTerminal');
    const terminalIndicator = document.getElementById('terminalIndicator');
    const customCmdInput = document.getElementById('customCmdInput');
    const btnRunCustomCmd = document.getElementById('btnRunCustomCmd');

    // Modale Dettagli
    const detailsModal = document.getElementById('detailsModal');
    const btnCloseModal = document.getElementById('btnCloseModal');
    const btnModalCloseBottom = document.getElementById('btnModalCloseBottom');
    const modalNum = document.getElementById('modalNum');
    const modalTitle = document.getElementById('modalTitle');
    const modalCmdSyntax = document.getElementById('modalCmdSyntax');
    const modalFullDesc = document.getElementById('modalFullDesc');
    const modalProsList = document.getElementById('modalProsList');
    const modalConsList = document.getElementById('modalConsList');
    const modalRiskBadge = document.getElementById('modalRiskBadge');
    const modalAdminReq = document.getElementById('modalAdminReq');
    const modalRebootReq = document.getElementById('modalRebootReq');
    const btnModalCopyCmd = document.getElementById('btnModalCopyCmd');
    const btnModalRun = document.getElementById('btnModalRun');

    // Rilancio Admin & Dropdown Esportazione
    const btnRelaunchAdmin = document.getElementById('btnRelaunchAdmin');
    const btnExportMenu = document.getElementById('btnExportMenu');
    const btnOpenInBrowser = document.getElementById('btnOpenInBrowser');

    if (btnOpenInBrowser) {
        btnOpenInBrowser.addEventListener('click', () => {
            fetch('/api/open-external-browser', { method: 'POST' })
                .then(res => res.json())
                .then(() => {
                    showToast("Apertura nel browser predefinito completata!", "success");
                })
                .catch(() => {
                    window.open(window.location.href, '_blank');
                });
        });
    }

    // =========================================================================
    // CENTRATURA DELLA FINESTRA APPLICAZIONE SULLO SCHERMO
    // =========================================================================
    try {
        if (window.screen && window.screen.availWidth) {
            const availW = window.screen.availWidth;
            const availH = window.screen.availHeight;
            const targetW = Math.min(1560, Math.floor(availW * 0.90));
            const targetH = Math.min(960, Math.floor(availH * 0.90));
            const posX = Math.max(0, Math.floor((availW - targetW) / 2));
            const posY = Math.max(0, Math.floor((availH - targetH) / 2));
            window.resizeTo(targetW, targetH);
            window.moveTo(posX, posY);
        }
    } catch (e) {
        // Nessun blocco se non consentito dal motore
    }

    // =========================================================================
    // ARRESTO AUTOMATICO ALLA CHIUSURA DELLA FINESTRA
    // =========================================================================
    // Invia un battito ogni 2 secondi per confermare che l'applicazione è attiva
    setInterval(() => {
        fetch('/api/heartbeat', { method: 'POST' }).catch(() => {});
    }, 2000);

    // Quando l'utente chiude la finestra (X), invia segnale di shutdown immediato
    window.addEventListener('beforeunload', () => {
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/shutdown');
        } else {
            fetch('/api/shutdown', { method: 'POST', keepalive: true }).catch(() => {});
        }
    });

    // =========================================================================
    // CARICAMENTO INFORMAZIONI E COMANDI DAL SERVER
    // =========================================================================
    fetch('/api/commands')
        .then(res => res.json())
        .then(data => {
            allCommands = data.commands || [];
            // Inizializza filtro predefinito (Tutti i 30 comandi)
            applyFilters();
        })
        .catch(err => {
            console.error("Errore nel caricamento del catalogo comandi:", err);
            showToast("Errore di connessione al backend", "error");
        });

    // =========================================================================
    // FILTRAGGIO CATEGORIE & RICERCA IN TEMPO REALE
    // =========================================================================
    let selectedCategory = 'all'; // Predefinito: Tutti i 30 comandi

    categoryTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            categoryTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            selectedCategory = tab.dataset.category;
            applyFilters();
        });
    });

    searchInput.addEventListener('input', () => {
        if (searchInput.value.trim().length > 0) {
            btnClearSearch.style.display = 'block';
        } else {
            btnClearSearch.style.display = 'none';
        }
        applyFilters();
    });

    btnClearSearch.addEventListener('click', () => {
        searchInput.value = '';
        btnClearSearch.style.display = 'none';
        applyFilters();
        searchInput.focus();
    });

    function applyFilters() {
        const query = searchInput.value.toLowerCase().trim();

        commandCards.forEach(card => {
            const cardId = card.id;
            const cmdObj = allCommands.find(c => c.id === cardId);
            if (!cmdObj) return;

            // Filtro Categoria
            let matchesCategory = false;
            if (selectedCategory === 'all') {
                matchesCategory = true;
            } else {
                matchesCategory = cmdObj.category === selectedCategory;
            }

            // Filtro Ricerca
            let matchesSearch = true;
            if (query.length > 0) {
                const searchString = `${cmdObj.name} ${cmdObj.display_cmd} ${cmdObj.command} ${cmdObj.short_desc} ${cmdObj.full_desc} ${cmdObj.pros.join(' ')} ${cmdObj.cons.join(' ')}`.toLowerCase();
                matchesSearch = searchString.includes(query);
            }

            if (matchesCategory && matchesSearch) {
                card.style.display = 'grid';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // =========================================================================
    // GESTIONE EVENTI SULLE CARD DEI COMANDI
    // =========================================================================
    document.getElementById('commandsGrid').addEventListener('click', (e) => {
        const btnRun = e.target.closest('.btn-run');
        const btnCopy = e.target.closest('.btn-copy');
        const btnInfo = e.target.closest('.btn-info');

        if (btnRun) {
            const cmdId = btnRun.dataset.id;
            executeCommand(cmdId);
        } else if (btnCopy) {
            const cmdText = btnCopy.dataset.cmd;
            copyToClipboard(cmdText, "Comando copiato negli appunti!");
        } else if (btnInfo) {
            const cmdId = btnInfo.dataset.id;
            openDetailsModal(cmdId);
        }
    });

    // =========================================================================
    // MODALE PRO & CONTRO
    // =========================================================================
    function openDetailsModal(cmdId) {
        const cmd = allCommands.find(c => c.id === cmdId);
        if (!cmd) return;

        activeModalCmdId = cmdId;
        modalNum.textContent = `#${cmd.num}`;
        modalTitle.textContent = cmd.name;
        modalCmdSyntax.textContent = cmd.command;
        modalFullDesc.textContent = cmd.full_desc;

        // Lista PRO
        modalProsList.innerHTML = '';
        cmd.pros.forEach(pro => {
            const li = document.createElement('li');
            li.textContent = pro;
            modalProsList.appendChild(li);
        });

        // Lista CONTRO
        modalConsList.innerHTML = '';
        cmd.cons.forEach(con => {
            const li = document.createElement('li');
            li.textContent = con;
            modalConsList.appendChild(li);
        });

        // Metadati & Rischio
        modalRiskBadge.textContent = cmd.risk_label;
        modalRiskBadge.className = `badge-risk risk-${cmd.risk}`;
        modalAdminReq.textContent = cmd.requires_admin ? "SI (Richiede UAC)" : "NO (Eseguibile da Utente)";
        modalRebootReq.textContent = cmd.needs_reboot ? "SI (Richiede Riavvio del Sistema)" : "NO";

        detailsModal.classList.add('show');
    }

    function closeDetailsModal() {
        detailsModal.classList.remove('show');
        activeModalCmdId = null;
    }

    btnCloseModal.addEventListener('click', closeDetailsModal);
    btnModalCloseBottom.addEventListener('click', closeDetailsModal);
    detailsModal.addEventListener('click', (e) => {
        if (e.target === detailsModal) closeDetailsModal();
    });

    btnModalCopyCmd.addEventListener('click', () => {
        if (activeModalCmdId) {
            const cmd = allCommands.find(c => c.id === activeModalCmdId);
            if (cmd) copyToClipboard(cmd.command, "Comando copiato negli appunti!");
        }
    });

    btnModalRun.addEventListener('click', () => {
        if (activeModalCmdId) {
            executeCommand(activeModalCmdId);
            closeDetailsModal();
        }
    });

    // =========================================================================
    // ESECUZIONE COMANDI & STREAMING TERMINALE SSE
    // =========================================================================
    function executeCommand(cmdId, customCmd = null) {
        // Mostra ed espande il pannello del terminale se minimizzato
        toggleTerminal(true);
        terminalIndicator.textContent = "IN ESECUZIONE...";
        terminalIndicator.style.background = "rgba(245, 158, 11, 0.25)";
        terminalIndicator.style.borderColor = "var(--neon-amber)";
        terminalIndicator.style.color = "var(--neon-amber)";

        // Chiude eventuale streaming precedente
        if (currentTaskEventSource) {
            currentTaskEventSource.close();
            currentTaskEventSource = null;
        }

        const payload = {};
        if (cmdId) payload.id = cmdId;
        if (customCmd) payload.custom_cmd = customCmd;

        appendTerminalLine(`\n-------------------------------------------------------------`, "term-gray");
        appendTerminalLine(`> [RICHIESTA] Inizializzazione comando in corso...`, "term-cyan");

        fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                appendTerminalLine(`[ERRORE] ${data.error}`, "term-err");
                resetTerminalIndicator(false);
                return;
            }

            const taskId = data.task_id;
            // Connessione Server-Sent Events per ricevere lo streaming dei caratteri
            currentTaskEventSource = new EventSource(`/api/stream/${taskId}`);

            currentTaskEventSource.onmessage = (event) => {
                if (event.data === "[DONE]") {
                    currentTaskEventSource.close();
                    currentTaskEventSource = null;
                    resetTerminalIndicator(true);
                    return;
                }

                try {
                    const parsed = JSON.parse(event.data);
                    if (parsed.text) {
                        let line = parsed.text;
                        let lineClass = "";
                        if (line.includes("[SUCCESS]")) lineClass = "term-cyan";
                        else if (line.includes("[WARN]")) lineClass = "term-warn";
                        else if (line.includes("[ERROR]") || line.includes("[EXIT]")) lineClass = "term-err";
                        
                        appendTerminalLine(line, lineClass);
                    }
                } catch (err) {
                    appendTerminalLine(event.data);
                }
            };

            currentTaskEventSource.onerror = (err) => {
                console.error("Errore SSE:", err);
                if (currentTaskEventSource) {
                    currentTaskEventSource.close();
                    currentTaskEventSource = null;
                }
                resetTerminalIndicator(false);
            };
        })
        .catch(err => {
            appendTerminalLine(`[ECCEZIONE DI RETE] ${err}`, "term-err");
            resetTerminalIndicator(false);
        });
    }

    function appendTerminalLine(text, customClass = "") {
        const span = document.createElement('span');
        if (customClass) span.className = customClass;
        span.textContent = text;
        terminalOutput.appendChild(span);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    function resetTerminalIndicator(success = true) {
        terminalIndicator.textContent = success ? "COMPLETATO" : "TERMINATO";
        terminalIndicator.style.background = success ? "rgba(0, 255, 136, 0.2)" : "rgba(239, 68, 68, 0.2)";
        terminalIndicator.style.borderColor = success ? "var(--neon-green)" : "var(--neon-red)";
        terminalIndicator.style.color = success ? "var(--neon-green)" : "var(--neon-red)";
    }

    // Input da riga di comando personalizzata nel terminale
    btnRunCustomCmd.addEventListener('click', () => {
        const val = customCmdInput.value.trim();
        if (val) {
            executeCommand(null, val);
            customCmdInput.value = '';
        }
    });

    customCmdInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            btnRunCustomCmd.click();
        }
    });

    // =========================================================================
    // CONTROLLI TERMINALE (ESPANSIONE / RIDUZIONE A ICONA, PULIZIA, COPIA)
    // =========================================================================
    function toggleTerminal(forceOpen = null) {
        if (!terminalPanel) return;
        const isMin = terminalPanel.classList.contains('minimized');
        const shouldOpen = forceOpen !== null ? forceOpen : isMin;

        if (shouldOpen) {
            terminalPanel.classList.remove('minimized');
            if (chevronIcon) {
                chevronIcon.className = 'fa-solid fa-chevron-down';
            }
            if (btnCloseTerminal) {
                btnCloseTerminal.title = "Riduci a icona console";
            }
            if (termToggleHint) {
                termToggleHint.textContent = "(Clicca per ridurre)";
            }
        } else {
            terminalPanel.classList.add('minimized');
            if (chevronIcon) {
                chevronIcon.className = 'fa-solid fa-chevron-up';
            }
            if (btnCloseTerminal) {
                btnCloseTerminal.title = "Espandi console";
            }
            if (termToggleHint) {
                termToggleHint.textContent = "(Clicca per espandere)";
            }
        }
    }

    // Permette di cliccare sull'intera barra header per aprire/chiudere la console
    if (terminalHeader) {
        terminalHeader.addEventListener('click', (e) => {
            if (e.target.closest('#btnClearTerminal') || e.target.closest('#btnCopyTerminal')) {
                return;
            }
            toggleTerminal();
        });
    }

    if (btnCloseTerminal) {
        btnCloseTerminal.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleTerminal();
        });
    }

    if (btnClearTerminal) {
        btnClearTerminal.addEventListener('click', () => {
            terminalOutput.innerHTML = '';
            appendTerminalLine('[READY] Console pulita.\n', 'term-gray');
        });
    }

    if (btnCopyTerminal) {
        btnCopyTerminal.addEventListener('click', () => {
            const logText = terminalOutput.innerText;
            copyToClipboard(logText, "Log della console copiato negli appunti!");
        });
    }

    // =========================================================================
    // ELEVAZIONE AD AMMINISTRATORE (UAC)
    // =========================================================================
    if (btnRelaunchAdmin) {
        btnRelaunchAdmin.addEventListener('click', () => {
            if (confirm("Vuoi richiedere i privilegi di Amministratore per consentire l'esecuzione di comandi critici (SFC, DISM, BCDEDIT)?\n\nWindows mostrerà il prompt di Controllo Account Utente (UAC).")) {
                const originalHtml = btnRelaunchAdmin.innerHTML;
                btnRelaunchAdmin.disabled = true;
                btnRelaunchAdmin.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Elevazione UAC...';
                showToast("Richiesta UAC inviata. Conferma il prompt di Windows...", "info");

                const startAdminPolling = () => {
                    let attempts = 0;
                    const pollInterval = setInterval(() => {
                        attempts++;
                        fetch('/api/system-status')
                            .then(res => {
                                if (res.ok) return res.json();
                                throw new Error("Server in fase di riavvio");
                            })
                            .then(status => {
                                if (status && status.is_admin) {
                                    clearInterval(pollInterval);
                                    showToast("Privilegi di Amministratore attivati! Ricaricamento interfaccia...", "success");
                                    setTimeout(() => {
                                        window.location.reload();
                                    }, 600);
                                }
                            })
                            .catch(() => {
                                // Normale: il server standard sta chiudendo e il server amministratore si sta avviando
                            });

                        if (attempts > 35) {
                            clearInterval(pollInterval);
                            window.location.reload();
                        }
                    }, 800);
                };

                fetch('/api/relaunch-admin', { method: 'POST' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            showToast(data.message, "success");
                            startAdminPolling();
                        } else {
                            showToast(`Errore: ${data.error}`, "error");
                            btnRelaunchAdmin.disabled = false;
                            btnRelaunchAdmin.innerHTML = originalHtml;
                        }
                    })
                    .catch(err => {
                        // Se la richiesta va in errore di rete perché il vecchio server si è chiuso istantaneamente,
                        // avviamo comunque il polling per agganciare il nuovo server elevato
                        startAdminPolling();
                    });
            }
        });
    }

    // =========================================================================
    // ESPORTAZIONE SCRIPT RESCUE (.BAT & .PS1)
    // =========================================================================
    btnExportMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        exportDropdown.classList.toggle('show');
    });

    document.addEventListener('click', () => {
        exportDropdown.classList.remove('show');
    });

    exportDropdown.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const format = link.dataset.format;
            const scope = link.dataset.scope; // 'original' o 'all'

            fetch('/api/export-script', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cmd_ids: [scope],
                    format: format
                })
            })
            .then(response => {
                if (!response.ok) throw new Error("Errore generazione script");
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Windows11_Repair_Suite_${scope}.${format}`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                showToast(`Script ${format.toUpperCase()} scaricato con successo!`, "success");
            })
            .catch(err => {
                showToast("Errore durante il download dello script", "error");
            });
        });
    });

    // =========================================================================
    // UTILITY: COPIA NEGLI APPUNTI & TOAST NOTIFICHE
    // =========================================================================
    function copyToClipboard(text, message = "Copiato negli appunti!") {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                showToast(message, "success");
            }).catch(() => fallbackCopy(text, message));
        } else {
            fallbackCopy(text, message);
        }
    }

    function fallbackCopy(text, message) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            showToast(message, "success");
        } catch (err) {
            showToast("Impossibile copiare automaticamente", "error");
        }
        document.body.removeChild(textArea);
    }

    function showToast(message, type = "success") {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `cyber-toast toast-${type}`;
        
        const icon = type === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    }
});
