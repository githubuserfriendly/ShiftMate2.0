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