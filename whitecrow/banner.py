import subprocess
import shutil
from . import __version__

HAS_FIGLET = shutil.which("figlet")
HAS_LOLCAT = shutil.which("lolcat")
HAS_COWSAY = shutil.which("cowsay")

BANNER = ""
COW = ""

if HAS_FIGLET:
    try:
        r = subprocess.run(["figlet", "WhiteCrow"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            BANNER = r.stdout
    except Exception:
        pass

if not BANNER:
    BANNER = f"""\
{'╔' + '═'*50 + '╗'}
{'║'}{f'WhiteCrow v{__version__}':^50}{'║'}
{'║'}{'OSINT & Bug Bounty Scanner':^50}{'║'}
{'╚' + '═'*50 + '╝'}
"""

if HAS_COWSAY:
    try:
        r = subprocess.run(["cowsay", "Ready to hunt bugs"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            COW = r.stdout
    except Exception:
        pass


def print_banner():
    if HAS_LOLCAT and BANNER:
        try:
            r = subprocess.run(["lolcat"], input=BANNER, capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                print(r.stdout, end="")
                if COW:
                    rc = subprocess.run(["lolcat"], input=COW, capture_output=True, text=True, timeout=5)
                    if rc.returncode == 0:
                        print(rc.stdout, end="")
                return
        except Exception:
            pass
    print(BANNER, end="")
    if COW:
        print(COW, end="")
