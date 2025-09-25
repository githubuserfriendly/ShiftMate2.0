## Welcome To ShiftMate!
  ![ShiftMate logo](App/static/Logo.png)

ShiftMate is a lightweight staff scheduling and attendance toolkit with a simple CLI: 
- admins create weekly rosters (Monday start, 9–5 or custom, roles/locations)
- staff view the combined roster, clock in/out
- weekly reports summarize hours and coverage

## Install Dependencies

```bash
    $ pip install -r requirements.txt
```

# Flask Commands

## Base Command
Create & Initialize Database

```bash
  flask init
```

## User Commands
1. Create New User

```bash
  flask user create <username> <password>
```

2. Generate List of All Users

```bash
  flask user list
```

3. Schedule a Simple Monday-Friday Week for a User
    (weekStart must be a Monday) (format: YYYY-MM-DD)
```bash
  flask user week <username> <weekStart>
```

## Shift Commands
1. Add a Shift 

```bash
    flask shift add <username> <work_date> <start> <end> [--role ROLE] [--location LOC]

```

2. View Combined Roster (All Staff)
```bash
    flask shift roster <start> <end>
```

3. View One User’s Shifts

```bash
    flask shift user <username> <start> <end>
```

4. Find Shift IDs for a User/Day
```bash
    flask shift find <username> <work_date>
```

## Attendance
1. Create an empty attendance record for the shift if missing (run once per shift if needed).
```bash
  flask att seed <username> <shift_id>
```

2. Clock In
```bash
      flask att in <username> <shift_id>
```

3. Clock Out
```bash
  flask att out <username> <shift_id>
```

4. Atendance Status
```bash
  flask att status <username> <shift_id>
```

## Report Command
Generate Weekly Reports (expects Monday YYYY-MM-DD)
```bash 
  flask report week <week_start>
```

## Test (Dev Helpers)

1. Run Tests (Run pytest suites)
```bash
  flask test user [unit|int|all]
```


2. Print Roster (Dev Output) (Print roster for a date range (plain output).)
```bash
  flask test roster <start> <end>
```

3. Print Weekly Report (Dev Output) (Print weekly report (plain output).)
```bash
  flask test report <week_start>
```
