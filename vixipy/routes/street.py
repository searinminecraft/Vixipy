from quart import Blueprint, abort, current_app, render_template

from ..api.street import get_data as get_street_data
from ..decorators import require_login

bp = Blueprint("street", __name__)

@bp.route("/street")
@require_login
async def main():
    if not current_app.config["DEBUG"]:
        # we do not want something incomplete to be shown
        abort(501)

    data = await get_street_data()

