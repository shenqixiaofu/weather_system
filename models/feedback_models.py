# models/user_models.py

from datetime import datetime
from models.weather_models import db


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    feedback_type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.now)