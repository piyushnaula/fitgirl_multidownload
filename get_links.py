import requests, os, pyperclip
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, Style
class console:
    def __init__(self) -> None:
        self.colors = {"green": Fore.GREEN, "red": Fore.RED, "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA, "cyan": Fore.CYAN, "white": Fore.WHITE, "black": Fore.BLACK, "reset": Style.RESET_ALL, "lightblack": Fore.LIGHTBLACK_EX, "lightred": Fore.LIGHTRED_EX, "lightgreen": Fore.LIGHTGREEN_EX, "lightyellow": Fore.LIGHTYELLOW_EX, "lightblue": Fore.LIGHTBLUE_EX, "lightmagenta": Fore.LIGHTMAGENTA_EX, "lightcyan": Fore.LIGHTCYAN_EX, "lightwhite": Fore.LIGHTWHITE_EX}
    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")
    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    def success(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightgreen']}SUCC {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightgreen']}{obj}{self.colors['white']} {self.colors['reset']}")
    def error(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightred']}ERRR {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightred']}{obj}{self.colors['white']} {self.colors['reset']}")
    def done(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightmagenta']}DONE {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightmagenta']}{obj}{self.colors['white']} {self.colors['reset']}")
    def warning(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightyellow']}WARN {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightyellow']}{obj}{self.colors['white']} {self.colors['reset']}")
    def info(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightblue']}INFO {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightblue']}{obj}{self.colors['white']} {self.colors['reset']}")
    def custom(self, message, obj, color):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors[color.upper()]}{color.upper()} {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors[color.upper()]}{obj}{self.colors['white']} {self.colors['reset']}")
    def input(self, message):
        return input(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightcyan']}INPUT   {self.colors['lightblack']}• {self.colors['white']}{message}{self.colors['reset']}")
log = console()
log.clear()

url = log.input("Enter Fitgirl Game Link : ")

print("Select file hoster:")
print("  1. FuckingFast (fuckingfast.co)")
print("  2. DataNodes (datanodes.to)")
choice = log.input("Enter choice [1/2] (default 1): ").strip()

if choice == "2":
    host_prefix = "https://datanodes.to/"
    host_name = "DataNodes"
else:
    host_prefix = "https://fuckingfast.co/"
    host_name = "FuckingFast"

try:
    r = requests.get(url)
    r.raise_for_status()
except requests.exceptions.RequestException as e:
    log.error("HTTP request failed", f"{url} ({e})")
    raise SystemExit(1)

soup = BeautifulSoup(r.text, "html.parser")

links = [
    a["href"]
    for dlinks_div in soup.find_all("div", class_="dlinks")
    for a in dlinks_div.find_all("a", href=True)
    if a["href"].startswith(host_prefix)
]
if not links:
    log.error(f"No Matching {host_name} URLs Found", "Retry..")
else:
    output = "\n".join(links)
    print(f"🔗 Matching {host_name} URLs :")
    print(output)
    pyperclip.copy(output)

    log.success(f"All {host_name} Links Copied To Clipboard", len(links))
