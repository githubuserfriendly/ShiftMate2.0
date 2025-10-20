from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user

from App.controllers import (
    ensure_attendance_record,
    clock_in as ctrl_clock_in,
    clock_out as ctrl_clock_out,
    approve_attendance,
    unapprove_attendance,
    get_attendance,
    get_attendance_for_user,
    get_attendance_for_shift,
    attendance_to_json,
)

attendance_views = Blueprint("attendance_views", __name__, url_prefix="/api/attendance")

# --- helpers ---

def _admin_required():
    if not current_user or not getattr(current_user, "isAdmin", False):
        return jsonify(error="Admins only"), 403
    return None

# --- routes ---

@attendance_views.route("", methods=["GET"])
@jwt_required()
def list_attendance():
    """
    GET /api/attendance?user_id=<id>&shift_id=<id>
    - If user_id given -> list that user's attendance records
    - If shift_id given -> list all attendance on that shift
    - If both missing -> 400
    """
    user_id = request.args.get("user_id", type=int)
    shift_id = request.args.get("shift_id", type=int)

    if user_id:
        items = get_attendance_for_user(user_id)
        return jsonify([attendance_to_json(a) for a in items]), 200
    if shift_id:
        items = get_attendance_for_shift(shift_id)
        return jsonify([attendance_to_json(a) for a in items]), 200
    return jsonify(error="Provide user_id or shift_id"), 400


@attendance_views.route("/<int:attendance_id>", methods=["GET"])
@jwt_required()
def get_attendance_by_id(attendance_id: int):
    att = get_attendance(attendance_id)
    if not att:
        return jsonify(error="Attendance not found"), 404
    return jsonify(attendance_to_json(att)), 200


@attendance_views.route("/ensure", methods=["POST"])
@jwt_required()
def ensure_attendance():
    """
    POST /api/attendance/ensure
    { "user_id": 1, "shift_id": 10, "approved": false }
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", current_user.id)  # default to caller
    shift_id = data.get("shift_id")
    if not shift_id:
        return jsonify(error="shift_id is required"), 400

    try:
        att = ensure_attendance_record(user_id=user_id, shift_id=shift_id, approved=data.get("approved"))
        return jsonify(attendance_to_json(att)), 201
    except ValueError as e:
        return jsonify(error=str(e)), 400


@attendance_views.route("/clock-in", methods=["POST"])
@jwt_required()
def clock_in():
    """
    POST /api/attendance/clock-in
    { "shift_id": 10, "user_id": 1? }  # user_id optional -> defaults to current_user
    """
    data = request.get_json(silent=True) or {}
    shift_id = data.get("shift_id")
    if not shift_id:
        return jsonify(error="shift_id is required"), 400

    user_id = data.get("user_id", current_user.id)
    try:
        att = ctrl_clock_in(user_id=user_id, shift_id=shift_id)
        return jsonify(attendance_to_json(att)), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400


@attendance_views.route("/clock-out", methods=["POST"])
@jwt_required()
def clock_out():
    """
    POST /api/attendance/clock-out
    { "shift_id": 10, "user_id": 1? }
    """
    data = request.get_json(silent=True) or {}
    shift_id = data.get("shift_id")
    if not shift_id:
        return jsonify(error="shift_id is required"), 400

    user_id = data.get("user_id", current_user.id)
    try:
        att = ctrl_clock_out(user_id=user_id, shift_id=shift_id)
        return jsonify(attendance_to_json(att)), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400


@attendance_views.route("/approve", methods=["POST"])
@jwt_required()
def approve():
    """
    POST /api/attendance/approve
    { "user_id": 1, "shift_id": 10 }
    Admins only.
    """
    guard = _admin_required()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    shift_id = data.get("shift_id")
    if not (user_id and shift_id):
        return jsonify(error="user_id and shift_id are required"), 400

    try:
        att = approve_attendance(user_id=user_id, shift_id=shift_id)
        return jsonify(attendance_to_json(att)), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400


@attendance_views.route("/unapprove", methods=["POST"])
@jwt_required()
def unapprove():
    """
    POST /api/attendance/unapprove
    { "user_id": 1, "shift_id": 10 }
    Admins only.
    """
    guard = _admin_required()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    shift_id = data.get("shift_id")
    if not (user_id and shift_id):
        return jsonify(error="user_id and shift_id are required"), 400

    try:
        att = unapprove_attendance(user_id=user_id, shift_id=shift_id)
        return jsonify(attendance_to_json(att)), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400
