# PandOCR - PaddleOCR-VL Web Frontend

<div align="center">

🎨 **美观大方的苹果风格 OCR 前端** | 🚀 **基于 PaddleOCR-VL** | 🐳 **完整 Docker 支持**

</div>

---

## ✨ 特性

- 🖼️ **拖放上传** - 支持 PDF、PNG、JPG、WEBP 格式
- 📄 **PDF 多页处理** - 自动拆分 PDF 页面并逐页识别
- 📝 **Markdown 输出** - 支持数学公式、表格、图表识别
- 🎯 **图片提取** - 自动提取文档中的图表并打包下载
- 📦 **一键下载** - 智能打包 Markdown + 图片为 ZIP 文件
- 🎨 **Apple 风格界面** - 现代、简洁、响应式设计
- 🔧 **灵活配置** - 支持文档矫正、方向识别、图表解析

## 🚀 快速开始

### 方式一：Docker Compose 部署（推荐）

**完整的一键部署解决方案，包含 PaddleOCR-VL 后端和前端界面。**

#### 1. 构建镜像

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
```

**Windows:**
```cmd
build.bat
```

#### 2. 启动服务

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

#### 3. 访问应用

- 🌐 **前端界面**: http://localhost:8000
- 🔌 **后端 API**: http://localhost:8081

> 详细的 Docker 部署文档请查看 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)

---

### 方式二：本地开发模式

**如果你已经有运行中的 PaddleOCR-VL 服务。**

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 启动前端服务

```bash
python server.py
```

#### 3. 访问应用

打开浏览器访问 [http://localhost:8000](http://localhost:8000)

---

## 📋 系统要求

### Docker 部署
- **操作系统**: Linux / Windows 10+ / macOS
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **GPU**: NVIDIA GPU (推荐 12GB+ VRAM)
- **CUDA**: 12.6+
- **存储**: 至少 50GB 可用空间

### 本地开发
- **Python**: 3.10+
- **PaddleOCR-VL 服务**: 运行在 `http://localhost:8081`

---

## 🎯 使用说明

### 1️⃣ 上传文件
- 拖拽文件到上传区域
- 或点击"浏览文件"选择
- 支持一次上传多个文件

### 2️⃣ 配置选项
- ✅ **启用图表解析** - 识别图表、表格等复杂元素
- ✅ **启用文档矫正** - 自动校正倾斜或扭曲的文档
- ✅ **启用方向识别** - 自动检测和旋转文档方向

### 3️⃣ 开始解析
- 点击"开始解析"按钮
- 实时查看处理队列进度
- 结果会实时显示在右侧

### 4️⃣ 下载结果
- **有图片**: 自动打包为 ZIP（Markdown + 图片文件夹）
- **无图片**: 直接下载 Markdown 文件
- 下载的文件可直接在 VSCode 等编辑器中查看

---

## 🛠️ 配置

### 环境变量

**Docker 部署 (docker-compose.yml):**
```yaml
environment:
  - PADDLE_SERVICE_URL=http://paddleocr-vl-api:8080/layout-parsing
```

**本地开发 (server.py):**
```python
PADDLE_SERVICE_URL = os.getenv("PADDLE_SERVICE_URL", "http://localhost:8080/layout-parsing")
```

### 端口修改

修改 `docker-compose.yml`:
```yaml
services:
  pandocr-web:
    ports:
      - "你的端口:8000"
```

---

## 📦 项目结构

```
pandocr/
├── server.py                 # FastAPI 后端服务
├── requirements.txt          # Python 依赖
├── Dockerfile               # 前端服务镜像
├── docker-compose.yml       # 完整部署配置
├── env.txt                  # 环境变量配置
├── static/
│   ├── index.html          # 前端页面
│   ├── style.css           # 样式文件
│   ├── app.js              # 前端逻辑
│   └── ocr_images/         # OCR 提取的图片
├── build.sh / build.bat    # 构建脚本
├── deploy.sh / deploy.bat  # 部署脚本
├── README.md               # 本文件
└── DOCKER_DEPLOY.md        # Docker 详细文档
```

---

## 🔧 常用命令

### Docker 管理

```bash
# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f pandocr-web

# 重启服务
docker compose restart pandocr-web

# 停止服务
docker compose down

# 完全清理
docker compose down -v
```

### 开发调试

```bash
# 监听文件变化自动重启
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# 查看实时日志
python server.py
```

---

## 🐛 故障排查

### 1. 前端无法连接到后端
```bash
# 检查 PaddleOCR-VL 服务是否运行
curl http://localhost:8081/health
```

# 检查网络连接
docker compose exec pandocr-web curl http://paddleocr-vl-api:8080/health
```

### 2. GPU 不可用
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 测试 Docker GPU 支持
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi
```

### 3. 图片显示不出来
- 确保 `static/ocr_images/` 目录有写权限
- 检查浏览器控制台是否有 404 错误
- Docker 部署时检查卷挂载是否正确

---

## 📸 截图

> 现代化的苹果风格界面，左侧控制区，右侧结果展示

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 开源协议

MIT License

---

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的 OCR 引擎
- [VLLM](https://github.com/vllm-project/vllm) - 高性能推理框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架

