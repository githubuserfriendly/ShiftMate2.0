from datetime import datetime, date
from App.database import db

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)

    # Who generated it (optional)
    generated_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)

    # Report identity / scope
    report_type = db.Column(db.String(40), nullable=False, index=True)  # e.g., "weekly", "monthly"
    period_start = db.Column(db.Date, nullable=False, index=True)
    period_end   = db.Column(db.Date, nullable=False, index=True)

    # Storage for the computed results (totals, rows, etc.)
    payload = db.Column(db.JSON, nullable=False, default={})

    # Lifecycle
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    generated_by = db.relationship("User", backref=db.backref("reports", lazy=True))

    __table_args__ = (
        # One report per type+period (adjust if you want multiple versions)
        db.UniqueConstraint("report_type", "period_start", "period_end", name="uq_report_type_period"),
    )

    def __repr__(self):
        return (
            f"<Report id={self.id} type={self.report_type!r} "
            f"{self.period_start}..{self.period_end} by={self.generated_by_id}>"
        )

    # ---- helpers ----
    @classmethod
    def weekly_key(cls, week_start: date):
        """Convenience for weekly reports."""
        week_end = week_start  # controller should pass end explicitly if needed
        return ("weekly", week_start, week_end)

    def get_json(self) -> dict:
        return {
            "id": self.id,
            "report_type": self.report_type,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "generated_by_id": self.generated_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "payload": self.payload or {},
        }
