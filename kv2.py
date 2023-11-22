from flask import Flask, jsonify, request
import threading
import logging
import argparse

app = Flask(__name__)

# Setup logging
# logging.basicConfig(
#     filename="/app/app.log",
#     level=logging.DEBUG,
#     format="%(asctime)s  : %(message)s",
# )

# logging.basicConfig(
#     filename="app.log",
#     level=logging.DEBUG,
#     format="%(asctime)s  : %(message)s",
# )

# In-memory key-value store
kv_store = {}
lock = threading.Lock()

logging.getLogger("werkzeug").setLevel(logging.ERROR)


# Endpoint to set the value for a key
@app.route("/store", methods=["PUT"])
def set_value():
    new_key = request.args.get("key")
    new_value = request.form["value"]

    with lock:
        if new_key in kv_store:
            # app.logger.warning(f"Attempt to add an existing key: {new_key}")
            return jsonify(error="Key already exists"), 409

        kv_store[new_key] = new_value
        # app.logger.info(f"Key '{new_key}' added with value: {new_value}")
        return jsonify(success=True), 201


# Endpoint to get the value for a key
@app.route("/retrieve", methods=["GET"])
def get_value():
    key = request.args.get("key")

    with lock:
        if key in kv_store:
            value = kv_store[key]
            # app.logger.info(f"Value retrieved for key '{key}': {value}")
            return jsonify(value=value), 200
        else:
            # app.logger.warning(f"Key not found: {key}")
            return jsonify(error="Key not found"), 404


# Endpoint to delete a key
@app.route("/remove", methods=["DELETE"])
def delete_key():
    key = request.args.get("key")

    with lock:
        if key in kv_store:
            del kv_store[key]
            # app.logger.info(f"Key '{key}' removed successfully")
            return jsonify(success=True), 200
        else:
            # app.logger.warning(f"Attempt to remove non-existent key: {key}")
            return jsonify(error="Key not found"), 404


# Endpoint for batch storing key-value pairs
@app.route("/store_batch", methods=["PUT"])
def set_batch_value():
    kv_pairs = request.json
    with lock:
        for key, value in kv_pairs.items():
            kv_store[key] = value
    #         app.logger.info(f"Stored key: {key} with value: {value}")
    # app.logger.info("Batch store operation completed")
    return jsonify(success=True), 201


# Endpoint for batch retrieving values by keys
@app.route("/retrieve_batch", methods=["GET"])
def get_batch_value():
    keys = request.json
    with lock:
        values = {key: kv_store.get(key) for key in keys}
        # missing_keys = [key for key in keys if key not in kv_store]
        # app.logger.info(f"Retrieved batch values for keys: {list(values.keys())}")
        # if missing_keys:
        #     app.logger.warning(f"Keys not found in batch retrieve: {missing_keys}")
    return jsonify(values), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)


# MAKE SURE TO COMBINE IN-MEMORY WITH PERSISTENT DATABASE BASED ON DYNAMODB AND INFICACHE WHERE PERISSTENT USES ONLY WHEN ISSUE/SERVER DOWN OTHERWISE SHOULDN'T AFFECT THE
# PERFORMANCE and can refer to the persistent database code in the old_kv_backup branch
