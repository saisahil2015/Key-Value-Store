from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Key_value(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(100), nullable=False)


class Workload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    max_memory_used = db.Column(db.Float)
    cpu_total_tottime = db.Column(db.Float)
    cpu_total_cumtime = db.Column(db.Float)
    cpu_percall_tottime = db.Column(db.Float)
    cpu_percall_cumtime = db.Column(db.Float)
