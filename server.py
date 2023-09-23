from flask import Flask, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s  : %(message)s",
)


record = {"Sahil": "Raina"}


@app.route("/get/<key>")
def getValue(key):
    if key in record:
        app.logger.info(f"Found value: {record[key]}; For key: {key}")
        return jsonify({"value": record[key]})
    app.logger.warning(f"No value found for key {key}")
    return jsonify({"error": f"No value found for key {key}"}), 404


if __name__ == "__main__":
    app.run(debug=True)
