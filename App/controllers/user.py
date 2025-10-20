
from App.models import User, Shift, Attendance
from App.database import db
from datetime import datetime, date, timedelta, time as dtime
from sqlalchemy import and_, or_



def schedule_shift(user_id: int, work_date: date, start: dtime, end: dtime, role=None, location=None):
    existing = Shift.query.filter_by(
        user_id=user_id,
        work_date=work_date,
        start_time=start,
        end_time=end
    ).first()
    if existing:
        if role is not None:
            existing.role = role
        if location is not None:
            existing.location = location
        db.session.commit()
        return existing

    shift = Shift(
        user_id=user_id,
        work_date=work_date,
        start_time=start,
        end_time=end,
        role=role,
        location=location
    )
    db.session.add(shift)
    db.session.commit()

    att = Attendance.query.filter_by(shift_id=shift.id, user_id=user_id).first()
    if not att:
        db.session.add(Attendance(shift_id=shift.id, user_id=user_id))
        db.session.commit()

    return shift

def schedule_week(user_id: int, week_start: date, daily_windows: dict, role=None, location=None, skip_existing=True):
    """
    daily_windows:
      {0: ("09:00","17:00"), 1: ("09:00","17:00"), 2: None, ...}

    skip_existing=True => duplicates are skipped/updated (no error)
    """
    created, skipped = [], []
    for offset in range(7):
        pair = daily_windows.get(offset)
        if not pair:
            continue
        start_s, end_s = pair
        start = dtime.fromisoformat(start_s)
        end   = dtime.fromisoformat(end_s)
        work_day = week_start + timedelta(days=offset)

        existing = Shift.query.filter_by(
            user_id=user_id,
            work_date=work_day,
            start_time=start,
            end_time=end
        ).first()

        if existing:
            if skip_existing:
                if role is not None: existing.role = role
                if location is not None: existing.location = location
                db.session.commit()
                skipped.append(existing)
                continue
            else:
                raise ValueError("Duplicate shift exists")

        created.append(
            schedule_shift(user_id, work_day, start, end, role, location)
        )

    return {"created": [s.get_json() for s in created],
            "skipped": [s.get_json() for s in skipped]}

def get_roster(start_date: date, end_date: date):
    q = Shift.query.filter(and_(Shift.work_date >= start_date, Shift.work_date <= end_date))\
                   .order_by(Shift.work_date.asc(), Shift.start_time.asc())
    return [s.get_json() for s in q.all()]

def clock_in(user_id: int, shift_id: int, when: datetime | None = None):
    when = when or datetime.now()
    att = Attendance.query.filter_by(shift_id=shift_id, user_id=user_id).first()
    if not att:
        raise ValueError("Attendance record not found for this shift/user.")
    if att.time_in:
        return att 
    att.time_in = when
    db.session.commit()
    return att

def clock_out(user_id: int, shift_id: int, when: datetime | None = None):
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

def weekly_report(week_start: date):
    week_end = week_start + timedelta(days=6)
    shifts = Shift.query.filter(and_(Shift.work_date >= week_start, Shift.work_date <= week_end)).all()

    report = {
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'totals_per_user': {}, 
        'shifts': []          
    }

    def init_user(u: User):
        if u.id not in report['totals_per_user']:
            report['totals_per_user'][u.id] = {
                'username': u.username,
                'scheduled_hours': 0.0,
                'worked_hours': 0.0
            }

    for s in shifts:
        scheduled = s.duration_hours()
        att = Attendance.query.filter_by(shift_id=s.id, user_id=s.user_id).first()
        worked = att.hours_worked() if att else 0.0

        init_user(s.user)
        report['totals_per_user'][s.user_id]['scheduled_hours'] += scheduled
        report['totals_per_user'][s.user_id]['worked_hours'] += worked

        report['shifts'].append({
            **s.get_json(),
            'scheduled_hours': round(scheduled, 2),
            'worked_hours': round(worked, 2),
            'time_in': att.time_in.isoformat() if (att and att.time_in) else None,
            'time_out': att.time_out.isoformat() if (att and att.time_out) else None,
        })

    for u in report['totals_per_user'].values():
        u['scheduled_hours'] = round(u['scheduled_hours'], 2)
        u['worked_hours'] = round(u['worked_hours'], 2)

    return report
    