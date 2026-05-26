# 🏠 Indoor Navigation Algorithm

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/111wukong/Indoor-navigation-algorithm/actions/workflows/ci.yml/badge.svg)](https://github.com/111wukong/Indoor-navigation-algorithm/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://hub.docker.com/)
[![Gradio](https://img.shields.io/badge/Gradio-Demo-orange?logo=gradio)](https://gradio.app/)
[![Stars](https://img.shields.io/github/stars/111wukong/Indoor-navigation-algorithm?style=social)](https://github.com/111wukong/Indoor-navigation-algorithm)

> 基于 EfficientNet 的室内场景识别系统 — 分类走廊、教室、楼梯间等室内环境，辅助室内导航。
>
> EfficientNet-based indoor scene recognition for navigation assistance.

**语言切换**：本文档为中文。For English, see [below](#english).

---

## 📸 Demo

启动 Gradio Web 演示：

```bash
pip install -r requirements.txt
python app.py
# 打开浏览器访问 http://localhost:7860
```

<p align="center">
  <img src="https://via.placeholder.com/600x400/0f172a/60a5fa?text=Indoor+Scene+Recognition+Demo" alt="Gradio Demo Screenshot" width="600">
</p>

> 💡 **功能**：上传图片或拍照 → 显示场景类别 + 置信度 → Top-3 预测结果排名
>
> **Features**：Upload or snap → scene class + confidence → top-3 predictions ranked

---

## 🏗 项目架构 / Architecture

```
                          ┌──────────────────────────┐
                          │      Gradio Web UI       │
                          │      (app.py :7860)       │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │     Flask API Server      │
                          │    (server.py :5000)      │
                          │  /health  /recognize      │
                          │  /poll    (task queue)    │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │    pre01.Eff (Inference)  │
                          │  ┌─────────────────────┐  │
                          │  │  EfficientNet V2-S   │  │
                          │  │  (PyTorch Backend)   │  │
                          │  └─────────────────────┘  │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │    5-Class Prediction     │
                          │  classroom  ·  corridor   │
                          │  stairwell  ·  lobby      │
                          │  office                   │
                          └──────────────────────────┘
```

---

## 📁 项目结构 / Project Structure

```
Indoor-navigation-algorithm/
├── app.py                     # Gradio Web 演示 🌐
├── model.py                   # EfficientNet B0-B7 实现
├── train.py                   # 训练管线
├── predict.py                 # 单图预测 CLI
├── server.py                  # Flask API 推理服务器
├── pre01.py                   # 模型封装 / 推理辅助
├── utils.py                   # 数据加载、训练、评估工具
├── my_dataset.py              # 自定义 PyTorch Dataset
├── trans_weights_to_pytorch.py # 权重转换工具
├── config.py                  # 集中配置管理
├── requirements.txt           # 运行时依赖
├── requirements-dev.txt       # 开发依赖 (pytest, ruff, coverage)
├── Dockerfile                 # Docker 镜像
├── .dockerignore
├── tests/                     # 测试目录
├── .github/workflows/         # CI 配置
├── CONTRIBUTING.md            # 贡献指南
└── README.md
```

---

## 🚀 快速开始 / Quick Start

### 方式一：本地运行

**环境要求**：Python 3.9+，推荐使用虚拟环境。

```bash
# 1. 克隆仓库
git clone https://github.com/111wukong/Indoor-navigation-algorithm.git
cd Indoor-navigation-algorithm

# 2. 安装依赖
pip install -r requirements.txt

# 3. 准备模型权重（二选一）
#    方式 A：使用你训练好的权重，放入 weights/ 目录
#    方式 B：下载预训练权重
#       Baidu Netdisk: https://pan.baidu.com/s/1ouX0UmjCsmSx3ZrqXbowjw  (pwd: 090i)

# 4a. 启动 Gradio Web 演示
python app.py
# 访问 http://localhost:7860

# 4b. 或启动 Flask API 服务器
python server.py
# 访问 http://localhost:5000

# 4c. 或训练自己的模型
python train.py --data-path /path/to/dataset --epochs 30 --batch-size 16
```

### 方式二：Docker 运行

```bash
# 构建镜像
docker build -t indoor-nav .

# 运行 Gradio Web 演示
docker run -p 7860:7860 \
  -v $(pwd)/weights:/app/weights \
  indoor-nav python app.py

# 运行 Flask API 服务器
docker run -p 5000:5000 \
  -v $(pwd)/weights:/app/weights \
  indoor-nav

# GPU 加速（需要 nvidia-docker）
docker run --gpus all -p 7860:7860 \
  -v $(pwd)/weights:/app/weights \
  indoor-nav python app.py
```

访问：
- Gradio 演示：http://localhost:7860
- Flask API：http://localhost:5000

---

## 🧠 模型 / Model

本项目使用 [EfficientNet](https://arxiv.org/abs/1905.11946) 架构，通过**复合缩放**（compound scaling）在参数量与精度之间取得优异平衡。预训练推理使用 EfficientNet V2-S。

| 变体 | 输入尺寸 | 参数量 | 用途 |
|------|---------|--------|------|
| B0 | 224×224 | 5.3M | 快速推理 / 移动端 |
| B1 | 240×240 | 7.8M | 边缘设备 |
| B2 | 260×260 | 9.2M | 平衡选择 |
| B3 | 300×300 | 12M | 服务器推理 |
| B4 | 380×380 | 19M | 高精度场景 |
| B5 | 456×456 | 30M | 大规模部署 |
| B6 | 528×528 | 43M | 研究用途 |
| B7 | 600×600 | 66M | 最佳精度 |

---

## 📊 训练 / Training

### 1. 准备数据集

按类别组织图片：

```
dataset/
├── classroom/
│   ├── img001.jpg
│   └── ...
├── corridor/
├── stairwell/
├── lobby/
└── office/
```

数据集下载：
- 百度网盘：[下载链接](https://pan.baidu.com/s/13py_RjUj0MotVWytEm1i2Q?pwd=8kzg) (提取码: `8kzg`)

### 2. 下载预训练权重

| 模型 | 下载 |
|------|------|
| EfficientNet-B0 | [百度网盘](https://pan.baidu.com/s/1ouX0UmjCsmSx3ZrqXbowjw) (提取码: `090i`) |

### 3. 开始训练

```bash
python train.py \
    --num_classes 5 \
    --epochs 30 \
    --batch-size 16 \
    --lr 0.01 \
    --data-path /path/to/dataset \
    --weights ./efficientnetb0.pth \
    --device cuda:0
```

训练日志写入 `runs/` 目录，使用 TensorBoard 查看：

```bash
tensorboard --logdir=runs
# 访问 http://localhost:6006
```

### 训练参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--num_classes` | 5 | 输出类别数 |
| `--epochs` | 30 | 训练轮数 |
| `--batch-size` | 16 | 批次大小 |
| `--lr` | 0.01 | 初始学习率 |
| `--lrf` | 0.01 | 最终学习率因子 (Cosine) |
| `--data-path` | `/data/flower_photos` | 数据集根目录 |
| `--weights` | `./efficientnetb0.pth` | 预训练权重路径 |
| `--freeze-layers` | False | 冻结骨干网络 |
| `--device` | `cuda:0` | 训练设备 |

---

## 🔮 推理 / Inference

### Python API

```python
from pre01 import Eff

model = Eff()
result = model.predict("/path/to/image.jpg")
print(result)
# {'direct': 'corridor', 'rate': '0.987'}
```

### Flask API 服务器

```bash
# 启动服务
python server.py
# Listening on http://0.0.0.0:5000
```

#### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/recognize` | 单图识别 |
| `POST` | `/poll` | 任务队列轮询处理 |

#### 示例

```bash
# 健康检查
curl http://localhost:5000/health

# 图片识别
curl -X POST http://localhost:5000/recognize \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/path/to/image.jpg"}'
```

#### 配置（环境变量）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `API_BASE_URL` | `https://landbigdata.swjtu.edu.cn/deep/` | 远程任务队列 URL |
| `INPUT_DIR` | `/root/temp/input/` | 输入图片目录 |
| `OUTPUT_DIR` | `/root/temp/output/` | 输出目录 |
| `SERVER_HOST` | `0.0.0.0` | 服务器绑定地址 |
| `SERVER_PORT` | `5000` | 服务器端口 |

---

## 📦 依赖 / Requirements

**运行时** (`requirements.txt`)：

```
torch>=1.7.0, torchvision>=0.8.0, flask>=2.0.0, flask-cors>=3.0.0
Pillow>=8.0.0, numpy>=1.19.0, opencv-python>=4.5.0
gradio>=4.0.0, tqdm>=4.50.0, matplotlib>=3.3.0
requests>=2.25.0, tensorflow>=2.4.0, tensorboard>=2.4.0
```

**开发** (`requirements-dev.txt`)：

```
pytest>=7.0.0, pytest-cov>=4.0.0, pytest-mock>=3.10.0
ruff>=0.4.0, coverage>=7.0.0
```

安装：

```bash
pip install -r requirements.txt        # 运行时
pip install -r requirements-dev.txt    # 开发
```

---

## 🤝 贡献 / Contributing

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

- 🐛 提交 Bug → [GitHub Issues](https://github.com/111wukong/Indoor-navigation-algorithm/issues)
- 💡 功能建议 → [GitHub Issues](https://github.com/111wukong/Indoor-navigation-algorithm/issues)
- 🔧 Pull Request → Fork → 新分支 → 写测试 → 提交 PR

---

## 📚 引用 / Citation

如果本项目对你的研究有帮助，请引用：

```bibtex
@misc{indoor-navigation-algorithm,
  author       = {111wukong},
  title        = {Indoor Navigation Algorithm},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/111wukong/Indoor-navigation-algorithm}},
}
```

```bibtex
@inproceedings{tan2019efficientnet,
  title     = {EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks},
  author    = {Tan, Mingxing and Le, Quoc V.},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2019},
  url       = {https://arxiv.org/abs/1905.11946}
}
```

---

## 📄 许可证 / License

MIT License. 详见 [LICENSE](LICENSE)。

---

---

<a name="english"></a>

## 🏠 Indoor Navigation Algorithm (English)

EfficientNet-based indoor scene recognition system. Classifies indoor environments
(corridors, classrooms, stairwells, lobbies, offices) for navigation assistance.

### Quick Start

```bash
git clone https://github.com/111wukong/Indoor-navigation-algorithm.git
cd Indoor-navigation-algorithm
pip install -r requirements.txt

# Web demo
python app.py  # → http://localhost:7860

# API server
python server.py  # → http://localhost:5000

# Training
python train.py --data-path /path/to/dataset --epochs 30
```

### Docker

```bash
docker build -t indoor-nav .
docker run -p 7860:7860 -v $(pwd)/weights:/app/weights indoor-nav python app.py
```

### API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/recognize` | Single image recognition |
| POST | `/poll` | Task queue polling |

See the Chinese section above for full documentation, or open an
[issue](https://github.com/111wukong/Indoor-navigation-algorithm/issues) if you have questions.
