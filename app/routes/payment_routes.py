import os
import uuid
import requests
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models import Student, Payment, Term

payment_bp = Blueprint("payment", __name__)

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_placeholder")
SCHOOL_FEE_AMOUNT = 50000 * 100  # 50,000 naira in kobo

def payment_login_required():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    if session.get("role") != "student":
        return redirect(url_for("auth.login"))
    return None

@payment_bp.route("/student/pay-fees")
def pay_fees():
    check = payment_login_required()
    if check:
        return check

    student = Student.query.filter_by(user_id=session["user_id"]).first()
    term = Term.query.filter_by(is_current=True).first()
    payments = Payment.query.filter_by(student_id=student.id).order_by(Payment.created_at.desc()).all()

    term_paid = False
    if term:
        term_paid = Payment.query.filter_by(
            student_id=student.id,
            term=term.name,
            status="successful"
        ).first() is not None

    return render_template("student/payment.html",
        student=student,
        term=term,
        payments=payments,
        term_paid=term_paid,
        amount=SCHOOL_FEE_AMOUNT // 100,
        paystack_public_key=os.getenv("PAYSTACK_PUBLIC_KEY", "pk_test_placeholder")
    )

@payment_bp.route("/student/initialize-payment", methods=["POST"])
def initialize_payment():
    check = payment_login_required()
    if check:
        return check

    student = Student.query.filter_by(user_id=session["user_id"]).first()
    term = Term.query.filter_by(is_current=True).first()

    if not term:
        flash("No active term set. Contact admin.", "error")
        return redirect(url_for("payment.pay_fees"))

    reference = f"DA-{student.student_id}-{uuid.uuid4().hex[:8].upper()}"

    email = request.form.get("email", f"{student.student_id}@davidacademy.edu.ng")

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": SCHOOL_FEE_AMOUNT,
        "reference": reference,
        "channels": ["card", "bank_transfer"],
        "metadata": {
            "student_id": student.student_id,
            "student_name": student.full_name,
            "term": term.name
        },
        "callback_url": url_for("payment.verify_payment", _external=True)
    }

    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=data, headers=headers, timeout=10
        )
        result = response.json()

        if result.get("status"):
            payment = Payment(
                student_id=student.id,
                term=term.name,
                amount=SCHOOL_FEE_AMOUNT,
                reference=reference,
                status="pending"
            )
            db.session.add(payment)
            db.session.commit()
            return redirect(result["data"]["authorization_url"])
        else:
            flash("Payment initialization failed. Try again.", "error")
            return redirect(url_for("payment.pay_fees"))

    except Exception as e:
        flash("Connection error. Please try again.", "error")
        return redirect(url_for("payment.pay_fees"))

@payment_bp.route("/payment/verify")
def verify_payment():
    reference = request.args.get("reference")
    if not reference:
        return redirect(url_for("payment.pay_fees"))

    payment = Payment.query.filter_by(reference=reference).first()
    if not payment:
        flash("Payment record not found.", "error")
        return redirect(url_for("payment.pay_fees"))

    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers, timeout=10
        )
        result = response.json()

        if result.get("status") and result["data"]["status"] == "success":
            payment.status = "successful"
            payment.channel = result["data"].get("channel", "card")
            payment.paid_at = datetime.utcnow()
            db.session.commit()
            flash("Payment successful! Your fees have been recorded.", "success")
        else:
            payment.status = "failed"
            db.session.commit()
            flash("Payment was not completed.", "error")
    except Exception:
        flash("Could not verify payment. Contact admin.", "error")

    return redirect(url_for("payment.pay_fees"))

@payment_bp.route("/payment/webhook", methods=["POST"])
def webhook():
    import hmac
    import hashlib
    payload = request.get_data()
    sig = request.headers.get("x-paystack-signature")
    expected = hmac.new(
        PAYSTACK_SECRET.encode(), payload, hashlib.sha512
    ).hexdigest()

    if sig != expected:
        return jsonify({"status": "invalid"}), 400

    data = request.get_json()
    if data.get("event") == "charge.success":
        reference = data["data"]["reference"]
        payment = Payment.query.filter_by(reference=reference).first()
        if payment and payment.status != "successful":
            payment.status = "successful"
            payment.channel = data["data"].get("channel", "card")
            payment.paid_at = datetime.utcnow()
            db.session.commit()

    return jsonify({"status": "ok"}), 200