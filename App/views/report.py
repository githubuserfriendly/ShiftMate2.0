from flask import Blueprint, render_template, jsonify, request, send_file, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers.report import weekly_report, get_all_reports, get_report_by_id
from datetime import datetime, timedelta
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

report_views = Blueprint('report_views', __name__, template_folder='../templates')


@report_views.route('/reports', methods=['GET'])
@jwt_required()
def view_reports():
    reports = get_all_reports()
    latest_report = reports[0] if reports else None
    return render_template('reports.html', report=latest_report)


@report_views.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_report():
    # Example: auto-generate for the past week
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)

    new_report = generate_weekly_report(start_date, end_date)
    flash("Weekly report generated successfully!", "success")
    return redirect(url_for('report_views.view_reports'))


@report_views.route('/reports/download/<int:report_id>')
@jwt_required()
def download_report(report_id):
    fmt = request.args.get('format', 'csv')
    report = get_report_by_id(report_id)
    if not report:
        flash("Report not found", "error")
        return redirect(url_for('report_views.view_reports'))

    if fmt == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Start Date', 'End Date', 'Total Shifts', 'Total Hours', 'Attendance Rate', 'Overtime Hours'])
        writer.writerow([report.start_date, report.end_date, report.total_shifts,
                         report.total_hours, report.attendance_rate, report.overtime_hours])
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'report_{report.id}.csv'
        )
    elif fmt == 'pdf':
        output = io.BytesIO()
        pdf = canvas.Canvas(output, pagesize=letter)
        pdf.drawString(100, 750, f"Weekly Report: {report.start_date} - {report.end_date}")
        pdf.drawString(100, 730, f"Total Shifts: {report.total_shifts}")
        pdf.drawString(100, 710, f"Total Hours: {report.total_hours}")
        pdf.drawString(100, 690, f"Staff Attendance Rate: {report.attendance_rate}%")
        pdf.drawString(100, 670, f"Overtime Hours: {report.overtime_hours}")
        pdf.save()
        output.seek(0)
        return send_file(output, mimetype='application/pdf',
                         as_attachment=True, download_name=f'report_{report.id}.pdf')
    else:
        flash("Invalid format", "error")
        return redirect(url_for('report_views.view_reports'))