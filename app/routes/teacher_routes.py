from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Student, Teacher, Grade, Term

teacher_bp = Blueprint("teacher", __name__)

def teacher_login_required():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    if session.get("role") != "teacher":
        flash("Access denied.", "error")
        return redirect(url_for("auth.login"))
    return None

@teacher_bp.route("/teacher/dashboard")
def dashboard():
    check = teacher_login_required()
    if check:
        return check

    teacher = Teacher.query.filter_by(user_id=session["user_id"]).first()
    students = Student.query.filter_by(
        class_name=teacher.class_assigned,
        status="active"
    ).all()
    term = Term.query.filter_by(is_current=True).first()

    return render_template("teacher/dashboard.html",
        teacher=teacher,
        students=students,
        term=term
    )

@teacher_bp.route("/teacher/enter-grade", methods=["POST"])
def enter_grade():
    check = teacher_login_required()
    if check:
        return check

    student_id = request.form["student_id"]
    term_id = request.form["term_id"]
    test_score = float(request.form["test_score"])
    exam_score = float(request.form["exam_score"])
    total = test_score + exam_score

    teacher = Teacher.query.filter_by(user_id=session["user_id"]).first()

    existing_grade = Grade.query.filter_by(
        student_id=student_id,
        term_id=term_id,
        subject_id=None
    ).first()

    grade = Grade.query.filter_by(
        student_id=student_id,
        term_id=term_id
    ).first()

    if grade:
        grade.test_score = test_score
        grade.exam_score = exam_score
        grade.total = total
        flash("Grade updated successfully.", "success")
    else:
        grade = Grade(
            student_id=student_id,
            term_id=term_id,
            subject_id=1,
            test_score=test_score,
            exam_score=exam_score,
            total=total
        )
        db.session.add(grade)
        flash("Grade saved successfully.", "success")

    db.session.commit()
    return redirect(url_for("teacher.dashboard"))