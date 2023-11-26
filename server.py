from flask import Flask, jsonify, request
import logging
import os
import threading
import argparse

app = Flask(__name__)

# In-memory key-value store
kv_store = {}
lock = threading.Lock()


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)
