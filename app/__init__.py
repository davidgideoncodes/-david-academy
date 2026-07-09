import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-fallback-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///school.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_PERMANENT"] = True

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

    db.init_app(app)
    mail.init_app(app)

    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.teacher_routes import teacher_bp
    app.register_blueprint(teacher_bp)

    from app.routes.student_routes import student_bp
    app.register_blueprint(student_bp)

    from app.routes.payment_routes import payment_bp
    app.register_blueprint(payment_bp)

    return app