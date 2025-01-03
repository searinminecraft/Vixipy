import os
import random

Version = "2.1"
AuthlessMode = False


def setAuthlessMode():
    global AuthlessMode
    AuthlessMode = True

    return "".join([chr(random.randint(97, 122)) for _ in range(33)])


PxSession = os.environ.get("PYXIV_TOKEN")

if not PxSession:
    PxSession = setAuthlessMode()

PyXivSecret = os.environ.get("PYXIV_SECRET", "ILoveVixipy")

PxAcceptLang = os.environ.get("PYXIV_ACCEPTLANG", "en-US,en;q=0.5")
PxInstanceName = os.environ.get("PYXIV_INSTANCENAME", "Vixipy")
NoR18 = int(os.environ.get("PYXIV_NOR18", 0)) == 1
GitRev = os.environ.get("GIT_REVISION", "unknown")
GitRepo = os.environ.get("GIT_REPO", "unknown")

# normalize
if GitRepo.startswith("http"): # https://codeberg.org/vixipy/vixipy.git/ for example, this strips the leading slash and .git
    GitRepo = GitRepo.removesuffix("/").removesuffix(".git")
else: # git@codeberg.org:vixipy/vixipy for example, this turns it into a https url
    GitRepo = GitRepo.split("@")[1].split(":")
    GitRepo = "https://" + GitRepo[0] + "/" + GitRepo[1]

# we need this file to ensure this function only runs once, since vixipy runs multiple workers
# it is removed if you shutdown gracefully
if not os.path.isfile("pyxiv.running"):
    with open("pyxiv.running", "w") as file:
        file.write("yes it is!")
    print(f"""
        
                ⠀⠀⠀⠀⢀⡴⣆⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⣼⣿⡗⠀⠀⠀⠀
                ⠀⠀⠀⣠⠟⠀⠘⠷⠶⠶⠶⠾⠉⢳⡄⠀⠀⠀⠀⠀⣧⣿⠀⠀⠀⠀⠀
                ⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣤⣤⣤⣤⣤⣿⢿⣄⠀⠀⠀⠀
 __   ____  __  ⠀⠀⡇⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠙⣷⡴⠶⣦
 \ \ / /\ \/ /  ⠀⠀⢱⡀⠀⠉⠉⠀⠀⠀⠀⠛⠃⠀⢠⡟⠂⠀⠀⢀⣀⣠⣤⠿⠞⠛⠋
  \ V /  >  <   ⣠⠾⠋⠙⣶⣤⣤⣤⣤⣤⣀⣠⣤⣾⣿⠴⠶⠚⠋⠉⠁⠀⠀⠀⠀⠀⠀
   \_/  /_/\_\  ⠛⠒⠛⠉⠉⠀⠀⠀⣴⠟⣣⡴⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀v{Version}
~~~~~~~~~~~~~~~~~~~~~~~~⠛⠛~~~~~~~~~~~~~~~~~~~~~~~~~""") # cute
    print(f"Vixipy is listening on 127.0.0.1:{os.environ.get('PYXIV_PORT')}")
    boolean = lambda a: "Yes" if a else "No"
    the_config = {
        "Commit": f"{GitRev} ({GitRepo})",
        "Using account": boolean(not AuthlessMode),
        "Accept-Language": PxAcceptLang,
        "Instance name": PxInstanceName,
        "NoR18": boolean(NoR18),
    }

    longest = ""
    for k in the_config:
        if len(k) > len(longest):
            longest = k

    sep = " :: "
    longest += sep

    for k in the_config:
        print(k, end="")
        print(" " * (len(longest)-len(k)-len(sep)), end="")
        print(sep, end="")
        print(the_config[k])
    
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")