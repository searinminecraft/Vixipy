import logging
from quart import Blueprint, abort, current_app, g, render_template, request
from jinja2_fragments.quart import render_block

from ..api.street import get_data as get_street_data
from ..decorators import require_login


bp = Blueprint("street", __name__)
log = logging.getLogger(__name__)


@bp.route("/street", methods=("GET", "POST"))
@require_login
async def main():
    if not current_app.config["DEBUG"]:
        # we do not want something incomplete to be shown
        abort(501)

    if request.method == "POST":
        f = await request.form

        vhis: str = f.get("vhi") or None
        vhms: str = f.get("vhm") or None
        vhns: str = f.get("vhn") or None
        vhcs: str = f.get("vhc") or None

        k = f.get("k") or None
        page = f.get("page") or None
        content_index_prev = f.get("content_index_prev") or None
        bootstrap = f.get("bootstrap") == "1"

        vhi = vhis.split(',') if vhis else None
        vhm = vhms.split(',') if vhms else None
        vhn = vhns.split(',') if vhns else None
        vhc = vhcs.split(',') if vhcs else None

        data = await get_street_data(
            k=k,
            page=page,
            content_index_prev=content_index_prev,
            vhc=vhc,
            vhm=vhm,
            vhn=vhn,
            vhi=vhi,
        )

        data.next_params.update(vhc, vhi, vhm, vhn)
        log.debug(data.next_params)

        if g.hx_request:
            if bootstrap:
                return await render_block("street/index.html.j2", "street_bootstrap", data=data)
            return await render_block("street/index.html.j2", "entries", data=data)
        return await render_template("street/index.html.j2", data=data)

    if not g.hx_request:
        data = await get_street_data()
        return await render_template("street/index.html.j2", data=data)

    return await render_template("street/index.html.j2")
