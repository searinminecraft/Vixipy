import os
import random

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
