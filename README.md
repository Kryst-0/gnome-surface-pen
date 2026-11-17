# Surface Pen per GNOME

Porting per GNOME Shell del plugin [omarchy-surface-pen](https://github.com/Kryst-0/omarchy-surface-pen), con cronologia Git condivisa. Repository derivato (fork del codice): GitHub non permette un fork nativo dello stesso repository nello stesso account personale, quindi questo repository non compare con il badge “forked from”.

Il pulsante superiore Bluetooth della Surface Pen apre app diverse con clic, doppio clic e pressione lunga. In presentazione, clic avanza e doppio clic torna indietro. Il pulsante laterale dello stilo e il supporto alla scrittura non vengono modificati. Non è un driver e non installa kernel o servizi privilegiati.

## Stato

Prima versione da collaudare su Fedora GNOME con la penna reale. Metadati predisposti per GNOME Shell 49, 50 e 51; non equivalgono a una verifica su tutte queste versioni. Su questa macchina Omarchy sono stati verificati sintassi, schema, pacchetto e logica automatizzata; GNOME Shell non è installato, quindi interfaccia, scorciatoie e input Wayland non sono ancora verificati in esecuzione. Non dichiarare compatibile una versione diversa disabilitando il controllo delle versioni.

## Installazione su Fedora GNOME

Il repository è privato: serve un account GitHub autorizzato. Per Fedora Workstation tradizionale (non Silverblue). Eseguire nella sessione grafica GNOME come utente normale:

```bash
sudo dnf install git gh python3 glib2 gnome-extensions-app
gh auth login
gh auth setup-git
gh repo clone Kryst-0/gnome-surface-pen
cd gnome-surface-pen
python3 build.py --install
```

Disconnettersi dalla sessione GNOME e rientrare. Poi:

```bash
gnome-extensions enable surface-pen@kryst-0.github.io
gnome-extensions prefs surface-pen@kryst-0.github.io
```

Il simbolo della penna appare nella barra superiore: dal menu si aprono preferenze e Bluetooth. Le preferenze consentono di cercare le app per i tre gesti, scegliere la modalità slide e modificare gli acceleratori. Predefiniti: Xournal++ per clic, LibreOffice Impress per doppio clic, nessuna app per pressione lunga. Le app vanno installate separatamente; se mancanti vengono indicate nelle preferenze. Il menu mostra l’ultimo gesto ricevuto, non lo stato della connessione Bluetooth.

Per creare soltanto il pacchetto ZIP: `python3 build.py`. Il risultato è `dist/surface-pen@kryst-0.github.io.shell-extension.zip`, installabile con `gnome-extensions install --force PERCORSO_DEL_FILE.zip`.

## Associazione e verifica

1. Associare il pulsante Bluetooth della penna dalle Impostazioni GNOME → Bluetooth (tenere premuto il pulsante superiore fino al lampeggio).
2. Scegliere tre app installate nelle preferenze, disattivare temporaneamente la modalità slide e provare i tre gesti.
3. Aprire una presentazione Impress a schermo intero (F5), selezionare modalità automatica e provare avanti e indietro. Verificare che non sposti la finestra.
4. Uscire dalla presentazione e verificare che i gesti tornino ad aprire le app. Provare anche la modalità “Sempre” con un lettore non riconosciuto e ripristinare “Automatica” al termine.
5. Disabilitare l’estensione e verificare che i tasti non siano più gestiti.

Modalità automatica: richiede una finestra a schermo intero e riconosce Impress, Papers, Evince, Okular, Atril, pdfpc, PDF di Firefox con `.pdf` nel titolo e titoli di comuni presentazioni web. Non può riconoscere ogni sito o PDF. In “Sempre”, i clic inviano frecce alla finestra attiva; la pressione lunga resta associata all’app scelta.

Le frecce vengono inviate tramite tastiera virtuale di Mutter, senza `xdotool`, `ydotool`, root o D-Bus Eval. L’invio attende il rilascio dei modificatori della penna e viene annullato se cambia la finestra attiva, cambia la modalità della shell o trascorrono 1,5 secondi. I tasti vengono gestiti solo nella sessione normale, non nella schermata di blocco.

## Scorciatoie e conflitti

| Gesto | Acceleratori predefiniti |
|---|---|
| Clic | `<Super>XF86AudioMicMute`, `<Super>F20`, `F20` |
| Doppio clic | `<Super>F19`, `F19` |
| Pressione lunga | `<Super>XF86Launch9`, `<Super>F18`, `F18` |

Alcuni layout traducono F20 in XF86AudioMicMute e F18 in XF86Launch9. Le varianti senza Super sono incluse per penne che non lo inviano. Sono scorciatoie globali, quindi valgono anche se generate da una normale tastiera. I tasti multimediali senza Super non vengono riservati. Le associazioni sono configurabili nelle preferenze usando acceleratori GTK separati da virgole; un campo vuoto disattiva quel gesto.

L’estensione non modifica le scorciatoie di sistema. Se GNOME o un’altra estensione occupa un acceleratore, risolvere il conflitto nelle relative impostazioni. Per vedere gli errori:

```bash
gnome-extensions info surface-pen@kryst-0.github.io
journalctl --user -b -o cat | rg 'Surface Pen|surface-pen|JS ERROR'
```

## Aggiornamento e rimozione

```bash
git pull --ff-only
python3 build.py --install
```

Disconnettersi e rientrare per caricare il nuovo codice.

```bash
gnome-extensions disable surface-pen@kryst-0.github.io
gnome-extensions uninstall surface-pen@kryst-0.github.io
```

Le preferenze GSettings rimangono. Per rimuoverle, prima della disinstallazione:

```bash
gsettings --schemadir "${XDG_DATA_HOME:-$HOME/.local/share}/gnome-shell/extensions/surface-pen@kryst-0.github.io/schemas" reset-recursively org.gnome.shell.extensions.surface-pen
```

## Sviluppo e origini

```bash
node --test tests/*.test.js
node --check extension.js
node --check prefs.js
python3 -m unittest discover -s tests -p 'test_*.py'
python3 build.py
```

Nessuna dipendenza npm. Node serve solo ai test. Le impostazioni GNOME sono indipendenti dal JSON Omarchy e non vengono importate automaticamente.

Riferimento protocollo del pulsante: https://github.com/qzed/linux-surface-pen-button-remap . Il codice del porting riprende il comportamento del progetto Omarchy; il riferimento esterno non viene vendorizzato.

API: [GNOME extensions](https://gjs.guide/extensions/), [GSettings](https://gjs.guide/extensions/development/preferences.html), [tastiera virtuale Mutter](https://mutter.gnome.org/clutter/method.VirtualInputDevice.notify_keyval.html).

Licenza MIT, come il progetto originale.
