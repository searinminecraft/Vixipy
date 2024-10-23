import os
import secrets

AuthlessMode = False

def setAuthlessMode():
    global AuthlessMode
    AuthlessMode = True

    return secrets.token_urlsafe(24).lower().replace("_", "")

PxSession = os.environ.get("PYXIV_TOKEN")

if not PxSession:
    PxSession = setAuthlessMode()

PyXivSecret = os.environ.get("PYXIV_SECRET", "ILoveVixipy")

PxAcceptLang = os.environ.get("PYXIV_ACCEPTLANG", "en-US,en;q=0.5")
PxInstanceName = os.environ.get("PYXIV_INSTANCENAME", "Vixipy")
