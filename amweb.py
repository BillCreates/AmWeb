#!.venv/bin/python3

import argparse
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException, SessionNotCreatedException, InvalidArgumentException, \
    WebDriverException, ElementClickInterceptedException
from colored import red, green, magenta
import time


class Script:
    def __init__(self, args):
        self.verbose = args.get("verbose", False)
        self.quiet = args.get("quiet", False)
        self.no_headless = args.get("no_headless", False)
        self.debug_chrome_path = args.get("debug_chrome_path", False)
        self.wait_time = args.get("wait_time", 500) / 1000

        self.verbose_progress("Benutzername abrufen.")
        whoami = subprocess.run(["whoami"], capture_output=True)
        if whoami.returncode != 0:
            self.error("Fehler beim Abrufen des Benutzernamens.")
            return
        user = whoami.stdout.decode().strip()
        self.verbose_progress(f"Benutzername erfolgreich abgerufen: {user}")
        # TODO pfad auf linux testen
        default_chrome_path = f"/home/{user}/.config/google-chrome/" # for apple: /Users/{user}/Library/Application Support/Google/Chrome
        self.options = webdriver.ChromeOptions()
        if not self.debug_chrome_path:
            self.options.add_argument(f"--user-data-dir={default_chrome_path}")
            self.options.add_argument("--profile-directory=Default")
        if not self.no_headless:
            # set custom user agent, otherwise driver.quit() hangs
            self.options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)")
            self.options.add_argument("--headless=new")

    def verbose_error(self, msg):
        if self.verbose:
            print(f"{magenta(msg)}")

    def verbose_progress(self, msg):
        if self.verbose:
            print(f"[{green('*')}] {msg}")

    @staticmethod
    def error(msg):
        print(f"[{red('*')}] {red(msg)}")

    def progress(self, msg):
        if not self.quiet or self.verbose:
            print(f"[{green('*')}] {msg}")

    def run(self) -> bool:
        print("Tragen Sie die Url zum Webmonitor ein: ", end="")
        url = input()
        # save the url to a file, so it can be read by the kioskmode script
        with open("url.txt", "w") as file:
            file.write(url)
        print("Geben Sie das Passwort für den Webmonitor ein: ", end="")
        password = input()

        kill_command = ["pkill", "-i", "chrome"] # TODO command auf linux testen
        self.progress(f"Schließen aller Chrome Instanzen ({" ".join(kill_command)}).")
        output = subprocess.run(kill_command, capture_output=True)
        # 0 = success, 1 = no process found, 2 = invalid options, 3 = internal error
        if output.returncode == 2 or output.returncode == 3:
            self.error(f"Chrome konnte nicht geschlossen werden: pkill return code {output.returncode}.")
            return False
        self.progress("Chrome Instanzen erfolgreich geschlossen.")

        try:
            driver = webdriver.Chrome(options=self.options)
        except SessionNotCreatedException as e:
            self.error("Chrome konnte nicht gestartet werden.")
            self.verbose_error(e)
            return False

        self.progress("Chrome erfolgreich gestartet.")

        self.progress(f"Öffne Url '{url}'")
        try:
            driver.get(url)
        except (InvalidArgumentException, WebDriverException) as e:
            self.error("Ungültige Url. Bitte überprüfen Sie die Url.")
            self.verbose_error(e)
            driver.quit()
            return False
        self.progress(f"'{driver.title}' erfolgreich aufgerufen.")

        try:
            password_input = driver.find_element(By.ID, "authPassword")
            encrypt_pw_input = driver.find_element(By.ID, "decryptPassword")
            password_input.send_keys(password)
            encrypt_pw_input.send_keys("1234")
        except NoSuchElementException as e:
            self.error("Passwortfelder nicht gefunden. Bitte überprüfen Sie die Url und ob Sie nicht schon eingelogged sind.")
            self.verbose_error(e)
            driver.quit()
            return False
        except Exception as e:
            self.error("Unbekannter Fehler.")
            self.verbose_error(e)
            driver.quit()
            return False

        try:
            submit_button = driver.find_element(By.ID, "submit")
            submit_button.click()
        except NoSuchElementException as e:
            self.error("Log-In Knopf nicht gefunden. Bitte überprüfen Sie die Url und ob Sie nicht schon eingelogged sind.")
            self.verbose_error(e)
            driver.quit()
            return False
        except ElementClickInterceptedException as e:
            self.error("Log-In Knopf konnte nicht gedrückt werden.")
            self.verbose_error(e)
            driver.quit()
            return False

        time.sleep(self.wait_time)

        try:
            driver.find_element(By.ID, "authPassword")
            self.error("Falsches Passwort!")
            driver.quit()
            return False
        except NoSuchElementException:
            pass

        self.progress("Login erfolgreich!")

        driver.quit()
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="./amweb.py", description="Automatischer Login für den Webmonitor.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Zeigt zusätzlich Infos bei Fehlern an (z.B. Stacktrace).")
    parser.add_argument("-q", "--quiet", action="store_true", help="Unterdrückt alle Ausgaben, bis auf Fehler und interaktive Eingaben.")
    parser.add_argument("--no-headless", action="store_true", help="Startet Chrome nicht im Headless Modus. Nützlich für Debugging.")
    parser.add_argument("--debug-chrome-path", action="store_true", help="Benutzt das Chrome Profil von Selenium. Nützlich für Debugging.")
    # time to wait after login button has been pressed, before checking if it worked
    parser.add_argument("--wait-time", type=int, default=500, help="Wartezeit in ms nachdem der Login Knopf gedrückt wurde, bevor überprüft wird ob der Login erfolgreich war.")

    args = parser.parse_args(sys.argv[1:])

    if Script(vars(args)).run():
        sys.exit(0)
    else:
        sys.exit(1)
