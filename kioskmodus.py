#!.venv/bin/python3
import argparse
import sys
from termcolor import colored


def verbose_progress(msg, verbose):
    if verbose:
        print(f"[{colored('*', 'green')}] {msg}")


def error(msg):
    print(f"[{colored("*", "red")}] {colored(msg, "red")}")


def run(args):
    verbose = args.get("verbose", False)
    url = args.get("url", None)
    no_safe = args.get("no_safe", False)
    if url is not None:
        verbose_progress(f"URL durch Argument übergeben: {url}", verbose)
        # url.txt updaten
        if not no_safe:
            verbose_progress("URL in url.txt speichern.", verbose)
            with open("./url.txt", "w") as file:
                file.write(url)
    else:
        try:
            with open("./url.txt", "r") as file:
                url = file.read().strip()
                verbose_progress(f"URL aus url.txt gelesen: {url}", verbose)
        except FileNotFoundError:
            error("url.txt konnte nicht gefunden werden. Entweder erstellen Sie url.txt mit der URL händisch oder führen amweb.py aus.")
            return

    autostart = (f"@lxpanel --profile LXDE-pi\n"
                 f"@pcmanfm --desktop --profile LXDE-pi\n"
                 f"\n"
                 f"@xset s off\n"
                 f"@xset -dpms\n"
                 f"@xset s noblank\n"
                 f"\n"
                 f"@chromium-browser --kiosk {url}\n")

    with open("/etc/xdg/lxsession/LXDE-pi/autostart", "a") as file:
        file.write(autostart)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="./kioskmodus.py", description="Kioskmodus für Raspberry Pi")
    parser.add_argument("url", type=str, nargs="?", default=None, help="Die URL, die im Kioskmodus geöffnet werden soll. Falls nicht gegben, wird die URL aus url.txt gelesen.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Zeigt mehr Informationen an.")
    parser.add_argument("--no-safe", action="store_true", help="Wenn die URL als Argument übergeben wird, wird standardmäßig url.txt damit überschrieben. Mit dieser Option wird dies deaktiviert.")
    args = parser.parse_args(sys.argv[1:])
    run(vars(args))