# run.py
# This is the ONE file you run to start the entire server.
# It imports the app, creates the database tables, then starts listening.

from app import create_app, db
from app.models import Student, Teacher, Subject, Term, Grade, PortalSettings, User

app = create_app()

with app.app_context():
    db.create_all()
    # this is the command that actually creates school.db
    # it reads all your models and builds the matching tables
    print("Database tables created successfully.")

if __name__ == "__main__":
    app.run(debug=True)