import os

PxSession = os.environ.get("PYXIV_TOKEN")

if not PxSession:
    raise RuntimeError("PYXIV_TOKEN environment variable was not provided")

PyXivSecret = os.environ.get("PYXIV_SECRET")

if not PyXivSecret:
    raise RuntimeError("PYXIV_SECRET environment variable was not provided")

PxAcceptLang = os.environ.get("PYXIV_ACCEPTLANG", "en-US,en;q=0.5")
PxInstanceName = os.environ.get("PYXIV_INSTANCENAME", "Vixipy")
