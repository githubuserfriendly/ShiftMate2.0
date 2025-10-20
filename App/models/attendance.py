# App/models/attendance.py
from App.database import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    shift_id = db.Column(db.Integer, db.ForeignKey("shifts.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    approved = db.Column(db.Boolean, default=False)

    shift = db.relationship("Shift", backref=db.backref("attendance", lazy=True))
    user  = db.relationship("User", backref=db.backref("attendance", lazy=True))

    __table_args__ = (
        db.UniqueConstraint("shift_id", "user_id", name="uq_attendance_shift_user"),
    )

    def __repr__(self):
        return (f"<Attendance id={self.id} shift_id={self.shift_id} user_id={self.user_id} "
                f"in={self.time_in} out={self.time_out} approved={self.approved}>")

    def hours_worked(self):
        if self.time_in and self.time_out:
            return max((self.time_out - self.time_in).total_seconds() / 3600.0, 0)
        return 0.0

    def get_json(self):
        return {
            "id": self.id,
            "shift_id": self.shift_id,
            "user_id": self.user_id,
            "time_in": self.time_in.isoformat() if self.time_in else None,
            "time_out": self.time_out.isoformat() if self.time_out else None,
            "approved": self.approved,
            "hours_worked": round(self.hours_worked(), 2),
        }
