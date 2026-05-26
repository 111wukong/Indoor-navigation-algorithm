# Indoor Navigation Algorithm — Docker Image
# EfficientNet-based indoor scene recognition server + Gradio web demo.
#
# Build:
#   docker build -t indoor-nav .
#
# Run server:
#   docker run -p 5000:5000 -v $(pwd)/weights:/app/weights indoor-nav
#
# Run Gradio demo:
#   docker run -p 7860:7860 -v $(pwd)/weights:/app/weights indoor-nav python app.py
#
# With GPU (nvidia-docker):
#   docker run --gpus all -p 7860:7860 -v $(pwd)/weights:/app/weights indoor-nav python app.py

FROM python:3.10-slim

LABEL maintainer="111wukong"
LABEL org.opencontainers.image.title="Indoor Navigation Algorithm"
LABEL org.opencontainers.image.description="EfficientNet-based indoor scene recognition"
LABEL org.opencontainers.image.url="https://github.com/111wukong/Indoor-navigation-algorithm"
LABEL org.opencontainers.image.source="https://github.com/111wukong/Indoor-navigation-algorithm"

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Working directory
# ---------------------------------------------------------------------------
WORKDIR /app

# ---------------------------------------------------------------------------
# Python dependencies (layer caching: install deps before copying code)
# ---------------------------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Application code
# ---------------------------------------------------------------------------
COPY model.py utils.py my_dataset.py pre01.py predict.py server.py config.py train.py trans_weights_to_pytorch.py app.py ./

# ---------------------------------------------------------------------------
# Ports
#   5000 — Flask server (server.py)
#   7860 — Gradio web demo (app.py)
# ---------------------------------------------------------------------------
EXPOSE 5000
EXPOSE 7860

# ---------------------------------------------------------------------------
# Runtime defaults
# ---------------------------------------------------------------------------
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=5000
ENV PYTHONUNBUFFERED=1

# Default: start the Flask server. Override CMD to run app.py or train.py.
ENTRYPOINT ["python", "server.py"]
