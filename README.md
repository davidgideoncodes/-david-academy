# David Academy — School Management Portal

A full-stack school management web portal built with Python and Flask.

🌐 **Live:** https://david-academy.onrender.com

---

## Features

- Animated landing page with dark/light mode
- Role-based login for Admin, Teacher, and Student
- Auto-generated student IDs per class (e.g. FGC-J1-2607001)
- Admin dashboard — enroll students, create teachers, open/close result portal
- Teacher dashboard — enter test and exam scores per student
- Student dashboard — view results when portal is open
- School fee payment with card and bank transfer (Paystack)
- Payment history tracking
- OTP email verification
- Terms of Use and Privacy Policy pages
- PostgreSQL database (Neon) for persistent storage
- Deployed on Render

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, SQLAlchemy |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Database | PostgreSQL (Neon) |
| Payments | Paystack |
| Deployment | Render |
| Email | Flask-Mail (Gmail SMTP) |

---

## Running Locally

```bash
git clone https://github.com/davidgideoncodes/-david-academy.git
cd -david-academy
pip install -r requirements.txt
python run.py
```

Create a `.env` file with:
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///school.db
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-gmail-app-password
PAYSTACK_SECRET_KEY=sk_test_...
PAYSTACK_PUBLIC_KEY=pk_test_...

---

## User Roles

| Role | Login | Access |
|---|---|---|
| Admin | username: `admin` | Full system control |
| Teacher | staff email | Grade entry for assigned class |
| Student | FGC student ID | View results, pay fees |

---

 ## Built by

David Gideon — [@davidgideoncodes](https://github.com/davidgideoncodes)