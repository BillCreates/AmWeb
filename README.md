# AMweb
Script um den Alarmmonitor automatisch auf dem Raspberry Pi zu einzurichten.

## Funktionsweise
Startet einen Chromebrowser mit dem **Default**-Profil (damit der Local Storage bestehen bleibt) im headless-mode und navigiert auf die angegebene AMweb-Seite.  
Dort wird sich mit dem angegebenen Passwort angemeldet. 
Da das Encryptionpasswortfeld nicht leer sein darf, wird hier im Moment `1234` eingegeben.
Unterstützung für ein indivuduelles Encryptionpasswort (welches nicht `""` ist) gibt es zur Zeit nicht.  
Danach wird `WAIT_TIME` Millisekunden (standardmäßig 500ms) gewartet und dann überprüft, ob der Login erfolgreich war.

## Installation
```bash
git clone https://github.com/BillCreates/AmWeb.git # Klont das Repository
python -m venv .venv                               # Erstellt ein virtuelles Environment
.venv/bin/activate                                 # Aktiviert das virtuelle Environment
pip install -r requirements.txt                    # Installiert die benötigten Python-Module
```

**Das Script ausführbar machen**:
```bash
chmod u+x amweb.py
```

## Benutzung

```bash
 ./amweb.py [-h] [-v] [-q] [--no-headless] [--debug-chrome-path] [--wait-time WAIT_TIME]
```

### Optionen
- **`-h`, `--help`**: Zeigt die Hilfe an.

- **`-v`, `--verbose`**: Zeigt zusätzliche Infos bei Fehlern an (Stacktraces).

- **`-q`, `--quiet`**: Unterdrückt alle Ausgaben, bis auf intearktive Eingaben und Error.

- **`--no-headless`**: Startet Chrome nicht im headless Modus, sodass man sehen kann was passiert.

- **`--debug-chrome-path`**: Benutzt das Selenium Chrome Profil und dadurch einen anderen Pfad, der z.B. für Session Storage und Local Storage genutzt wird.
  Dadurch bleibt der Local Storage auch nicht zwischen Selenium-Läufen bestehen, was nützlich zum Debuggen sein kann.

- **`--wait-time WAIT_TIME`**: Gibt die Zeit in Millisekunden an, die nach Drücken des Login-Knopfes gewartet werden soll, bevor überprüft wird, ob der Login erfolgreich war.
  Standardmäßig sind es 500ms, bei langsamerer Internetverbindung kann dieser Wert erhöht werden.