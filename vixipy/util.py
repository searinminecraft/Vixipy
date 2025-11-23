from __future__ import annotations

from quart import g, request
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from quart import Quart


class ServerTiming:
    def __init__(self, name: str, dur: Union[int, float]):
        self.name = name.replace("/", "_")
        self.dur = dur
    
    @property
    def as_header_value(self):
        return f"{self.name if len(self.name) < 40 else f'{self.name[:39]}...'};dur={self.dur}"


def is_consented():
    return request.cookies.get("Vixipy-Consented") == "1"


def add_server_timing_metric(name: str, dur: Union[int, float]):
    if not g.get("server_timings"):
        g.server_timings = []
    
    g.server_timings.append(ServerTiming(name, dur))

def add_server_timing_header(r):
    r.headers["Server-Timing"] = ",".join([x.as_header_value for x in g.get("server_timings", [])])
    return r

def init_app(app: Quart):
    app.after_request(add_server_timing_header)
