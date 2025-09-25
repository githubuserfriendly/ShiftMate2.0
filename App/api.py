# App/api.py
from flask import Blueprint, request, jsonify
from datetime import date, datetime, time as dtime
from App.controllers import (
    schedule_shift, schedule_week, get_roster,
    clock_in, clock_out, weekly_report
)

api = Blueprint('api', __name__, url_prefix='/api')

def parse_date(s): return date.fromisoformat(s)
def parse_datetime(s): return datetime.fromisoformat(s)

# --- Admin: create one shift ---
@api.route('/admin/shifts', methods=['POST'])
def api_create_shift():
    data = request.get_json() or {}
    shift = schedule_shift(
        user_id=int(data['user_id']),
        work_date=parse_date(data['date']),
        start=_to_time(data['start']),
        end=_to_time(data['end']),
        role=data.get('role'),
        location=data.get('location'),
    )
    return jsonify(shift.get_json()), 201

# --- Admin: create a week's schedule for a user ---
@api.route('/admin/shifts/bulk', methods=['POST'])
def api_create_week():
    data = request.get_json() or {}
    created = schedule_week(
        user_id=int(data['user_id']),
        week_start=parse_date(data['week_start']),
        daily_windows=data['daily_windows'],
        role=data.get('role'),
        location=data.get('location'),
    )
    return jsonify([s.get_json() for s in created]), 201

# --- Staff: combined roster ---
@api.route('/roster', methods=['GET'])
def api_roster():
    start = parse_date(request.args.get('start'))
    end = parse_date(request.args.get('end'))
    return jsonify(get_roster(start, end)), 200

# --- Staff: time in/out ---
@api.route('/attendance/clock-in', methods=['POST'])
def api_clock_in():
    data = request.get_json() or {}
    att = clock_in(int(data['user_id']), int(data['shift_id']))
    return jsonify(att.get_json()), 200

@api.route('/attendance/clock-out', methods=['POST'])
def api_clock_out():
    data = request.get_json() or {}
    att = clock_out(int(data['user_id']), int(data['shift_id']))
    return jsonify(att.get_json()), 200

# --- Admin: weekly report ---
@api.route('/admin/reports/weekly', methods=['GET'])
def api_weekly_report():
    week_start = parse_date(request.args.get('week_start'))
    return jsonify(weekly_report(week_start)), 200

# helpers
def _to_time(s: str) -> dtime:
    return dtime.fromisoformat(s)
