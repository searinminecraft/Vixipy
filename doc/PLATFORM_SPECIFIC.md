# Platform / Operating System Notes

## Haiku
You cannot activate virtual environments on Haiku due to how the directory structuring works, so you will have to execute the `python` in the venv manually.

* To install dependencies: `venv/non-packaged/bin/python -m pip install -r requirements.txt`
* To run Vixipy in debug: `venv/non-packaged/bin/python -m vixipy`
* To run in production: `venv/non-packaged/bin/python -m hypercorn vixipy --bind :8000`

## Windows/FreeBSD/Certain Linux distributions and VPS providers
You may need to enable `PIXIV_DIRECT_CONNECTION` due to blocks by Cloudflare. This will cause Vixipy to be slower depending on where you are located.
