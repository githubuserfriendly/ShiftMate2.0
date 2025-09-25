import click, pytest, sys, json
from flask.cli import with_appcontext, AppGroup
from datetime import datetime, date, time as dtime, timedelta
from App.database import db, get_migrate
from App.models import User, Shift, Attendance
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.controllers import schedule_shift, schedule_week, get_roster, clock_in, clock_out, weekly_report

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('Database Initialized!')

# Groups: 
# HOW TO USE GROUPS : flask <group> <command>
user_cli = AppGroup('user', help='User object commands')
test = AppGroup('test', help='Testing commands') 
shift_cli = AppGroup('shift', help='Shift scheduling and roster commands')
att_cli = AppGroup('att', help='Attendance (clock in/out) commands')
report_cli = AppGroup('report', help='Reporting commands')

'''
User Commands
'''

# Creating a user:
# This command will be : flask user create bob bobpass
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# Generating List of all Users
@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users_json())
    else:
        print(get_all_users_json())
app.cli.add_command(user_cli)


'''
Test Commands
'''

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
app.cli.add_command(test)


@user_cli.command("week", help="Schedule a simple 9-5 week for a user (Mon-Fri)")
@click.argument("username")
@click.argument("week_start")  # YYYY-MM-DD (Monday)
def schedule_simple_week(username, week_start):
    u = User.query.filter_by(username=username).first()
    if not u:
        print("User not found")
        return
    ws = date.fromisoformat(week_start)
    windows = {i: ("09:00","17:00") for i in range(5)}  # Mon-Fri

    result = schedule_week(u.id, ws, windows, role=None, location=None, skip_existing=True)
    created, skipped = result["created"], result["skipped"]
    print(f"Created {len(created)} shifts; Skipped (already existed) {len(skipped)}.")

@test.command("roster", help="Print roster for a date range")
@click.argument("start")
@click.argument("end")
def print_roster(start, end):
    roster = get_roster(date.fromisoformat(start), date.fromisoformat(end))
    for r in roster:
        print(r)

@test.command("report", help="Weekly report by week_start")
@click.argument("week_start")
def print_report(week_start):
    rep = weekly_report(date.fromisoformat(week_start))
    print(rep)

def _print_json(data):
    print(json.dumps(data, indent=2, default=str))

def _to_time(s):
    return dtime.fromisoformat(s)

def _find_user(username):
    u = User.query.filter_by(username=username).first()
    if not u:
        print(f"User '{username}' not found")
        return None
    return u

def _find_shift_id(username, work_date, start_str=None):
    """
    Utility: find a user's shift id on a given date (optionally matching start time).
    Returns the first match.
    """
    u = _find_user(username)
    if not u:
        return None
    q = Shift.query.filter(Shift.user_id == u.id, Shift.work_date == date.fromisoformat(work_date))
    if start_str:
        q = q.filter(Shift.start_time == _to_time(start_str))
    s = q.order_by(Shift.start_time.asc()).first()
    if not s:
        print("No matching shift found.")
        return None
    return s.id

# ---- SHIFT COMMANDS ----
@shift_cli.command("add", help="Create a single shift for a user")
@click.argument("username")
@click.argument("work_date")   # YYYY-MM-DD
@click.argument("start")       # HH:MM
@click.argument("end")         # HH:MM
@click.option("--role", default=None)
@click.option("--location", default=None)
def shift_add(username, work_date, start, end, role, location):
    u = _find_user(username)
    if not u: return
    s = schedule_shift(
        user_id=u.id,
        work_date=date.fromisoformat(work_date),
        start=_to_time(start),
        end=_to_time(end),
        role=role,
        location=location
    )
    print("Created shift:")
    _print_json(s.get_json())

@shift_cli.command("roster", help="Show combined roster for a date range (all staff)")
@click.argument("start")  # YYYY-MM-DD
@click.argument("end")    # YYYY-MM-DD
def shift_roster(start, end):
    roster = get_roster(date.fromisoformat(start), date.fromisoformat(end))
    _print_json(roster)

@shift_cli.command("user", help="Show one user's shifts in a date range")
@click.argument("username")
@click.argument("start")
@click.argument("end")
def shift_user(username, start, end):
    roster = get_roster(date.fromisoformat(start), date.fromisoformat(end))
    only = [r for r in roster if r.get('username') == username]
    _print_json(only)

@shift_cli.command("find", help="Find a user's shift IDs on a given date (useful before clock-in/out)")
@click.argument("username")
@click.argument("work_date")
def shift_find(username, work_date):
    u = _find_user(username)
    if not u: return
    shifts = Shift.query.filter(
        Shift.user_id == u.id,
        Shift.work_date == date.fromisoformat(work_date)
    ).order_by(Shift.start_time.asc()).all()
    payload = [s.get_json() | {'id': s.id} for s in shifts]
    if not payload:
        print("No shifts found.")
    else:
        _print_json(payload)

app.cli.add_command(shift_cli)

# ---- ATTENDANCE COMMANDS ----
@att_cli.command("seed", help="Create an empty attendance record for a shift (if missing)")
@click.argument("username")
@click.argument("shift_id", type=int)
def att_seed(username, shift_id):
    u = _find_user(username)
    if not u: return
    rec = Attendance.query.filter_by(shift_id=shift_id, user_id=u.id).first()
    if rec:
        print("Attendance already exists:")
        _print_json(rec.get_json())
        return
    rec = Attendance(user_id=u.id, shift_id=shift_id)
    db.session.add(rec)
    db.session.commit()
    print("Created attendance record:")
    _print_json(rec.get_json())

@att_cli.command("in", help="Clock IN now for a user on a shift by id")
@click.argument("username")
@click.argument("shift_id", type=int)
def att_in(username, shift_id):
    u = _find_user(username)
    if not u: return
    att = clock_in(u.id, shift_id, when=datetime.now())
    _print_json(att.get_json())

@att_cli.command("out", help="Clock OUT now for a user on a shift by id")
@click.argument("username")
@click.argument("shift_id", type=int)
def att_out(username, shift_id):
    u = _find_user(username)
    if not u: return
    att = clock_out(u.id, shift_id, when=datetime.now())
    _print_json(att.get_json())

@att_cli.command("status", help="Show attendance record for a shift/user")
@click.argument("username")
@click.argument("shift_id", type=int)
def att_status(username, shift_id):
    u = _find_user(username)
    if not u: return
    rec = Attendance.query.filter_by(shift_id=shift_id, user_id=u.id).first()
    if rec:
        _print_json(rec.get_json())
    else:
        print("No attendance record found.")
app.cli.add_command(att_cli)

# ---- REPORT COMMANDS (prettier output) ----
@report_cli.command("week", help="Weekly report (week_start = Monday)")
@click.argument("week_start")
def report_week(week_start):
    rep = weekly_report(date.fromisoformat(week_start))
    _print_json(rep)
app.cli.add_command(report_cli)