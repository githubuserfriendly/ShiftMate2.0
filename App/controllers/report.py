from App.models import Shift, Attendance, User
from datetime import timedelta, date

def weekly_report(week_start: date):
    week_end = week_start + timedelta(days=6)
    shifts = Shift.query.filter(Shift.work_date.between(week_start, week_end)).all()

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