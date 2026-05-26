# Contributing to Indoor Navigation Algorithm

感谢你考虑为本项目做贡献！🦞

Thank you for considering contributing! Here's how you can help.

## 🐛 Bug Reports

- 在提交 issue 前，请先搜索已有 issue，避免重复
- 使用清晰的标题描述问题
- 提供复现步骤、运行环境（Python 版本、操作系统、依赖版本）
- 如果有错误日志，请完整粘贴

## 💡 Feature Requests

- 描述你希望的功能以及使用场景
- 说明为什么这个功能对项目有价值

## 🔧 Pull Requests

### 前置准备

1. Fork 本仓库，clone 到本地
2. 创建新分支：`git checkout -b feature/your-feature-name`
3. 安装开发依赖：

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 代码风格

本项目使用 [Ruff](https://github.com/astral-sh/ruff) 进行代码检查和格式化：

```bash
# 检查
ruff check .

# 自动修复
ruff check --fix .

# 格式化
ruff format .
```

### 测试

所有新功能必须包含测试。运行测试：

```bash
# 运行全部测试
pytest tests/ -v

# 带覆盖率报告
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Commit 规范

推荐使用语义化提交信息：

```
feat: 添加 Gradio Web 演示
fix: 修复模型加载时的路径错误
docs: 更新 README 安装说明
test: 添加服务器端点测试
refactor: 重构配置加载逻辑
chore: 更新 CI 配置
```

### PR 流程

1. 确保所有测试通过
2. 确保代码通过 Ruff 检查
3. PR 标题清晰，描述改动内容
4. PR 尽量小而聚焦，一个 PR 只做一件事
5. 如果是新功能，在 PR 描述中附上使用示例或截图

## 📦 项目结构

```
Indoor-navigation-algorithm/
├── app.py                     # Gradio Web 演示
├── model.py                   # EfficientNet 模型实现
├── train.py                   # 训练管线
├── predict.py                 # 单图预测 CLI
├── server.py                  # Flask 推理服务器
├── pre01.py                   # 模型封装 / 推理辅助
├── utils.py                   # 数据加载、训练、评估工具
├── my_dataset.py              # 自定义 PyTorch Dataset
├── trans_weights_to_pytorch.py # 权重转换工具
├── config.py                  # 集中配置
├── requirements.txt           # 运行时依赖
├── requirements-dev.txt       # 开发依赖
├── Dockerfile                 # Docker 镜像
├── tests/                     # 测试目录
├── .github/workflows/         # CI 配置
└── README.md
```

## ❓ 有问题？

在 GitHub Issues 中提问，我们会尽快回复。

Welcome aboard! 🚀
