from flask import Flask, jsonify, request
import logging
import os
from flask_sqlalchemy import SQLAlchemy
from models import db, Key_value
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)

# sqllite
sqllite_uri = "sqlite:///" + os.path.abspath(os.path.curdir) + "/key_values.db"
app.config["SQLALCHEMY_DATABASE_URI"] = sqllite_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# load existing db otherwise create new db
with app.app_context():
    try:
        Key_value.query.all()
    except:
        db.create_all()

# logging
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s  : %(message)s",
)


@app.route("/retrieve", methods=["GET"])
def get_value():
    given_key = request.form["key"]
    matched_key_value = Key_value.query.filter_by(key=given_key).first()

    # find a given key in database
    if matched_key_value:
        message = f"The key [{given_key}] is found"
        app.logger.info(message)
        return (
            jsonify(
                {
                    "status": "success",
                    "value": matched_key_value.value,
                    "message": message,
                }
            ),
            200,
        )

    # not found
    else:
        message = f"The key [{given_key}] is not found"
        app.logger.warning(message)
        return jsonify({"status": "fail", "message": message}), 404


@app.route("/store", methods=["PUT"])
def put_key():
    new_key = request.form["key"]
    new_value = request.form["value"]

    try:
        # Locking the row if it exists to prevent concurrent modifications
        row = Key_value.query.filter_by(key=new_key).with_for_update().first()

        # if a given key already exists in the database
        if row:
            message = f"The key [{new_key}] already exists"
            app.logger.warning(message)
            return jsonify({"status": "fail", "message": message}), 404

        # a given key can be stored
        else:
            new_pair = Key_value(key=new_key, value=new_value)
            db.session.add(new_pair)
            db.session.commit()

            message = f"The key [{new_key}] with the value [{new_value}] is stored"
            app.logger.info(message)
            return jsonify({"status": "success", "message": message}), 201

    except IntegrityError:
        db.session.rollback()
        message = f"Failed to store the key [{new_key}] due to a concurrent operation. Please try again."
        app.logger.error(message)
        return jsonify({"status": "error", "message": message}), 500


@app.route("/remove", methods=["DELETE"])
def remove_key():
    given_key = request.form["key"]

    try:
        # Locking the row for deletion to prevent concurrent modifications
        row = Key_value.query.filter_by(key=given_key).with_for_update().first()

        if row:
            db.session.delete(row)
            db.session.commit()

            message = f"The key [{given_key}] is removed"
            app.logger.info(message)
            return jsonify({"status": "success", "message": message}), 200

        else:
            message = f"The key [{given_key}] is not found"
            app.logger.warning(message)
            return jsonify({"status": "fail", "message": message}), 404

    except NoResultFound:
        db.session.rollback()
        message = f"Failed to delete the key [{given_key}] due to a concurrent operation. Please try again."
        app.logger.error(message)
        return jsonify({"status": "error", "message": message}), 500


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
