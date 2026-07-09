from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Student, User, Teacher, PortalSettings
from app.utils.id_generator import generate_student_id
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

def login_required(role):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    if session.get("role") != role:
        flash("You do not have permission.", "error")
        return redirect(url_for("auth.login"))
    return None

@admin_bp.route("/admin/dashboard")
def dashboard():
    check = login_required("admin")
    if check:
        return check
    students = Student.query.order_by(Student.enrolled_at.desc()).all()
    teachers = Teacher.query.all()
    portal = PortalSettings.query.first()
    return render_template("admin/dashboard.html", students=students, teachers=teachers, portal=portal)

@admin_bp.route("/admin/enroll", methods=["POST"])
def enroll_student():
    check = login_required("admin")
    if check:
        return check

    full_name = request.form["full_name"]
    date_of_birth = request.form["date_of_birth"]
    class_name = request.form["class_name"]
    parent_contact = request.form["parent_contact"]
    password = request.form["password"]

    now = datetime.now()
    existing_students = Student.query.with_entities(Student.student_id).all()
    existing_ids = [row.student_id for row in existing_students]
    new_id = generate_student_id(now.year, now.month, existing_ids, class_name=class_name)

    user = User(
        username=new_id,
        password_hash=generate_password_hash(password),
        role="student"
    )
    db.session.add(user)
    db.session.commit()

    student = Student(
        student_id=new_id,
        full_name=full_name,
        date_of_birth=date_of_birth,
        class_name=class_name,
        parent_contact=parent_contact,
        status="active",
        user_id=user.id
    )
    db.session.add(student)
    db.session.commit()

    flash(f"Student enrolled! ID: {new_id}", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/admin/create-teacher", methods=["POST"])
def create_teacher():
    check = login_required("admin")
    if check:
        return check

    full_name = request.form["full_name"]
    email = request.form["email"]
    subject = request.form["subject"]
    class_assigned = request.form["class_assigned"]
    password = request.form["password"]

    existing = User.query.filter_by(username=email).first()
    if existing:
        flash("A teacher with that email already exists.", "error")
        return redirect(url_for("admin.dashboard"))

    user = User(
        username=email,
        password_hash=generate_password_hash(password),
        role="teacher"
    )
    db.session.add(user)
    db.session.commit()

    teacher = Teacher(
        full_name=full_name,
        email=email,
        subject=subject,
        class_assigned=class_assigned,
        user_id=user.id
    )
    db.session.add(teacher)
    db.session.commit()

    flash(f"Teacher account created for {full_name}!", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/admin/toggle-portal", methods=["POST"])
def toggle_portal():
    check = login_required("admin")
    if check:
        return check

    portal = PortalSettings.query.first()
    if not portal:
        portal = PortalSettings(is_open=True, opened_at=datetime.utcnow())
        db.session.add(portal)
        flash("Portal created and opened!", "success")
    else:
        if portal.is_open:
            portal.is_open = False
            portal.closed_at = datetime.utcnow()
            flash("Portal is now CLOSED.", "error")
        else:
            portal.is_open = True
            portal.opened_at = datetime.utcnow()
            flash("Portal is now OPEN.", "success")
    db.session.commit()
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/admin/create-admin")
def create_admin():
    existing = User.query.filter_by(role="admin").first()
    if existing:
        flash("Admin account already exists.", "error")
        return redirect(url_for("auth.login"))
    admin = User(
        username="admin",
        password_hash=generate_password_hash("admin123"),
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()
    flash("Admin account created! Username: admin | Password: admin123", "success")
    return redirect(url_for("auth.login"))
