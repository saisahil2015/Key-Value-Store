from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Key_value(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(100), nullable=False)


class Workload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_read = db.Column(db.Integer)
    num_write = db.Column(db.Integer)
    read_write_ratio = db.Column(db.Float)
    max_cpu_used = db.Column(db.Float)
    max_memory_used = db.Column(db.Float)
