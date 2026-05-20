"""
Centralized configuration for training, evaluation, and inference.

Override defaults via environment variables or by creating config.local.py.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class TrainConfig:
    """Training configuration."""
    num_classes: int = int(os.environ.get("NUM_CLASSES", "5"))
    epochs: int = int(os.environ.get("EPOCHS", "30"))
    batch_size: int = int(os.environ.get("BATCH_SIZE", "16"))
    lr: float = float(os.environ.get("LR", "0.01"))
    lrf: float = float(os.environ.get("LRF", "0.01"))
    data_path: str = os.environ.get("DATA_PATH", "/data/flower_photos")
    weights: str = os.environ.get("WEIGHTS", "./efficientnetb0.pth")
    freeze_layers: bool = os.environ.get("FREEZE_LAYERS", "false").lower() == "true"
    device: str = os.environ.get("DEVICE", "cuda:0")
    model_variant: str = os.environ.get("MODEL_VARIANT", "B0")
    seed: int = int(os.environ.get("SEED", "0"))

    @property
    def img_size(self) -> int:
        return {
            "B0": 224, "B1": 240, "B2": 260, "B3": 300,
            "B4": 380, "B5": 456, "B6": 528, "B7": 600,
        }.get(self.model_variant.upper(), 224)


@dataclass
class ServerConfig:
    """Server configuration."""
    base_url: str = os.environ.get("API_BASE_URL", "https://landbigdata.swjtu.edu.cn/deep/")
    input_dir: str = os.environ.get("INPUT_DIR", "/root/temp/input/")
    output_dir: str = os.environ.get("OUTPUT_DIR", "/root/temp/output/")
    host: str = os.environ.get("SERVER_HOST", "0.0.0.0")
    port: int = int(os.environ.get("SERVER_PORT", "5000"))
    poll_interval: float = float(os.environ.get("POLL_INTERVAL", "1.0"))
    run_docker: str = os.environ.get("RUN_DOCKER", "nvidia/cuda:10.2-efficientnet")


# Global instances
train_config = TrainConfig()
server_config = ServerConfig()
