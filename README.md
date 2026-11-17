# Surface Pen per Omarchy

Plugin per la barra Omarchy (Quickshell) e Hyprland con configurazione Lua, con selettore delle app per clic, doppio clic e pressione lunga del pulsante superiore Bluetooth. Selezionare il gesto e fare clic su un'app: il salvataggio è immediato.

Predefiniti: Xournal++, LibreOffice Impress, Omawrite. In presentazione: clic = freccia destra, doppio clic = freccia sinistra. La modalità automatica richiede una finestra a schermo intero e riconosce Impress, lettori PDF comuni, PDF aperti in Firefox con `.pdf` nel titolo e presentazioni web dal titolo. Per altri programmi scegliere “Slide: sempre”; ritornare su automatico al termine. “Slide: disattivato” usa sempre le app configurate.

Configurazione: `~/.config/surface-pen/settings.json`. Il plugin non usa servizi privilegiati né cattura altri dispositivi di input. Le associazioni Hyprland sono SUPER+XF86AudioMicMute/F19/XF86Launch9 e F20/F19/F18 per varianti senza modificatore. I binding SUPER seguono la traduzione XKB di F20 in XF86AudioMicMute e di F18 in XF86Launch9; i binding per codici fisici non vengono usati perché questa versione di Hyprland li registra senza tasto. Questi tasti sono riservati anche se generati da un'altra tastiera. La penna invia già gesti distinti, quindi non serve un timer per distinguere i clic.

Fonte protocollo: https://github.com/qzed/linux-surface-pen-button-remap

Installazione idempotente: `python3 install.py`. I file personali modificati vengono salvati con suffisso `.bak.surface-pen-<timestamp>` alla prima installazione. Test: `python3 -m unittest discover -s . -p 'test_*.py'`.

Verifica sul dispositivo ancora necessaria: la penna risultava associata e trusted, ma disconnessa durante l'installazione. Premere il pulsante per risvegliarla, quindi provare i gesti e una presentazione F5 di Impress. Il pulsante laterale dello stilo non è il pulsante superiore Bluetooth e non viene modificato.

Rimozione: togliere la voce krysto.surface-pen da shell.json, le sei righe o.bind sotto il commento Surface Pen in bindings.lua, e la cartella del plugin. Eseguire `hyprctl reload` e `hyprctl configerrors`.


## Installazione da GitHub

Richiede Omarchy con Omarchy Shell, Hyprland Lua, Python 3, `gio` (glib2) e Bluetooth funzionante. Associare prima la penna dal pannello Bluetooth. Non installare questo plugin su GNOME.

```bash
git clone https://github.com/Kryst-0/omarchy-surface-pen.git
cd omarchy-surface-pen
python3 install.py
hyprctl reload
hyprctl configerrors
```

Il pannello appare nella barra e permette di scegliere app e modalità slide. Le app predefinite devono essere installate separatamente; si può scegliere qualunque app disponibile. Le impostazioni esistenti vengono conservate. Per aggiornare: `git pull --ff-only`, poi ripetere `python3 install.py` e i controlli Hyprland.

Porting GNOME derivato da questo progetto: [gnome-surface-pen](https://github.com/Kryst-0/gnome-surface-pen).
