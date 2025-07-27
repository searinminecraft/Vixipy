import asyncio
import argparse
from hypercorn import Config
from hypercorn.asyncio import serve

from . import app, __copyright__
from .bootstrap import bootstrap

class _Arguments:
    debug: bool
    binds: list[str]
    version: bool

async def __bootstrapper():
    await bootstrap(app)

async def main(bind: list[str]):
    config = Config.from_mapping(
        include_server_header=False,
        bind=bind
    )

    await bootstrap(app)
    await serve(app, config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Yet another feature rich pixiv frontend"
    )
    parser.add_argument("--debug", action="store_true", help="Run quart application in debug mode")
    parser.add_argument(
        "-b",
        "--bind",
        dest="binds",
        help=""" The TCP host/address to bind to. Should be either host:port, host,
        unix:path or fd://num, e.g. 127.0.0.1:5000, 127.0.0.1,
        unix:/tmp/socket or fd://33 respectively.  """,
        default=[],
        action="append",
    )
    parser.add_argument("--version", action="store_true", help="Show version")

    args: _Arguments = parser.parse_args()

    if args.version:
        print("Vixipy version", app.config["VIXIPY_VERSION"])
        print(__copyright__)
        exit()

    if len(args.binds) == 0:
        args.binds = ["127.0.0.1:8000"]

    if args.debug:
        app.before_serving(__bootstrapper)
        app.run(debug=True, host="0.0.0.0")
    else:
        asyncio.run(main(args.binds))
