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
    mean_key_size = db.Column(db.Float)
    mean_value_size = db.Column(db.Float)
    std_key_size = db.Column(db.Float)
    std_value_size = db.Column(db.Float)
    var_key_size = db.Column(db.Float)
    var_value_size = db.Column(db.Float)
    # New columns for engineered features
    read_write_product = db.Column(db.Float)
    std_size_ratio = db.Column(db.Float)
    mean_key_squared = db.Column(db.Float)
    log_num_read = db.Column(db.Float)
    max_cpu_usage = db.Column(db.Float)
    max_memory_usage = db.Column(db.Float)
