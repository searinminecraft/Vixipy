import os
import random
import logging
from urllib.parse import urlparse

Version = "2.7"
AuthlessMode = False
log = logging.getLogger("vixipy.cfg")


def setAuthlessMode():
    global AuthlessMode
    AuthlessMode = True

    return "".join([chr(random.randint(97, 122)) for _ in range(33)])


PxSession = os.environ.get("PYXIV_TOKEN")

if not PxSession:
    PxSession = setAuthlessMode()

MultipleSessions = False
if len(PxSession.split(",")) != 1:
    MultipleSessions = True
    PxSession = PxSession.split(",")

TokenBalancer = os.environ.get("PYXIV_TOKEN_BALANCER", "random").lower().strip()
if TokenBalancer not in ["random", "next"]:
    log.error("Invalid TokenBalancer, please set it to random or next")
    TokenBalancer = "random"

PyXivSecret = os.environ.get("PYXIV_SECRET", "ILoveVixipy")

PxAcceptLang = os.environ.get("PYXIV_ACCEPTLANG", "en-US,en;q=0.5")
PxInstanceName = os.environ.get("PYXIV_INSTANCENAME", "Vixipy")
NoR18 = int(os.environ.get("PYXIV_NOR18", 0)) == 1
RateLimitsEnabled = int(os.environ.get("PYXIV_RATELIMITS", 0)) == 1
GitRev = os.environ.get("GIT_REVISION", "unknown")
GitRepo = os.environ.get("GIT_REPO", "unknown")
TryAcquireSession = int(os.environ.get("PYXIV_ACQUIRE_SESSION", 0)) == 1
DefaultProxy = os.environ.get("PYXIV_DEFAULT_PROXY", "")
UgoiraServer = os.environ.get("PYXIV_UGOIRA_SERVER", "https://t-hk.ugoira.com/ugoira/%s.mp4")
UgoiraServerReferer = os.environ.get("PYXIV_UGOIRA_SERVER_REFERER", "https://ugoira.com")
UgoiraServerTrusted = int(os.environ.get("PYXIV_UGOIRA_SERVER_TRUSTED", 0)) == 1
UgoiraServerNeedsDate = int(os.environ.get("PYXIV_UGOIRA_SERVER_NEEDS_DATE", 0)) == 1

UgoiraServerNetloc = ""
if UgoiraServerTrusted:
    UgoiraServerNetloc = urlparse(UgoiraServer).netloc or ""

Themes = os.environ.get("PYXIV_ADDITIONAL_THEMES", "").split(",")
DefaultTheme = os.environ.get("PYXIV_DEFAULT_THEME", "aqua")
DefaultThemes = (
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "aqua",
    "pink",
    "purple",
    "grayscale",
    "brand-pixiv",
    "ocean",
)

# normalize
if GitRepo.startswith(
    "http"
):  # https://codeberg.org/vixipy/vixipy.git/ for example, this strips the leading slash and .git
    GitRepo = GitRepo.removesuffix("/").removesuffix(".git")
else:  # git@codeberg.org:vixipy/vixipy for example, this turns it into a https url
    # in case GitRepo isn't set
    try:
        GitRepo = GitRepo.split("@")[1].split(":")
        GitRepo = "https://" + GitRepo[0] + "/" + GitRepo[1]
    except Exception:
        GitRepo = "https://codeberg.org/vixipy/Vixipy"

# we need this file to ensure this function only runs once, since vixipy runs multiple workers
# it is removed if you shutdown gracefully
if not os.path.isfile("pyxiv.running"):
    with open("pyxiv.running", "w") as file:
        file.write("yes it is!")
    print(
        rf"""

                ⠀⠀⠀⠀⢀⡴⣆⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⣼⣿⡗⠀⠀⠀⠀
                ⠀⠀⠀⣠⠟⠀⠘⠷⠶⠶⠶⠾⠉⢳⡄⠀⠀⠀⠀⠀⣧⣿⠀⠀⠀⠀⠀
                ⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣤⣤⣤⣤⣤⣿⢿⣄⠀⠀⠀⠀
 __   ____  __  ⠀⠀⡇⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠙⣷⡴⠶⣦
 \ \ / /\ \/ /  ⠀⠀⢱⡀⠀⠉⠉⠀⠀⠀⠀⠛⠃⠀⢠⡟⠂⠀⠀⢀⣀⣠⣤⠿⠞⠛⠋
  \ V /  >  <   ⣠⠾⠋⠙⣶⣤⣤⣤⣤⣤⣀⣠⣤⣾⣿⠴⠶⠚⠋⠉⠁⠀⠀⠀⠀⠀⠀
   \_/  /_/\_\  ⠛⠒⠛⠉⠉⠀⠀⠀⣴⠟⣣⡴⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀v{Version}
~~~~~~~~~~~~~~~~~~~~~~~~⠛⠛~~~~~~~~~~~~~~~~~~~~~~~~~"""
    )  # cute
    print(f"Vixipy is listening on 127.0.0.1:{os.environ.get('PYXIV_PORT')}")
    boolean = lambda a: "Yes" if a else "No"
    the_config = {
        "Commit": f"{GitRev} ({GitRepo})",
        "Using account": boolean(not AuthlessMode)
        + (f" ({len(PxSession)} accounts)" if MultipleSessions else ""),
        "Accept-Language": PxAcceptLang,
        "Instance name": PxInstanceName,
        "No R18": boolean(NoR18),
        "Rate limiting": boolean(RateLimitsEnabled),
        "Acquire session": boolean(TryAcquireSession),
        "Workers": os.environ.get("PYXIV_WORKERS", "1"),
    }

    longest = ""
    for k in the_config:
        if len(k) > len(longest):
            longest = k

    sep = " :: "
    longest += sep

    for k in the_config:
        print(k, end="")
        print(" " * (len(longest) - len(k) - len(sep)), end="")
        print(sep, end="")
        print(the_config[k])

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
