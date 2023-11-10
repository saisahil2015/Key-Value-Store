from flask import Flask, jsonify, request
import threading 
import logging
import argparse

app = Flask(__name__)

# In-memory key-value store
kv_store = {}
lock = threading.Lock()

# Endpoint to set the value for a key
@app.route('/store', methods=['PUT'])
def set_value():
    new_key = request.args.get("key")
    new_value = request.form["value"]

    with lock:
        if new_key in kv_store:
            return jsonify(error='Key already exists'), 404

        kv_store[new_key] = new_value
        return jsonify(success=True), 201

# Endpoint to get the value for a key
@app.route('/retrieve', methods=['GET'])
def get_value():
    key = request.args.get("key")

    with lock:
        if key in kv_store:
            value = kv_store[key]
            return jsonify(value=value), 200
        else:
            return jsonify(error='Key not found'), 404

# Endpoint to delete a key
@app.route('/remove', methods=['DELETE'])
def delete_key():
    key = request.args.get("key")

    with lock:
        if key in kv_store:
            del kv_store[key]
            return jsonify(success=True), 200
        else:
            return jsonify(error='Key not found'), 404

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--log", type=str, default="app.log")

    args = parser.parse_args()
    port = args.port
    log_filename = args.log

    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format="%(asctime)s  : %(message)s",
    )

    app.run(debug=False, port=port, host="localhost")