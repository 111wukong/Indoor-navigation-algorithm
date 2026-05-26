"""
File-existence sanity checks (no dependencies required).
Runs everywhere — CI, local, Docker.
"""

import os


def test_model_file_exists():
    """Ensure model.py exists in the project root."""
    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "model.py",
    )
    assert os.path.exists(model_path), f"model.py not found at {model_path}"


def test_config_file_exists():
    """Ensure config.py exists."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "config.py",
    )
    assert os.path.exists(config_path), f"config.py not found at {config_path}"


def test_server_file_exists():
    """Ensure server.py exists."""
    server_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "server.py",
    )
    assert os.path.exists(server_path), f"server.py not found at {server_path}"


def test_requirements_file_exists():
    """Ensure requirements.txt exists."""
    req_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "requirements.txt",
    )
    assert os.path.exists(req_path), f"requirements.txt not found at {req_path}"
