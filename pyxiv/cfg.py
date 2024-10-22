import os
import secrets

def setAuthlessMode():
    global AuthlessMode
    AuthlessMode = True

    return secrets.token_urlsafe(24).lower()

PxSession = os.environ.get("PYXIV_TOKEN", setAuthlessMode())
PyXivSecret = os.environ.get("PYXIV_SECRET", "ILoveVixipy")

PxAcceptLang = os.environ.get("PYXIV_ACCEPTLANG", "en-US,en;q=0.5")
PxInstanceName = os.environ.get("PYXIV_INSTANCENAME", "Vixipy")
