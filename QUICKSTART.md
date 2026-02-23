# 🚀 PandOCR 快速开始指南

## ⚡ 一分钟快速部署

### Windows 用户

```cmd
REM 1. 构建镜像
build.bat

REM 2. 启动服务
deploy.bat

REM 3. 访问应用
start http://localhost:8000
```

### Linux/macOS 用户

```bash
# 1. 构建镜像
chmod +x build.sh deploy.sh
./build.sh

# 2. 启动服务
./deploy.sh

# 3. 访问应用
open http://localhost:8000  # macOS
# xdg-open http://localhost:8000  # Linux
```

---

## 📝 完整步骤详解

### 步骤 1: 准备环境

**必需条件:**
- ✅ Docker Desktop 已安装并运行
- ✅ NVIDIA GPU + CUDA 12.6+ 驱动
- ✅ 至少 50GB 可用磁盘空间

**检查命令:**
```bash
docker --version
nvidia-smi
```

### 步骤 2: 获取代码

```bash
cd D:\pandocr  # 或你的项目目录
```

### 步骤 3: 构建镜像

**方式 A - 使用脚本（推荐）:**
```bash
./build.sh       # Linux/macOS
build.bat        # Windows
```

**方式 B - 手动构建:**
```bash
docker compose --env-file env.txt pull
docker compose --env-file env.txt build pandocr-web
```

⏱️ **预计时间**: 首次构建约 10-20 分钟（取决于网络速度）

### 步骤 4: 启动服务

**方式 A - 使用脚本（推荐）:**
```bash
./deploy.sh      # Linux/macOS
deploy.bat       # Windows
```

**方式 B - 手动启动:**
```bash
docker compose --env-file env.txt up -d
```

⏱️ **预计时间**: 
- PaddleOCR-VLM Server: 3-5 分钟（首次加载模型）
- PaddleOCR-VL API: 30 秒
- PandOCR Web: 10 秒

### 步骤 5: 验证服务

```bash
# 查看所有服务状态
docker compose ps

# 应该看到 3 个服务都是 "Up (healthy)"
```

### 步骤 6: 开始使用

1. 🌐 打开浏览器访问 http://localhost:8000
2. 📂 拖拽或选择文件（图片/PDF）
3. ⚙️ 选择解析选项
4. ▶️ 点击"开始解析"
5. ⬇️ 下载结果（Markdown + 图片）

---

## 🎯 常见使用场景

### 场景 1: 单张图片识别

1. 拖拽图片到上传区
2. 点击"开始解析"
3. 等待识别完成（通常 5-15 秒）
4. 点击"下载"获取 Markdown

### 场景 2: 多页 PDF 识别

1. 上传 PDF 文件
2. 系统自动拆分为多个页面
3. 点击"开始解析"
4. 逐页识别（每页约 5-15 秒）
5. 下载 ZIP 包（包含完整 Markdown + 所有图片）

### 场景 3: 批量处理多个文件

1. 一次性拖拽多个文件
2. 队列中会显示所有文件
3. 点击"开始解析"
4. 系统自动逐个处理
5. 下载合并的结果

---

## 🔧 配置选项说明

### 启用图表解析
- ✅ **推荐开启**: 用于包含表格、图表、流程图的文档
- ❌ **可关闭**: 纯文字文档，可提升速度

### 启用文档矫正
- ✅ **推荐开启**: 用于手机拍照的倾斜文档
- ❌ **可关闭**: 扫描仪生成的标准文档

### 启用方向识别
- ✅ **推荐开启**: 用于方向不确定的文档
- ❌ **可关闭**: 确定方向正确的文档

---

## 📊 性能参考

**测试环境**: NVIDIA RTX 3090 (24GB VRAM)

| 文档类型 | 页数 | 处理时间 | 识别质量 |
|---------|------|---------|---------|
| 纯文字文档 | 1 页 | 5-8 秒 | ⭐⭐⭐⭐⭐ |
| 带公式文档 | 1 页 | 8-12 秒 | ⭐⭐⭐⭐⭐ |
| 图表密集文档 | 1 页 | 12-18 秒 | ⭐⭐⭐⭐ |
| 混合复杂文档 | 1 页 | 15-20 秒 | ⭐⭐⭐⭐⭐ |
| 多页 PDF | 10 页 | 100-180 秒 | ⭐⭐⭐⭐⭐ |

---

## 🐛 遇到问题？

### Q1: "Docker 未运行"
**解决**: 启动 Docker Desktop，等待图标变绿

### Q2: "GPU 支持未检测到"
**解决**: 
```bash
# 安装 NVIDIA 驱动
nvidia-smi

# 安装 NVIDIA Container Toolkit
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### Q3: "端口 8000/8081 已被占用"
**解决**: 
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8081
taskkill /F /PID [PID号]
```

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

### Q4: "服务启动缓慢"
**原因**: 首次启动需要加载 VLLM 模型（约 5GB）  
**等待**: 3-5 分钟后再访问

### Q5: "图片显示不出来"
**解决**: 
```bash
# 检查卷权限
docker compose exec pandocr-web ls -la /app/static/ocr_images/

# 重启服务
docker compose restart pandocr-web
```

---

## 📞 获取帮助

1. 📖 查看完整文档: [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)
2. 🔍 查看日志: `docker compose logs -f`
3. 💬 提交 Issue: GitHub Issues

---

## 🎉 下一步

- 📚 阅读 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) 了解高级配置
- 🔒 配置 HTTPS 反向代理（生产环境）
- 📊 监控资源使用情况
- 🔄 定期更新镜像版本

---

**祝你使用愉快！** 🚀

