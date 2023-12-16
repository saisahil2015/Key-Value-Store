from flask import Flask, jsonify, request
import logging
import os
from flask_sqlalchemy import SQLAlchemy
from models import db, Key_value, Workload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import json
import threading
import argparse

app = Flask(__name__)

# In-memory key-value store
kv_store = {}
lock = threading.Lock()

# sqllite
sqllite_uri = "sqlite:///" + os.path.abspath(os.path.curdir) + "/databases.db"
app.config["SQLALCHEMY_DATABASE_URI"] = sqllite_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# load existing db otherwise create new db
with app.app_context():
    try:
        Key_value.query.all()
        Workload.quert.all()
    except:
        db.create_all()

# # logging
# logging.basicConfig(
#     filename="app.log",
#     level=logging.DEBUG,
#     format="%(asctime)s  : %(message)s",
# )


@app.route("/metrics", methods=["POST"])
def store_metrics():
    """
    Store received metrics in the database.
    """
    data = request.get_json()
    try:
        new_metric = Workload(
            num_read=data["num_reads"],
            num_write=data["num_writes"],
            read_write_ratio=data["read_write_ratio"],
            mean_key_size=data["mean_key_size"],
            mean_value_size=data["mean_value_size"],
            std_key_size=data["std_key_size"],
            std_value_size=data["std_value_size"],
            var_key_size=data["var_key_size"],
            var_value_size=data["var_value_size"],
            max_cpu_usage=data["max_cpu_usage"],
            max_memory_usage=data["max_memory_usage"],
        )
        db.session.add(new_metric)
        db.session.commit()
        return (
            jsonify({"status": "success", "message": "Metrics stored successfully."}),
            201,
        )

    except KeyError:
        return jsonify({"status": "error", "message": "Malformed data."}), 400

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=90, debug=True, threaded=True)
