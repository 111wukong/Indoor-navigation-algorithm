"""
Tests for Indoor Navigation Algorithm server (requires torch, flask).

- Model import
- Config import
- Flask app creation and endpoint tests

Mocking model dependencies so tests run without model weights or GPU.
"""

import os
import sys
from unittest import mock

import pytest

# All tests in this file require torch + flask
pytest.importorskip("torch", reason="torch not installed")
pytest.importorskip("flask", reason="flask not installed")
pytest.importorskip("flask_cors", reason="flask-cors not installed")


# ---------------------------------------------------------------------------
# Module imports (torch-level)
# ---------------------------------------------------------------------------

def test_model_import():
    """Test that model.py can be imported (no model weights needed)."""
    import model
    assert hasattr(model, "EfficientNet"), "EfficientNet class should exist"
    assert callable(model.efficientnet_b0), "efficientnet_b0 should be callable"


def test_config_import():
    """Test that config.py can be imported."""
    import config
    assert hasattr(config, "TrainConfig"), "TrainConfig should exist"
    assert hasattr(config, "ServerConfig"), "ServerConfig should exist"


# ---------------------------------------------------------------------------
# Flask app tests (with mocking for missing model dependencies)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_pre01():
    """
    Mock pre01.Eff so we can create the Flask app without real model weights,
    class_indices.json, or a GPU.

    server.py imports pre01 at module level, so we must inject the mock
    into sys.modules BEFORE server.py is imported for the first time.
    """
    mock_eff = mock.MagicMock()
    mock_eff_instance = mock.MagicMock()
    mock_eff_instance.predict.return_value = {
        "direct": "corridor",
        "rate": "0.987",
    }
    mock_eff.return_value = mock_eff_instance

    mock_pre01_module = mock.MagicMock()
    mock_pre01_module.Eff = mock_eff
    mock_pre01_module.__name__ = "pre01"

    with mock.patch.dict(sys.modules, {"pre01": mock_pre01_module}):
        yield mock_eff


class TestFlaskApp:
    """Flask app creation and endpoint tests."""

    def test_flask_app_creation(self, mock_pre01):
        """Test that the Flask app can be created (with mocked model)."""
        from server import app
        assert app is not None, "Flask app should be created"
        assert app.name == "server", f"App name should be 'server', got '{app.name}'"

    def test_health_endpoint(self, mock_pre01):
        """Test the /health endpoint returns ok status."""
        from server import app
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ok"
            assert "model_loaded" in data

    def test_recognize_missing_image_path(self, mock_pre01):
        """Test /recognize returns 400 when image_path is missing."""
        from server import app
        with app.test_client() as client:
            response = client.post(
                "/recognize",
                json={},
                content_type="application/json",
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["code"] == 400

    def test_recognize_nonexistent_image(self, mock_pre01):
        """Test /recognize returns 404 for nonexistent image."""
        from server import app
        with app.test_client() as client:
            response = client.post(
                "/recognize",
                json={"image_path": "/nonexistent/path/image.jpg"},
                content_type="application/json",
            )
            assert response.status_code == 404
            data = response.get_json()
            assert data["code"] == 404
