from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Painting(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title_en = db.Column(db.String(200))
    title_vi = db.Column(db.String(200))

    description_en = db.Column(db.Text)
    description_vi = db.Column(db.Text)

    image = db.Column(db.String(200))

    is_sold = db.Column(db.Boolean, default=False)

    

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    message = db.Column(db.Text)
    painting = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_contacted = db.Column(db.Boolean, default=False) # NEW