# Indoor Navigation Algorithm

EfficientNet-based indoor scene recognition system. Classifies indoor environments (corridors, rooms, stairwells, etc.) for navigation assistance.

## Architecture

```
                    ┌─────────────────┐
                    │  Input Image    │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  EfficientNet   │
                    │  (B0-B7)        │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  Classifier     │
                    │  (5 categories) │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  Prediction     │
                    └─────────────────┘
```

## Project Structure

```
Indoor-navigation-algorithm/
├── model.py                  # EfficientNet implementation (B0-B7)
├── train.py                  # Training pipeline
├── predict.py                # Single-image prediction
├── server.py                 # Flask inference server
├── pre01.py                  # Model wrapper / inference helper
├── utils.py                  # Data loading, training, evaluation utilities
├── my_dataset.py             # Custom PyTorch Dataset
├── trans_weights_to_pytorch.py  # Weight conversion utility
├── requirements.txt
├── .gitignore
└── README.md
```

## Model

The project uses [EfficientNet](https://arxiv.org/abs/1905.11946) (B0–B7 variants), a family of convolutional neural networks that achieve state-of-the-art accuracy with significantly fewer parameters through compound scaling.

| Variant | Input Size | Parameters |
|---------|-----------|------------|
| B0      | 224×224   | 5.3M       |
| B1      | 240×240   | 7.8M       |
| B2      | 260×260   | 9.2M       |
| B3      | 300×300   | 12M        |
| B4      | 380×380   | 19M        |
| B5      | 456×456   | 30M        |
| B6      | 528×528   | 43M        |
| B7      | 600×600   | 66M        |

## Training

### 1. Prepare Dataset

Organize images by category:

```
swdatasets/
├── classroom/
│   ├── img001.jpg
│   └── ...
├── corridor/
├── stairwell/
├── lobby/
└── office/
```

Download the prepared dataset:
- Baidu Netdisk: [Download](https://pan.baidu.com/s/13py_RjUj0MotVWytEm1i2Q?pwd=8kzg) (pwd: `8kzg`)

### 2. Download Pretrained Weights

| Model | Download |
|-------|----------|
| EfficientNet-B0 | [Baidu Netdisk](https://pan.baidu.com/s/1ouX0UmjCsmSx3ZrqXbowjw) (pwd: `090i`) |

### 3. Run Training

```bash
python train.py \
    --num_classes 5 \
    --epochs 30 \
    --batch-size 16 \
    --lr 0.01 \
    --data-path /path/to/swdatasets \
    --weights ./efficientnetb0.pth \
    --device cuda:0
```

Training logs are written to `runs/` — view with TensorBoard:

```bash
tensorboard --logdir=runs
# Visit http://localhost:6006
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--num_classes` | 5 | Number of output categories |
| `--epochs` | 30 | Training epochs |
| `--batch-size` | 16 | Batch size |
| `--lr` | 0.01 | Initial learning rate |
| `--lrf` | 0.01 | Final learning rate factor |
| `--data-path` | — | Dataset root directory |
| `--weights` | — | Pretrained weights path |
| `--freeze-layers` | False | Freeze backbone layers |
| `--device` | cuda:0 | Training device |

## Prediction

```python
from pre01 import Eff

model = Eff()
result = model.predict("/path/to/image.jpg")
print(result)
```

Or via the CLI:

```bash
python predict.py --image /path/to/image.jpg --weights ./weights/model-29.pth
```

## Server Deployment

Start the Flask inference server:

```bash
python server.py
# Listening on http://0.0.0.0:5000
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/recognize` | Single image recognition |
| `POST` | `/poll` | Poll-based task processing |

### Example

```bash
curl -X POST http://localhost:5000/recognize \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/path/to/image.jpg"}'
```

### Configuration (Environment Variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `https://landbigdata.swjtu.edu.cn/deep/` | Remote task queue URL |
| `INPUT_DIR` | `/root/temp/input/` | Input image directory |
| `OUTPUT_DIR` | `/root/temp/output/` | Output directory |
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `5000` | Server port |

## Requirements

```
torch>=1.7.0
torchvision>=0.8.0
flask>=2.0.0
flask-cors>=3.0.0
Pillow>=8.0.0
numpy>=1.19.0
opencv-python>=4.5.0
tqdm>=4.50.0
matplotlib>=3.3.0
requests>=2.25.0
tensorboard>=2.4.0
```

Install: `pip install -r requirements.txt`

## License

MIT
