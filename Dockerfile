# Indoor Navigation Algorithm — Docker Image
# EfficientNet-based indoor scene recognition server.

FROM python:3.10-slim

LABEL maintainer="111wukong"
LABEL description="Indoor navigation inference server (EfficientNet)"

# Set working directory
WORKDIR /app

# Install system dependencies needed for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY model.py utils.py my_dataset.py pre01.py predict.py server.py config.py train.py trans_weights_to_pytorch.py ./

# Expose the server port
EXPOSE 5000

# Environment defaults (override at runtime)
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=5000

# Run the inference server
ENTRYPOINT ["python", "server.py"]
