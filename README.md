# AMweb Setup
Scripte um den Alarmmonitor automatisch auf dem Raspberry Pi zu einzurichten und immer automatisch im Chrome Kioskmodus zu starten.

## Installation
```bash
git clone https://github.com/BillCreates/AmWeb.git # Klont das Repository
cd AmWeb                                           # In das Projektverzeichnis wechseln
python -m venv .venv                               # Erstellt ein virtuelles Environment in .venv/
source .venv/bin/activate                          # Aktiviert das virtuelle Environment
pip install --upgrade pip                          # Aktualisiert pip auf die neueste Version
pip install -r requirements.txt                    # Installiert die benötigten Python-Module
```

## Benutzung
```bash
./wlan_setup.sh
./amweb_setup.sh
```
Falls nötig, die Skripte zuerst ausführbar machen mit `chmod u+x wlan_setup.sh amweb_setup.sh`.

## WLAN Setup
Konfiguriert die WLAN-Verbindung des Raspberry Pi, damit dieser sich automatisch mit dem gewünschten WLAN verbindet.
Dafür wird die Umgebung gescannt und das Passwort für das gewählte WLAN abgefragt.

### Benutzung

```bash
./wlan_setup.py [-h] [-q] [-v] [-n NETWORK] [-p PASSWORD] [-a]
```

#### Optionen
- **`-h`, `--help`**: Zeigt die Hilfe an.
- **`-q`, `--quiet`**: Unterdrückt alle Ausgaben, bis auf intearktive Eingaben und Error.
- **`-v`, `--verbose`**: Zeigt zusätzliche Informationen bei Fehlern an (Error/Stacktraces).
- **`-n NETWORK`, `--network NETWORk`**: Gibt den Namen des WLANs an, mit dem sich der Raspberry Pi verbinden soll.
  Wenn kein Netzwerk angegeben wird, wird eine Liste aller verfügbaren Netzwerke angezeigt und der Benutzer kann eines auswählen.
- **`-p PASSWORD`, `--password PASSWORD`**: Gibt das Passwort für das WLAN an. Wird ignoriert, wenn `-n` nicht gegeben ist. Ist `-n` ohne `-p` gegeben, wird der Benutzer nach dem Passwort gefragt.
- **`-a`, `--auto-connect`**: Wenn angegeben, wird der Raspberry Pi automatisch mit dem angegebenen WLAN verbunden, ohne dass der Benutzer gefragt wird.
  Wird ignoriert, wenn `-n` nicht gegeben ist.

## AMweb Login
Startet einen Chromebrowser mit dem **Default**-Profil (damit der Local Storage bestehen bleibt) im headless-mode und navigiert auf die angegebene AMweb-Seite.  
Dort wird sich mit dem angegebenen Passwort angemeldet.
Da das Encryptionpasswortfeld nicht leer sein darf, wird hier im Moment `1234` eingegeben.
Unterstützung für ein indivuduelles Encryptionpasswort (welches nicht `""` ist) gibt es zurzeit nicht.  
Danach wird `WAIT_TIME` Millisekunden (standardmäßig 500ms) gewartet und dann überprüft, ob der Login erfolgreich war.

Zusätzlich wird die eingegebene Url in der Datei `url.txt` gespeichert, die dann von `kioskmodus.py` eingelesen wird.

### Benutzung

```bash
./amweb.py [-h] [-v] [-q] [--no-headless] [--debug-chrome-path] [--wait-time WAIT_TIME]
```

#### Optionen
- **`-h`, `--help`**: Zeigt die Hilfe an.

- **`-v`, `--verbose`**: Zeigt zusätzliche Informationen bei Fehlern an (Error/Stacktraces).

- **`-q`, `--quiet`**: Unterdrückt alle Ausgaben, bis auf intearktive Eingaben und Error.

- **`--no-headless`**: Startet Chrome nicht im headless Modus, sodass man sehen kann was passiert.

- **`--debug-chrome-path`**: Benutzt das Selenium Chrome Profil und dadurch einen anderen Pfad, der z.B. für Session Storage und Local Storage genutzt wird.
  Dadurch bleibt der Local Storage auch nicht zwischen Selenium-Läufen bestehen, was nützlich zum Debuggen sein kann.

- **`--wait-time WAIT_TIME`**: Gibt die Zeit in Millisekunden an, die nach Drücken des Login-Knopfes gewartet werden soll, bevor überprüft wird, ob der Login erfolgreich war.
  Standardmäßig sind es 500ms, bei langsamerer Internetverbindung kann dieser Wert erhöht werden.

## Kioskmodus
Richtet die Config-Dateien auf dem Raspberry Pi so ein, dass der Alarmmonitor immer im Chrome Kioskmodus gestartet wird.

Dafür wird die Url aus der Datei `url.txt` eingelesen. Die Url kann auch als Argument übergeben werden.

### Benutzung

```bash
./kioskmodus.py [-h] [-v] [--no-safe] [url]
```

#### Optionen
- **`-h`, `--help`**: Zeigt die Hilfe an.
- **`-v`, `--verbose`**: Zeigt zusätzliche Informationen bei Fehlern an (Error/Stacktraces).
- **`--no-safe`**: Wenn die Url als Argument übergeben wird, wird standardmäßig `url.txt` damit überschrieben. Mit dieser Option wird dies deaktiviert.

## Kiosk Spiegelung
Richtet eine Config-Dateien auf dem Raspberry Pi ein, womit bei jedem Start des Raspberry Pi beide HDMI Ausgänge gespeigelt werden.

### Benutzung

```bash
./setup-mirror.sh
```