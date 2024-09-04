import os

PxSession = os.environ.get("PYXIV_TOKEN")

if not PxSession:
    raise NameError("PYXIV_TOKEN envionment variable was not provided")

PxAcceptLang = os.environ.get("PYXIV_ACCEPTLANG", "en-US,en;q=0.5")
