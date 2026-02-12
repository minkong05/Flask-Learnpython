from flask import Flask, request, jsonify
import subprocess
import uuid
import os

app = Flask(__name__)

# For local testing
SANDBOX_SECRET = "super-long-random-string-here"

@app.route("/execute", methods=["POST"])
def execute():

    if request.headers.get("X-SANDBOX-SECRET") != SANDBOX_SECRET:
        print(SANDBOX_SECRET)
        print(request.headers.get("X-SANDBOX-SECRET"))
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    code = data.get("code", "")

    container_name = f"sandbox-{uuid.uuid4()}"

    try:
        result = subprocess.run(
            [
                "docker", "run",
                "--rm",
                "--name", container_name,
                "--network=none",
                "--memory=128m",
                "--cpus=0.5",
                "--pids-limit=32",
                "python-sandbox",
                "python3", "-c", code
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        return jsonify({
            "output": result.stdout,
            "error": result.stderr
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timeout"}), 408

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001)