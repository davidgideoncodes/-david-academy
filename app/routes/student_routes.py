from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models import Student, Grade, Term, PortalSettings

student_bp = Blueprint("student", __name__)

def student_login_required():
    if "user_id" not in session:
        flash("not available", "error")
        return redirect(url_for("auth.login"))
    if session.get("role") != "student":
        flash("Access denied.", "error")
        return redirect(url_for("auth.login"))
    return None

@student_bp.route("/student/dashboard")
def dashboard():
    check = student_login_required()
    if check:
        return check

    student = Student.query.filter_by(user_id=session["user_id"]).first()
    portal = PortalSettings.query.first()
    portal_open = portal and portal.is_open
    term = Term.query.filter_by(is_current=True).first()
    grades = []

    if portal_open and term and student:
        grades = Grade.query.filter_by(
            student_id=student.id,
            term_id=term.id
        ).all()

    return render_template("student/dashboard.html",
        student=student,
        portal_open=portal_open,
        grades=grades,
        term=term
    )