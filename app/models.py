from datetime import datetime
from . import db

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(20))
    class_name = db.Column(db.String(20), nullable=False)
    parent_contact = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    grades = db.relationship("Grade", backref="student", lazy=True)
    payments = db.relationship("Payment", backref="student", lazy=True)
    def __repr__(self):
        return f"<Student {self.student_id}>"

class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    class_assigned = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    def __repr__(self):
        return f"<Teacher {self.full_name}>"

class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    grades = db.relationship("Grade", backref="subject", lazy=True)
    def __repr__(self):
        return f"<Subject {self.name}>"

class Term(db.Model):
    __tablename__ = "terms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    grades = db.relationship("Grade", backref="term", lazy=True)
    def __repr__(self):
        return f"<Term {self.name}>"

class Grade(db.Model):
    __tablename__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"), nullable=False)
    test_score = db.Column(db.Float, default=0)
    exam_score = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    def __repr__(self):
        return f"<Grade student={self.student_id} total={self.total}>"

class PortalSettings(db.Model):
    __tablename__ = "portal_settings"
    id = db.Column(db.Integer, primary_key=True)
    is_open = db.Column(db.Boolean, default=False)
    opened_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    def __repr__(self):
        return f"<PortalSettings is_open={self.is_open}>"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f"<User {self.username}>"

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    term = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    channel = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default="pending")
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f"<Payment {self.reference} {self.status}>"