from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from models import db, Painting, Inquiry
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from functools import wraps
import smtplib
from email.mime.text import MIMEText
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask_migrate import Migrate

app = Flask(__name__)


UPLOAD_FOLDER = "static/images"
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///database.db"

cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("CLOUD_API_KEY"),
    api_secret=os.environ.get("CLOUD_API_SECRET")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = os.environ.get("SECRET_KEY", "fallback-key")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"
db.init_app(app)
migrate = Migrate(app, db)

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper



@app.route("/inquiry", methods=["POST"])
def submit_inquiry():
    data = request.json

    new_inquiry = Inquiry(
        name=data["name"],
        phone=data["phone"],
        message=data["message"],
        painting=data["painting"],
        email=data["email"] 
    )
    
    db.session.add(new_inquiry)
    db.session.commit()

     # 🔥 SEND EMAIL HERE

    try:
        send_email(
            data["name"],
            data["phone"],
            data["message"],
            data["painting"],
            data["email"]
        )

        send_auto_reply(
            data["email"],
            data["name"],
            data["painting"]
        )

    except Exception as e:
        print("Email error:", e)
     

    return jsonify({"status": "success"})

# Language
@app.context_processor
def inject_lang():
    lang = request.args.get("lang", "en")
    return dict(lang=lang)


# Routes
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/gallery")
def gallery():
    paintings = Painting.query.all()
    return render_template("gallery.html", paintings=paintings)


@app.route("/painting/<int:id>")
def painting(id):
    painting = Painting.query.get_or_404(id)
    return render_template("painting.html", painting=painting)


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    
    
    if request.method == "POST":
        title_en = request.form["title_en"]
        title_vi = request.form["title_vi"]
        description_en = request.form["description_en"]
        description_vi = request.form["description_vi"]

        file = request.files["image"]

        if file:
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result["secure_url"]
            is_sold = "is_sold" in request.form
            painting = Painting(
                title_en=title_en,
                title_vi=title_vi,
                description_en=description_en,
                description_vi=description_vi,
                image=image_url,
                is_sold=is_sold
            )

            db.session.add(painting)
            db.session.commit()
        
        return redirect(url_for("gallery"))
    
    return render_template("admin.html")

@app.route("/admin/inquiries")
@admin_required
def admin_inquiries():
   
    
    inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin_inquiries.html", inquiries=inquiries)

@app.route("/admin/inquiry/<int:id>/delete", methods=["POST"])
@admin_required
def delete_inquiry(id):
  
    inquiry = Inquiry.query.get_or_404(id)
    db.session.delete(inquiry)
    db.session.commit()
    return jsonify({"status": "deleted"})

@app.route("/admin/inquiry/<int:id>/contacted", methods=["POST"])
@admin_required
def mark_contacted(id):
    
    inquiry = Inquiry.query.get_or_404(id)

    if not inquiry.is_contacted:  # 👈 prevent duplicate update
        inquiry.is_contacted = True
        db.session.commit()

    return jsonify({"status": "updated"})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_inquiries"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


def send_email(name, phone, message, painting, email):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    receiver = sender  # send to yourself

    subject = f"🎨 New Inquiry: {painting}"
    
    body = f"""
New customer inquiry:

Name: {name}
Phone: {phone}
Painting: {painting}
email: {email}
Message:
{message}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

    
def send_auto_reply(to_email, name, painting):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")

    subject = "🎨 Thank you for your inquiry"

    body = f"""
Hi {name},

Thank you for your interest in "{painting}".

We received your inquiry and will contact you soon.

Best regards,
Art Gallery
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)


# Create DB automatically
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port= 10000)