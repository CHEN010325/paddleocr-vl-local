# NaviDC-OCR 冲到文档解析第一：1.2B 小模型凭什么赢过一众 OCR？附本地一键部署教程

原创 晴天 晴天 AI智探录

最近文档解析圈有个模型很值得聊：**NaviDC-OCR**。

它只有约 1.2B 参数，却在官方公布的 OmniDocBench v1.6 上拿到 96.87 分，高于 OvisOCR2 的 96.58 和 PaddleOCR-VL-1.6 的 96.33；在 Wild-OmniDocBench 上也达到 88.53。论文还显示，它在 ICDAR 2026 Sci-ImageMiner Challenge 中拿到了第一名。[官方 GitHub](https://github.com/caipeng328/NaviDC-OCR) · [官方论文](https://arxiv.org/abs/2608.12898) · [官方模型卡](https://huggingface.co/StarDoc-AI/NaviDC-OCR)

先把边界说清楚：这里的“第一”是指论文和模型卡列出的这些公开测试条件，不是说它在所有图片、所有语言、所有业务里都绝对第一。但这个结果依然很有意思——一个 1.2B 的文档专用模型，为什么能在复杂文档解析上超过更大或更早发布的方案？

这篇文章就从这个问题出发，拆解 NaviDC-OCR 为什么强、它到底升级了什么，以及如何通过我们做的本地项目一键部署，把它真正用起来。

![NaviDC-OCR 模型概览](https://raw.githubusercontent.com/caipeng328/NaviDC-OCR/main/assets/model.png)

*图片来源：NaviDC-OCR 官方 GitHub 仓库。*

## 先看成绩：它不是只在一个榜单上赢

官方模型卡列出的 OmniDocBench v1.6 对比结果如下：

| 模型 | 参数量 | Overall | Text Edit | Formula CDM | Table TEDS | Table TEDS-S | Read Order Edit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| NaviDC-OCR | 1.2B | **96.87** | 0.027 | 96.36 | **97.05** | **98.52** | 0.122 |
| OvisOCR2 | 0.8B | 96.58 | **0.025** | 97.53 | 94.76 | 97.16 | **0.111** |
| PaddleOCR-VL-1.6 | 0.9B | 96.33 | 0.033 | **97.49** | 94.76 | 97.11 | 0.127 |
| MinerU2.5-Pro | 1.2B | 95.75 | 0.036 | 97.45 | 93.42 | 95.92 | 0.120 |

这个表里有一个很容易被忽略的细节：NaviDC-OCR 并不是每个子指标都第一。它在公式 CDM、阅读顺序等项目上并不占优，但 Overall、表格 TEDS 和 TEDS-S 更突出，最终把综合分推到了第一。

翻译成人话：它不是只擅长把字认出来，而是更重视一页文档整体结构能不能还原出来。

在更接近真实拍摄环境的 Wild-OmniDocBench 上，NaviDC-OCR 的 Overall 是 88.53，PaddleOCR-VL-1.6 是 87.36，MinerU2.5-Pro 是 87.33。这个差距不算“碾压”，但说明它在非理想文档上的稳定性确实值得关注。

![NaviDC-OCR 官方评测结果](https://raw.githubusercontent.com/caipeng328/NaviDC-OCR/main/assets/score.png)

*图片来源：NaviDC-OCR 官方 GitHub 仓库。*

## 为什么它能拿到第一

### 1. 它从一开始就同时处理数字文档和拍照文档

很多 OCR 或文档解析方案，默认输入是规整 PDF：页面平整、文字清楚、版面固定。但现实里经常是手机拍的合同、倾斜的发票、弯曲的书页，或者带阴影的扫描件。

NaviDC-OCR 的名字里，DC 就是 Digital and Camera-Captured。它的目标不是为两类文档各做一个模型，而是让同一个模型同时理解电子文档和相机拍摄文档。

这点很关键，因为拍照文档最麻烦的地方往往不是文字模糊，而是几何关系变了：文字块发生透视变形，表格线弯了，阅读顺序也可能被破坏。

### 2. 几何感知，让模型不必先“完美矫正”再识别

官方介绍中提到了 Geometry-aware Document Modeling，以及面向复杂曲线的 Curvature-Guided Douglas-Peucker Sampling（CGDP）。

不用被名字吓到，它们解决的是一个很实际的问题：页面歪了、弯了、变形了，模型仍然要知道文字和版面原本处在什么关系里。

传统流水线通常是：先检测版面，再矫正图片，最后 OCR。前面的检测或矫正一旦错了，后面会连续出错。NaviDC-OCR 试图把几何信息直接融入文档理解过程，减少这种级联误差。

### 3. 表格和公式不再只当成普通文字生成

文档解析最难的部分，往往不是正文，而是表格和公式。

如果把表格当成从左到右的一串文字，单元格关系很容易丢；如果把公式当成普通字符，分式、上下标和矩阵结构也很难恢复。

NaviDC-OCR 使用 Content-Structure Decoupled Learning，把内容和结构拆开建模，再让两者重新对齐。它的思路是：文字是什么是一件事，文字在表格或公式里的结构位置是另一件事。

这也是它在表格 TEDS、TEDS-S 等指标上表现突出的原因之一。最终用户真正需要的，通常不是一段“看起来像表格”的文本，而是可以继续转换成 Markdown、HTML 或 JSON 的结构化结果。

### 4. 数据工程比单纯堆参数更重要

NaviDC-OCR 的训练方案里，还有一套很有意思的数据引擎：

- Multi-node Consensus Voting（MCV）：用多个模型结果投票，生成更可靠的伪标签；
- Geometry-aware Data Synthesis：合成更像真实拍摄的变形文档；
- Image-to-Image Self-Verification：把预测结果重新渲染成图，再和原图进行自验证；
- Progressive Data Cleaning：持续清理和筛选训练数据。

这套流程的价值在于，文档数据不只是“图片加文字答案”。版面、几何、阅读顺序、表格结构都需要同时被校验。

所以 NaviDC-OCR 的优势不只是模型参数量，而是数据怎么来、错误怎么被发现、结构怎么被重新确认。

![NaviDC-OCR 数据引擎](https://raw.githubusercontent.com/caipeng328/NaviDC-OCR/main/assets/data_engine.png)

*图片来源：NaviDC-OCR 官方 GitHub 仓库。*

### 5. 四阶段训练，把模型从“看见”训练到“看懂”

官方仓库将训练过程分成四个阶段：

1. Vision-Language Alignment：先完成视觉和语言对齐；
2. Geometry-aware Document Parsing：加入几何感知的文档解析；
3. Content-Structure Decoupled Learning：学习内容与结构的关系；
4. Reinforcement Learning：进一步优化输出质量。

这条路线比直接拿一个通用 VLM 去做 OCR 更有针对性。模型不是只学“图片里有什么”，还要学“这些内容在页面里是什么关系”。

## 它适合哪些人

如果你的任务包括下面这些内容，NaviDC-OCR 值得优先测试：

- 论文、教材、技术说明书的 PDF 解析；
- 手机拍摄的合同、票据、档案和表单；
- 需要保留结构的表格和公式抽取；
- 复杂版面、跨栏排版和图文混排文档；
- 对数据隐私有要求的本地或内网部署。

但如果只是识别几行规整文字，普通 OCR 可能更快；如果你需要极低延迟的超大规模并发，也应该先根据自己的显卡和吞吐需求做测试。榜单成绩是选型参考，不是上线前的性能承诺。

显存也要提前说清楚：项目的启动预检下限约为 7,680 MiB，但这是“有机会启动”的兼容性门槛，不是舒适运行线。考虑到模型权重、vLLM 运行时、KV Cache 以及高分辨率页面，实际建议至少 10GB，想稳定处理长 PDF 和复杂图片，推荐 12GB 及以上显卡。

## 不想自己拼环境？我们项目已经接好了

直接使用官方代码可以验证 NaviDC-OCR，但还要自己处理模型启动、PDF 分页、文件上传、Office 转换、结果展示和任务管理。

我们维护的 `paddleocr-local` 项目，把 NaviDC-OCR 接进了一个本地 WebUI。NaviDC-OCR 是文章主角，项目的作用只是把它变成一个更容易体验和落地的工具：

- 上传图片、PDF、DOCX、PPTX；
- PDF 按页解析并展示进度；
- 结果支持 Markdown、JSON 和图片资源导出；
- 本地保存任务历史；
- 同一个页面切换多个 OCR / 文档解析模型；
- 单 GPU 环境只让当前模型占用显存，切换时先停止旧模型。

## Windows + NVIDIA 一键部署 NaviDC-OCR

先安装 NVIDIA 驱动和支持 GPU 的 Docker Desktop，然后在 PowerShell 执行：

```powershell
git clone https://github.com/CHEN010325/paddleocr-local.git
cd paddleocr-local
docker --version
nvidia-smi
.\windows-one-click.bat -Model navidc-ocr
```

多卡机器可以指定显卡：

```powershell
.\windows-one-click.bat -Model navidc-ocr -GpuId 0
```

脚本会自动完成 GPU 检查、镜像构建、模型服务创建和 WebUI 启动。第一次运行会下载依赖和模型，等待时间取决于网络和磁盘速度。

部署完成后打开：

```text
http://localhost:8000
```

NaviDC-OCR 适配服务的健康检查地址是：

```powershell
curl http://localhost:8086/health
```

如果启动失败，查看日志：

```powershell
docker logs --tail 200 navidc-ocr-api
```

## Linux + Docker 部署

RTX 30/40 系列先使用普通 NVIDIA 配置：

```bash
git clone https://github.com/CHEN010325/paddleocr-local.git
cd paddleocr-local
cp env.docker env.txt
sed -i 's/^PANDOCR_ACTIVE_MODEL_ON_START=.*/PANDOCR_ACTIVE_MODEL_ON_START=navidc-ocr/' env.txt
chmod +x build.sh deploy.sh
./build.sh
./deploy.sh
```

RTX 50 / Blackwell 使用项目中的 `env.txt`，同样将：

```dotenv
PANDOCR_ACTIVE_MODEL_ON_START=navidc-ocr
```

部署后访问 `http://localhost:8000`。

## 显存不足时怎么调

项目文档给 NaviDC-OCR 的启动兼容性参考是 7,680 MiB，硬件推荐则是 12GB 以上。8GB 只能作为降低参数后的尝试，不能当作稳定运行配置。如果显存比较紧张，可以在 `env.txt` 或 `env.docker` 中调整：

```dotenv
NAVIDC_OCR_MAX_TOKENS=2048
NAVIDC_OCR_MAX_RENDER_PIXELS=40000000
NAVIDC_OCR_MAX_PAGES_PER_REQUEST=10
```

然后重新执行一键命令：

```powershell
.\windows-one-click.bat -Model navidc-ocr
```

模型缓存位于：

```text
model_cache_navidc_ocr
```

不要随便删除这个目录，否则下次启动需要重新下载权重。

## 最后总结

NaviDC-OCR 这次真正值得关注的地方，不只是 96.87 这个数字，而是它把文档解析里最难的几件事放到了一起：

- 电子文档和拍照文档统一处理；
- 几何变形直接进入模型理解过程；
- 表格和公式同时考虑内容与结构；
- 用数据引擎和自验证减少脏标签；
- 用 1.2B 参数做到相对轻量的本地部署。

如果你想先了解模型，建议直接看[官方 Hugging Face 模型卡](https://huggingface.co/StarDoc-AI/NaviDC-OCR)和[技术报告](https://arxiv.org/abs/2608.12898)。

如果你想马上把它跑起来，进入项目目录执行：

```powershell
.\windows-one-click.bat -Model navidc-ocr
```

然后打开 `http://localhost:8000`，上传一份自己的 PDF 或拍照文档，看看这个目前在公开文档解析评测中领先的 1.2B 模型，放到真实文件上到底表现怎么样。

项目地址：[CHEN010325/paddleocr-local](https://github.com/CHEN010325/paddleocr-local)
