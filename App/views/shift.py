# App/views/shift.py
from flask import Blueprint

shift_views = Blueprint("shift_views", __name__, url_prefix="/api/shifts")

@shift_views.get("/_health")
def health():
    return {"ok": True}
