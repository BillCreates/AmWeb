import subprocess
import sys
import re
import argparse
import time

from colored import red, green, magenta

def progress(msg, quiet):
    if not quiet:
        print(f"[{green('*')}] {msg}")


def error(msg):
    print(f"[{red('*')}] {red(msg)}")


def verbose_error(msg, verbose):
    if verbose:
        print(f"{magenta(msg)}")

def add_connection(ssid, password, verbose, quiet) -> bool:
    progress(f"Verbinde mit Netzwerk '{ssid}'...", quiet)
    output = subprocess.run([
        "sudo", "nmcli",                # networkmanager command as root
        "connection", "add",            # add a new connection
        "type", "wifi",                 # of type wifi
        "ifname", "wlan0",              # on the wlan0 interface
        "con-name", f"'{ssid}'",        # with the name of the ssid
        "ssid", f"'{ssid}'",            # and the ssid
        "wifi-sec.key-mgmt", "wpa-psk", # with wpa-psk key management
        "wifi-sec.psk", password        # and the password
    ], capture_output=True)
    if output.returncode != 0:
        error("Fehler bei der Verbindung zum Netzwerk")
        stderr = output.stderr.decode() if output.stderr else ""
        verbose_error(f"return code: {output.returncode}; stderr: {stderr}", verbose)
        return False

    # should autoconnect by default, but just in case
    output = subprocess.run([
        "sudo", "nmcli",
        "c", "modify", f"'{ssid}'",
        "connection.autoconnect", "yes"
    ], capture_output=True)
    if output.returncode != 0:
        error("Fehler beim Aktivieren der automatischen Verbindung")
        stderr = output.stderr.decode() if output.stderr else ""
        verbose_error(f"return code: {output.returncode}; stderr: {stderr}", verbose)
        return False

    progress(f"Netzwerk '{ssid}' erfolgreich hinzugefügt!", quiet)
    return True

def interactive(args) -> bool:
    verbose = args.get("verbose", False)
    quiet = args.get("quiet", False)
    progress("Suche nach verfügbaren Netzwerken...", quiet)
    # use iwlist instead of nmcli to force a rescan
    output = subprocess.run(["sudo", "iwlist", "wlan0", "scan"], capture_output=True)
    if output.returncode != 0:
        error("Fehler bei der Suche nach Netzwerken")
        stderr = output.stderr.decode() if output.stderr else ""
        verbose_error(f"return code: {output.returncode}; stderr: {stderr}", verbose)
        return False
    # https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists/7961425#7961425
    ssids = list(dict.fromkeys(re.findall(r"ESSID:\"(.+)\"", output.stdout.decode())))

    progress("Folgende Netzwerke wurden gefunden:", quiet)
    for (i, ssid) in enumerate(ssids):
        print(f"[{i + 1}] {ssid}")

    choice = input("Wählen Sie ein Netzwerk aus: ")

    try:
        choice = int(choice)
    except ValueError as e:
        error("Ungültige Eingabe")
        verbose_error(e, verbose)
        return False
    if choice < 1 or choice > len(ssids):
        error(f"Die Eingabe muss zwischen {1} und {len(ssids)} liegen")
        return False
    ssid = ssids[choice - 1]

    password = input("Geben Sie das Passwort ein: ")

    return add_connection(ssid, password, verbose, quiet)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="./wlan_setup.py", description="Wlan Setup für Raspberry Pi")
    parser.add_argument("-q", "--quiet", action="store_true", help="Nur nötige Ausgaben anzeigen")
    parser.add_argument("-v", "--verbose", action="store_true", help="Zeigt mehr Informationen an")
    parser.add_argument("-n", "--network", type=str, help="Der Name des Netzwerks, mit dem verbunden werden soll. Überspringt die interaktive Auswahl.")
    parser.add_argument("-p", "--password", type=str, help="Das Passwort des Netzwerks, mit dem verbunden werden soll. Setzt -n voraus.")

    args = parser.parse_args(sys.argv[1:])
    status = False
    if args.network is not None and args.password is not None:
        status = add_connection(args.network, args.password, args.verbose, args.quiet)
    else:
        status = interactive(vars(args))

    if not status:
        sys.exit(1)

    # reboot the system:
    # this closes the ssh connection instead of just hanging
    # and then automatically connects to the new network
    for i in range(5, -1, -1):
        print(f"Der Raspberry Pi wird in {i}s neugestartet...\r", end="")
        time.sleep(1)

    progress("\nsudo reboot", args.quiet)
    subprocess.run(["sudo", "reboot"])
