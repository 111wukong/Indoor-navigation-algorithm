"""
Indoor Navigation — Server Module
====================================

Flask-based inference server for indoor scene recognition.
Communicates with a remote task queue via REST API.

Endpoints
---------
``GET  /health``     — Health check; returns ``{"status": "ok", "model_loaded": bool}``.
``POST /recognize``  — Single image recognition.  Body: ``{"image_path": "..."}``.
                       Returns ``{"code": 0, "result": {"direct": "...", "rate": "..."}}``.
``POST /poll``       — Poll-and-process one task from the remote queue.

Quick Start
-----------
.. code-block:: bash

   python server.py          # default: http://0.0.0.0:5000
   curl http://localhost:5000/health

   curl -X POST http://localhost:5000/recognize \\
        -H "Content-Type: application/json" \\
        -d '{"image_path": "/path/to/image.jpg"}'

Configuration
-------------
All settings are read from environment variables (see ``ServerConfig``).
"""

import json
import logging
import os
import shutil
import time
from typing import Optional

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

from pre01 import Eff

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class ServerConfig:
    """Server configuration — override via env vars or config file."""
    BASE_URL: str = os.environ.get("API_BASE_URL", "https://landbigdata.swjtu.edu.cn/deep/")
    INPUT_DIR: str = os.environ.get("INPUT_DIR", "/root/temp/input/")
    OUTPUT_DIR: str = os.environ.get("OUTPUT_DIR", "/root/temp/output/")
    HOST: str = os.environ.get("SERVER_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("SERVER_PORT", "5000"))
    POLL_INTERVAL: float = float(os.environ.get("POLL_INTERVAL", "1.0"))
    RUN_DOCKER: str = os.environ.get("RUN_DOCKER", "nvidia/cuda:10.2-efficientnet")


config = ServerConfig()

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("server")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)

# Lazy-loaded model singleton
_model: Optional[Eff] = None


def get_model() -> Eff:
    """Get or create the singleton model instance."""
    global _model
    if _model is None:
        logger.info("Loading model...")
        _model = Eff()
        logger.info("Model loaded successfully.")
    return _model


# ---------------------------------------------------------------------------
# Remote API helpers
# ---------------------------------------------------------------------------

def check_task() -> Optional[dict]:
    """Poll the remote API for a pending task."""
    url = f"{config.BASE_URL.rstrip('/')}/api/aitaskcheck"
    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json;charset=UTF-8"},
            json={"runmode": "2", "taskstatus": "2", "rundocker": config.RUN_DOCKER},
            timeout=10,
        )
        return resp.json()
    except Exception as e:
        logger.warning("Task check failed: %s", e)
        return None


def update_task(
    task_id: str,
    status: str,
    message: str = "",
    output_file: str = "",
) -> Optional[dict]:
    """Report task status back to the remote API."""
    url = f"{config.BASE_URL.rstrip('/')}/api/aitaskupdate"
    payload: dict = {
        "aitaskid": task_id,
        "taskstatus": status,
        "overtime": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if message:
        payload["resultdata"] = message
    if output_file:
        payload["resultfile"] = output_file

    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json;charset=UTF-8"},
            json=payload,
            timeout=10,
        )
        return resp.json()
    except Exception as e:
        logger.error("Task update failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """Health-check endpoint."""
    return jsonify({"status": "ok", "model_loaded": _model is not None})


@app.route("/recognize", methods=["POST"])
def recognize():
    """
    Single image recognition endpoint.

    Expects JSON body: {"image_path": "/path/to/image.jpg"}
    Returns recognition result as JSON.
    """
    data = request.get_json(silent=True)
    if not data or "image_path" not in data:
        return jsonify({"code": 400, "error": "Missing 'image_path' in request body"}), 400

    image_path = data["image_path"]
    if not os.path.exists(image_path):
        return jsonify({"code": 404, "error": f"Image not found: {image_path}"}), 404

    try:
        model = get_model()
        result = model.predict(image_path)
        logger.info("Recognition complete: %s -> %s", image_path, result)
        return jsonify({"code": 0, "result": result})
    except Exception as e:
        logger.exception("Recognition failed")
        return jsonify({"code": 500, "error": str(e)}), 500


@app.route("/poll", methods=["POST"])
def poll_tasks():
    """
    Poll-based task processing (one iteration).

    Reads one task from the remote queue, processes it, and reports back.
    Suitable for cron-based or external scheduler invocation.
    """
    task = check_task()
    if task is None:
        return jsonify({"code": 1, "message": "No task available or network error"})

    code = str(task.get("code", ""))
    if code != "843":
        return jsonify({"code": 2, "message": f"Unexpected response code: {code}"})

    try:
        task_data = task.get("data", {})
        task_type = str(task_data.get("tasktype", ""))
        task_id = str(task_data.get("aitaskid", ""))
        image_name = str(task_data.get("submitfile", ""))

        logger.info("Processing task %s (type=%s, image=%s)", task_id, task_type, image_name)

        update_task(task_id, "3")  # mark as processing

        if task_type == "1":
            source_path = os.path.join(config.INPUT_DIR, image_name)
            result_path = os.path.join(config.OUTPUT_DIR, image_name)
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)

            model = get_model()
            result = model.predict(source_path)
            shutil.copy2(source_path, result_path)

            update_task(task_id, "4", json.dumps(result), image_name)
            return jsonify({"code": 0, "task_id": task_id, "result": result})

        else:
            msg = f"Unsupported task type: {task_type}"
            update_task(task_id, "6", json.dumps({"error": msg}), image_name)
            return jsonify({"code": 3, "error": msg})

    except Exception as e:
        logger.exception("Task processing error")
        update_task(task_id, "6", json.dumps({"error": str(e)}), image_name)
        return jsonify({"code": 5, "error": str(e)}), 500


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info(
        "Starting Indoor Navigation Server on %s:%d",
        config.HOST, config.PORT,
    )
    app.run(host=config.HOST, port=config.PORT, debug=False)
