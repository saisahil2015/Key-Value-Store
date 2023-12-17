# PERSISTENT SERVER CODE

# from flask import Flask, jsonify, request
# import logging
# import os
# from flask_sqlalchemy import SQLAlchemy
# from models import db, Key_value
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.orm.exc import NoResultFound

# app = Flask(__name__)

# # sqllite
# sqllite_uri = "sqlite:///" + os.path.abspath(os.path.curdir) + "/key_values.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = sqllite_uri
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db.init_app(app)

# # load existing db otherwise create new db
# with app.app_context():
#     try:
#         Key_value.query.all()
#     except:
#         db.create_all()

# # logging
# logging.basicConfig(
#     filename="app.log",
#     level=logging.DEBUG,
#     format="%(asctime)s  : %(message)s",
# )


# @app.route("/retrieve", methods=["GET"])
# def get_value():
#     given_key = request.args.get("key")
#     matched_key_value = Key_value.query.filter_by(key=given_key).first()

#     # find a given key in database
#     if matched_key_value:
#         message = f"The key [{given_key}] is found"
#         app.logger.info(message)
#         return (
#             jsonify(
#                 {
#                     "status": "success",
#                     "value": matched_key_value.value,
#                     "message": message,
#                 }
#             ),
#             200,
#         )

#     # not found
#     else:
#         message = f"The key [{given_key}] is not found"
#         app.logger.warning(message)
#         return jsonify({"status": "fail", "message": message}), 404


# @app.route("/store", methods=["PUT"])
# def put_key():
#     new_key = request.args.get("key")
#     new_value = request.form["value"]

#     try:
#         # Locking the row if it exists to prevent concurrent modifications
#         row = Key_value.query.filter_by(key=new_key).with_for_update().first()

#         # if a given key already exists in the database
#         if row:
#             message = f"The key [{new_key}] already exists"
#             app.logger.warning(message)
#             return jsonify({"status": "fail", "message": message}), 404

#         # a given key can be stored
#         else:
#             new_pair = Key_value(key=new_key, value=new_value)
#             db.session.add(new_pair)
#             db.session.commit()

#             message = f"The key [{new_key}] with the value [{new_value}] is stored"
#             app.logger.info(message)
#             return jsonify({"status": "success", "message": message}), 201

#     except IntegrityError:
#         db.session.rollback()
#         message = f"Failed to store the key [{new_key}] due to a concurrent operation. Please try again."
#         app.logger.error(message)
#         return jsonify({"status": "error", "message": message}), 500


# @app.route("/remove", methods=["DELETE"])
# def remove_key():
#     given_key = request.args.get("key")

#     try:
#         # Locking the row for deletion to prevent concurrent modifications
#         row = Key_value.query.filter_by(key=given_key).with_for_update().first()

#         if row:
#             db.session.delete(row)
#             db.session.commit()

#             message = f"The key [{given_key}] is removed"
#             app.logger.info(message)
#             return jsonify({"status": "success", "message": message}), 200

#         else:
#             message = f"The key [{given_key}] is not found"
#             app.logger.warning(message)
#             return jsonify({"status": "fail", "message": message}), 404

#     except NoResultFound:
#         db.session.rollback()
#         message = f"Failed to delete the key [{given_key}] due to a concurrent operation. Please try again."
#         app.logger.error(message)
#         return jsonify({"status": "error", "message": message}), 500


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=80, debug=True, threaded=True)


# IN-MEMORY SERVER CODE
from flask import Flask, jsonify, request
import logging
import os
import threading
import argparse

app = Flask(__name__)

# In-memory key-value store
kv_store = {}
replica_kv_store = {}
lock = threading.Lock()


# Endpoint to set the value for a key
@app.route("/store", methods=["PUT"])
def set_value():
    mode = request.args.get("mode")     # primary or replica
    new_key = request.args.get("key")
    new_value = request.form["value"]

    with lock:
        if mode == "primary":
            if new_key in kv_store:
                return jsonify(error="Key already exists"), 404

            kv_store[new_key] = new_value
            return jsonify(success=True), 201
        
        else:
            if new_key in replica_kv_store:
                return jsonify(error="Key already exists"), 404

            replica_kv_store[new_key] = new_value
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

# Endpoint to get all keys and values (primary or replica)
@app.route("/get_all", methods=["GET"])
def get_all():
    mode = request.args.get("mode")     # primary or replica
    with lock:
        if mode == "primary":
            return jsonify(kv_store), 200
        else:
            return jsonify(replica_kv_store), 200

# Endpoint to remove all keys and values (primary or replica)
@app.route("/remove_all", methods=["DELETE"])
def remove_all():
    mode = request.args.get("mode")     # primary or replica
    with lock:
        if mode == "primary":
            kv_store.clear()
            return jsonify(success=True), 200
        else:
            replica_kv_store.clear()
            return jsonify(success=True), 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--log", type=str, default="app.log")

    args = parser.parse_args()
    port = args.port
    log_filename = args.log

    # logging
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format="%(asctime)s  : %(message)s",
    )

    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
    # app.run(host="0.0.0.0", port=80, debug=True)


# MAKE SURE TO COMBINE IN-MEMORY WITH PERSISTENT DATABASE BASED ON DYNAMODB AND INFICACHE WHERE PERISSTENT USES ONLY WHEN ISSUE/SERVER DOWN OTHERWISE SHOULDN'T AFFECT THE
# PERFORMANCE
