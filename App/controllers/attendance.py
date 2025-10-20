from App.models import Attendance
from App.database import db
from datetime import datetime
from typing import Optional

def clock_in(user_id: int, shift_id: int, when: Optional[datetime] = None):
    when = when or datetime.now()
    att = Attendance.query.filter_by(shift_id=shift_id, user_id=user_id).first()
    if not att:
        raise ValueError("Attendance record not found for this shift/user.")
    if att.time_in:
        return att
    att.time_in = when
    db.session.commit()
    return att

def clock_out(user_id: int, shift_id: int, when: Optional[datetime] = None):
    when = when or datetime.now()
    att = Attendance.query.filter_by(shift_id=shift_id, user_id=user_id).first()
    if not att:
        raise ValueError("Attendance record not found for this shift/user.")
    if not att.time_in:
        raise ValueError("Cannot clock out before clocking in.")
    if att.time_out:
        return att
    att.time_out = when
    db.session.commit()
    return att


def ensure_attendance_record(user_id: int, shift_id: int, approved: Optional[bool] = None):
    """Return existing attendance record for (user_id, shift_id) or create it.
    If `approved` is provided, update the approved flag on the record.
    Raises ValueError only on invalid input.
    """
    if not user_id or not shift_id:
        raise ValueError("user_id and shift_id are required")

    att = Attendance.query.filter_by(shift_id=shift_id, user_id=user_id).first()
    if att:
        # update approved flag if caller provided a value
        if approved is not None and att.approved != approved:
            att.approved = bool(approved)
            db.session.commit()
        return att

    att = Attendance(user_id=user_id, shift_id=shift_id)
    if approved is not None:
        att.approved = bool(approved)
    db.session.add(att)
    db.session.commit()
    return att


def get_attendance(attendance_id: int):
    return Attendance.query.get(attendance_id)


def get_attendance_for_user(user_id: int):
    return Attendance.query.filter_by(user_id=user_id).all()


def get_attendance_for_shift(shift_id: int):
    return Attendance.query.filter_by(shift_id=shift_id).all()


def approve_attendance(user_id: int, shift_id: int):
    att = Attendance.query.filter_by(user_id=user_id, shift_id=shift_id).first()
    if not att:
        raise ValueError("Attendance record not found for this shift/user.")
    if not att.approved:
        att.approved = True
        db.session.commit()
    return att


def unapprove_attendance(user_id: int, shift_id: int):
    att = Attendance.query.filter_by(user_id=user_id, shift_id=shift_id).first()
    if not att:
        raise ValueError("Attendance record not found for this shift/user.")
    if att.approved:
        att.approved = False
        db.session.commit()
    return att


def attendance_to_json(att: Attendance):
    return att.get_json() if att else None