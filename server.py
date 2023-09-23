from flask import Flask, jsonify

app = Flask(__name__)


record = {"Sahil": "Raina"}


@app.route("/get/<key>")
def getValue(key):
    if key in record:
        return jsonify({"value": record[key]})
    return jsonify({"error": f"No value found for key {key}"}), 404


if __name__ == "__main__":
    app.run(debug=True)
