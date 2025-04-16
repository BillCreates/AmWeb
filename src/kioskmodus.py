import argparse
import subprocess
import sys
import tempfile

from colored import red, green, magenta


def verbose_progress(msg, verbose):
    if verbose:
        print(f"[{green('*')}] {msg}")


def error(msg):
    print(f"[{red('*')}] {red(msg)}")


def verbose_error(msg, verbose):
    if verbose:
        print(f"{magenta(msg)}")


def create_service(url: str) -> str:
    return f"""
[Unit]
Description=Chromium Kiosk Mode for AmWeb
After=graphical.target

[Service]
ExecStart=/usr/bin/chromium --ozone-platform=wayland --kiosk {url}
Restart=always
User=fw_admin
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=WAYLAND_DISPLAY=wayland-0
Environment=XDG_SESSION_TYPE=wayland

[Install]
WantedBy=graphical.target
"""

def run(args):
    verbose = args.get("verbose", False)
    url = args.get("url", None)
    no_safe = args.get("no_safe", False)
    # user is not root at this point, so url.txt is owned by root
    if url is not None:
        verbose_progress(f"Url durch Argument übergeben: {url}", verbose)
        # url.txt updaten
        if not no_safe:
            verbose_progress("Url in 'url.txt' speichern.", verbose)
            with open("./url.txt", "w") as file:
                file.write(url)
    else:
        try:
            with open("./url.txt", "r") as file:
                url = file.read().strip()
                verbose_progress(f"Url aus url.txt gelesen: {url}", verbose)
        except FileNotFoundError as e:
            error("'url.txt' konnte nicht gefunden werden. Entweder erstellen Sie 'url.txt' mit der Url händisch oder führen amweb.py aus.")
            verbose_error(e, verbose)
            return

    # authenticate with sudo
    output = subprocess.run(["sudo", "-v"])
    if output.returncode != 0:
        error("Sudo Authentifizierung fehlgeschlagen.")
        verbose_error(output.stderr.decode().strip(), verbose)
        return False

    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(create_service(url))
            tmp_path = f.name
        verbose_progress("Schiebe temporäre Datei in /etc/systemd/system", verbose)
        output = subprocess.run(["sudo", "mv", tmp_path, "/etc/systemd/system/chromium-kiosk.service"], capture_output=True)
        if output.returncode != 0:
            error("Service-Datei konnte nicht verschoben werden.")
            verbose_error(output.stderr.decode() if output.stderr else "", verbose)
            return
        verbose_progress("Service Configdatei hinzugefügt.", verbose)
    except Exception as e:
        error("Systemd-Service-Datei konnte nicht geschrieben werden.")
        verbose_error(e, verbose)
        return

    verbose_progress("Service 'chromium-kiosk' aktivieren.", verbose)
    output = subprocess.run(["sudo", "systemctl", "enable", "chromium-kiosk"], capture_output=True)
    if output.returncode != 0:
        error("Service konnte nicht aktiviert werden.")
        verbose_error(output.stderr.decode() if output.stderr else "", verbose)
        return

    verbose_progress("Service daemon neu laden.", verbose)
    output = subprocess.run(["sudo", "systemctl", "daemon-reload"], capture_output=True)
    if output.returncode != 0:
        error("Service daemon konnte nicht neu geladen werden.")
        verbose_error(output.stderr.decode() if output.stderr else "", verbose)
        return

    verbose_progress("Service 'chromium-kiosk' starten.", verbose)
    output = subprocess.run(["sudo", "systemctl", "start", "chromium-kiosk"], capture_output=True)
    if output.returncode != 0:
        error("Service konnte nicht gestartet werden.")
        verbose_error(output.stderr.decode() if output.stderr else "", verbose)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="./kioskmodus.py", description="Kioskmodus für Raspberry Pi")
    parser.add_argument("url", type=str, nargs="?", default=None, help="Die Url, die im Kioskmodus geöffnet werden soll. Falls nicht gegben, wird die Url aus url.txt gelesen.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Zeigt mehr Informationen an.")
    parser.add_argument("--no-safe", action="store_true", help="Wenn die Url als Argument übergeben wird, wird standardmäßig url.txt damit überschrieben. Mit dieser Option wird dies deaktiviert.")
    args = parser.parse_args(sys.argv[1:])
    run(vars(args))