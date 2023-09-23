from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Key_value(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), nullable=False)


