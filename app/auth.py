import os
import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
from app.models import User, PortalSettings

auth_bp = Blueprint("auth", __name__)

def send_otp(user):
    otp = ''.join(random.choices(string.digits, k=6))
    user.otp_code = otp
    user.otp_expires = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    if user.email:
        try:
            msg = Message(
                subject="Your David Academy Login Code",
                recipients=[user.email],
                html=f"""
                <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;background:#060d2e;border-radius:16px;padding:40px;color:#fff;">
                    <h2 style="color:#ffd700;margin-bottom:8px;">David Academy</h2>
                    <p style="color:rgba(255,255,255,0.6);margin-bottom:32px;">Student Portal</p>
                    <h3 style="font-size:15px;color:rgba(255,255,255,0.8);margin-bottom:16px;">Your login verification code:</h3>
                    <div style="background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.2);border-radius:12px;padding:24px;text-align:center;margin-bottom:24px;">
                        <span style="font-size:36px;font-weight:900;letter-spacing:8px;color:#ffd700;">{otp}</span>
                    </div>
                    <p style="color:rgba(255,255,255,0.4);font-size:13px;">This code expires in 10 minutes. Do not share it with anyone.</p>
                </div>
                """
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Mail error: {e}")
            return False
    return False

@auth_bp.route("/")
def home():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        elif session.get("role") == "teacher":
            return redirect(url_for("teacher.dashboard"))
        else:
            return redirect(url_for("student.dashboard"))
    return render_template("home.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"].strip()
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("Username not found.", "error")
        return render_template("login.html")

    if not check_password_hash(user.password_hash, password):
        flash("Wrong password.", "error")
        return render_template("login.html")

    if user.email and os.getenv("MAIL_USERNAME"):
        sent = send_otp(user)
        if sent:
            session["pending_user_id"] = user.id
            return redirect(url_for("auth.verify_otp"))

    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role

    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif user.role == "teacher":
        return redirect(url_for("teacher.dashboard"))
    else:
        return redirect(url_for("student.dashboard"))

@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "pending_user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        entered = request.form["otp"].strip()
        user = User.query.get(session["pending_user_id"])

        if not user or not user.otp_code:
            flash("Session expired. Please login again.", "error")
            return redirect(url_for("auth.login"))

        if datetime.utcnow() > user.otp_expires:
            flash("Code expired. Please login again.", "error")
            return redirect(url_for("auth.login"))

        if entered != user.otp_code:
            flash("Wrong code. Try again.", "error")
            return render_template("verify_otp.html")

        user.otp_code = None
        user.otp_expires = None
        db.session.commit()
        session.pop("pending_user_id")

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role

        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif user.role == "teacher":
            return redirect(url_for("teacher.dashboard"))
        else:
            return redirect(url_for("student.dashboard"))

    return render_template("verify_otp.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.home"))

@auth_bp.route("/api/portal-status")
def portal_status():
    portal = PortalSettings.query.first()
    is_open = portal.is_open if portal else False
    return jsonify({"is_open": is_open})

@auth_bp.route("/terms")
def terms():
    return render_template("terms.html")

@auth_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")