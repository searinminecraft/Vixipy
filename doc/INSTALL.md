# Installing Vixipy
Installing it is pretty straight forward. These should work on most platforms.


## Regular method
1. Install Python from your distribution or from python.org. At least version 3.10 is required
2. Clone the repository:
```sh
daiwa@umamusume:~ $ git clone https://codeberg.org/vixipy/Vixipy
daiwa@umamusume:~ $ cd Vixipy
```
3. Create a virtual environment:
```sh
daiwa@umamusume:~/Vixipy $ python3 -m venv venv
```

> [!NOTE]
> On some distributions (such as Ubuntu), venv is not included, and a separate package must be installed.

4. Activate the virtual environment:

> [!NOTE]
> If you are using Haiku, virtual environments are somewhat broken.
> You can skip this step

Windows:

```bat
rem If using PowerShell, use .ps1 instead of .bat
C:\Users\Daiwa Scarlet\Vixipy> .\venv\Scripts\activate.bat
```

Linux, macOS, BSD:

```sh
daiwa@umamusume:~/Vixipy $ . venv/bin/activate
```

5. Install the dependencies:

All other platforms:

```sh
(venv) daiwa@umamusume:~/Vixipy $ pip install -r requirements.txt
```

Haiku:

```sh
~/Vixipy > venv/non-packaged/bin/pip install -r requirements.txt
```

6. Create and edit the configuration file. See [CONFIGURATION.md](./CONFIGURATION.md) for details.

```sh
(venv) daiwa@umamusume:~/Vixipy $ mkdir instance
(venv) daiwa@umamusume:~/Vixipy $ nano instance/config.py
```

7. Finally, run Vixipy:
```sh
(venv) daiwa@umamusume:~/Vixipy $ python -m vixipy
```

## Docker

1. Make a copy of `compose.example.yaml` to `compose.yaml` and make any necessary edits.

```sh
daiwa@umamusume:~/Vixipy $ cp compose.example.yaml compose.yaml
daiwa@umamusume:~/Vixipy $ nano compose.yaml
```

Its recommended that for any Vixipy-related configuration you create and edit the `instance/config.py` file insead of inside the compose file. See [CONFIGURATION.md](./CONFIGURATION.md) for details.

```sh
daiwa@umamusume:~/Vixipy $ mkdir instance
daiwa@umamusume:~/Vixipy $ nano instance/config.py
```

2. Run the container as a daemon:
```sh
daiwa@umamusume:~/Vixipy $ docker compose up -d
```

(use docker-compose instead of docker compose if that fails)

# All set!

Vixipy runs on http://127.0.0.1:8000 and http://[::1]:8000 by default. To change the binding address, use the `--bind` argument. You may also use UNIX sockets by adding the `--bind unix:<name>.sock` argument.

If exposing to the internet, it is recommended to use and configure a reverse proxy. See your reverse proxy documentation for details.
