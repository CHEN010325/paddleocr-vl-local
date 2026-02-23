# PandOCR Docker 部署指南

## 📦 项目架构

```
┌─────────────────────┐
│   用户浏览器         │
│  localhost:8000     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  pandocr-web        │ ← 我们的前端服务
│  FastAPI + 静态页面  │   (端口 8000)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ paddleocr-vl-api    │ ← PaddleOCR-VL Pipeline
│  文档解析服务        │   (端口 8081)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ paddleocr-vlm-server│ ← VLLM 推理引擎
│  GPU 加速推理       │   (内部端口)
└─────────────────────┘
```

## 🚀 快速开始

### 1. 构建并启动所有服务

```bash
# 使用现有的 env.txt 文件
docker compose --env-file env.txt -f docker-compose.yml up -d --build
```

### 2. 查看服务状态

```bash
docker compose ps
```

预期输出：
```
NAME                   STATUS          PORTS
paddleocr-vlm-server   Up (healthy)    
paddleocr-vl-api       Up (healthy)    0.0.0.0:8081->8080/tcp
pandocr-web            Up (healthy)    0.0.0.0:8000->8000/tcp
```

### 3. 访问应用

- **前端界面**: http://localhost:8000
- **PaddleOCR API**: http://localhost:8081

### 4. 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f pandocr-web
docker compose logs -f paddleocr-vl-api
docker compose logs -f paddleocr-vlm-server
```

### 5. 停止服务

```bash
# 停止但保留容器和数据
docker compose stop

# 停止并删除容器（保留镜像和数据卷）
docker compose down

# 完全清理（包括数据卷）
docker compose down -v
```

## 🔧 配置说明

### 环境变量 (env.txt)

```bash
API_IMAGE_TAG_SUFFIX=latest-offline      # PaddleOCR API 镜像标签
VLM_BACKEND=vllm                         # VLM 后端类型
VLM_IMAGE_TAG_SUFFIX=latest-offline      # VLM 镜像标签
```

### 数据持久化

- **OCR 提取的图片**: 存储在 Docker 卷 `ocr_images`
  ```bash
  # 查看卷位置
  docker volume inspect pandocr_ocr_images
  
  # 备份数据
  docker run --rm -v pandocr_ocr_images:/data -v $(pwd):/backup \
    alpine tar czf /backup/ocr_images_backup.tar.gz -C /data .
  ```

### 端口配置

如果需要修改端口，编辑 `docker-compose.yml`：

```yaml
services:
  pandocr-web:
    ports:
      - "8000:8000"  # 改为 "你的端口:8000"
```

## 🛠️ 高级操作

### 仅重新构建前端服务

```bash
docker compose build pandocr-web
docker compose up -d pandocr-web
```

### 更新镜像

```bash
# 拉取最新的 PaddleOCR-VL 镜像
docker compose pull

# 重新启动
docker compose up -d
```

### 资源限制

如果需要限制资源使用，在 `docker-compose.yml` 中添加：

```yaml
services:
  pandocr-web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🐛 故障排查

### 1. 前端无法连接到后端

检查网络连接：
```bash
docker compose exec pandocr-web curl http://paddleocr-vl-api:8080/health
```

### 2. GPU 不可用

检查 NVIDIA 驱动和 Docker GPU 支持：
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi
```

### 3. 服务启动失败

查看详细日志：
```bash
docker compose logs --tail=100 [服务名]
```

### 4. 健康检查失败

手动测试健康检查端点：
```bash
curl http://localhost:8000/
curl http://localhost:8081/health
```

## 📊 监控和维护

### 查看资源使用

```bash
docker stats
```

### 清理未使用的资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune
```

## 🔒 生产环境建议

1. **使用具体的镜像版本标签**（而不是 `latest`）
2. **配置反向代理**（如 Nginx）处理 HTTPS
3. **设置资源限制**防止资源耗尽
4. **配置日志轮转**防止磁盘占满
5. **定期备份数据卷**
6. **使用环境变量管理敏感配置**

### Nginx 反向代理示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 大文件上传支持
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

## 📝 开发模式

如果需要在开发时实时更新代码：

```yaml
services:
  pandocr-web:
    volumes:
      - ./server.py:/app/server.py
      - ./static:/app/static
    command: uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

然后运行：
```bash
docker compose up -d pandocr-web
```

## 🎉 完成！

现在你的 PandOCR 应用已经完全容器化，可以轻松部署到任何支持 Docker 的环境！

