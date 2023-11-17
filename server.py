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


# Endpoint to set the value for a key
@app.route("/store", methods=["PUT"])
def set_value():
    new_key = request.args.get("key")
    new_value = request.form["value"]

    with lock:
        if new_key in kv_store:
            return jsonify(error="Key already exists"), 404

        kv_store[new_key] = new_value
        return jsonify(success=True), 201


# Endpoint to get the value for a key
@app.route("/retrieve", methods=["GET"])
def get_value():
    key = request.args.get("key")

    with lock:
        if key in kv_store:
            value = kv_store[key]
            return jsonify(value=value), 200
        else:
            return jsonify(error="Key not found"), 404


# Endpoint to delete a key
@app.route("/remove", methods=["DELETE"])
def delete_key():
    key = request.args.get("key")

    with lock:
        if key in kv_store:
            del kv_store[key]
            return jsonify(success=True), 200
        else:
            return jsonify(error="Key not found"), 404


@app.route("/metrics", methods=["POST"])
def store_metrics():
    """
    Store received metrics in the database.
    """
    data = request.get_json()
    try:
        new_metric = Workload(
            num_read=data["num_read"],
            num_write=data["num_write"],
            read_write_ratio=data["read_write_ratio"],
            cpu_usage=data["cpu_usage"],
            memory_usage=data["memory_usage"],
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
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)
