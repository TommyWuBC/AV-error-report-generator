# AV-error-report-generator
# Autonomous Sweeper Fault Diagnosis Tool

# 低速无人驾驶清扫车故障诊断工具

## English

### 1. Project Overview

This tool analyzes ROS/application log files from low-speed autonomous sweeper vehicles and generates a structured Chinese fault diagnosis report.

The current workflow is:

```text
Upload .log file
    ↓
Parse and aggregate log events
    ↓
Generate structured JSON analysis
    ↓
Call LLM provider
    ↓
Generate Markdown report
    ↓
Export PDF report
```

The tool is designed as a simple internal utility for operations, delivery, after-sales, and engineering teams.

---

### 2. Main Features

* Upload `.log` files through a Streamlit web interface.
* Parse structured log lines.
* Count severity levels such as `INFO`, `WARN`, `ERR`, and `FATAL`.
* Group repeated fault events.
* Apply rule-based diagnosis.
* Generate a Chinese AI diagnosis report.
* Export the final report as a PDF file.
* Support multiple LLM providers:

  * Qwen / Alibaba Cloud Model Studio
  * OpenAI

---

### 3. Recommended Environment

Tested deployment environment:

```text
Ubuntu 20.04
Python 3.8
Streamlit
Playwright
Qwen API through Alibaba Cloud Model Studio
```

Development was done on Windows, but Ubuntu compatibility was tested through a VirtualBox Ubuntu VM.

---

### 4. Setup on Ubuntu

Create and activate a Python virtual environment:

```bash
python3 -m venv ~/avtool-venv
source ~/avtool-venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browser dependency:

```bash
python -m playwright install chromium
```

---

### 5. API Key Setup

Create a `.env` file in the project root.

Example:

```text
DASHSCOPE_API_KEY=your_qwen_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

The `.env` file should not be committed to Git.

Make sure `.gitignore` contains:

```text
.env
__pycache__/
*.pyc
.venv/
```

For company deployment in China, Qwen is recommended as the default provider.

---

### 6. Running the Tool

Activate the virtual environment:

```bash
source ~/avtool-venv/bin/activate
```

Enter the project folder:

```bash
cd /path/to/AV-error-report-generator
```

Start the Streamlit app:

```bash
streamlit run app.py
```

Then open the displayed local URL in the browser.

---

### 7. How to Use

1. Upload a `.log` file.
2. Select the LLM provider.
3. Click the generate button.
4. Wait for analysis and report generation.
5. Download the generated PDF report.

---

### 8. Notes

* The tool does not send raw logs directly to the LLM.
* Logs are first parsed into structured JSON.
* The LLM receives structured fault summaries, not the full raw log file.
* This reduces token usage and helps control hallucination risk.
* The generated report should still be reviewed by an engineer before final use.

---

### 9. Known Issues

* PDF generation depends on Playwright and Chromium.
* On Windows, PDF generation may fail inside Streamlit due to event-loop/subprocess conflicts.
* This was handled by using a separate `pdf_worker.py` script.
* Python 3.8 does not support `str.removesuffix()`, so Python 3.8-compatible string slicing is used instead.

---

## 中文

### 1. 项目简介

本工具用于分析低速无人驾驶清扫车的 ROS / 应用日志文件，并自动生成中文故障诊断报告。

当前流程如下：

```text
上传 .log 日志文件
    ↓
解析并聚合日志事件
    ↓
生成结构化 JSON 分析结果
    ↓
调用大语言模型
    ↓
生成 Markdown 报告
    ↓
导出 PDF 报告
```

该工具定位为公司内部使用的轻量级故障诊断辅助工具，面向运维、交付、售后和工程团队。

---

### 2. 主要功能

* 通过 Streamlit 页面上传 `.log` 日志文件。
* 解析结构化日志行。
* 统计 `INFO`、`WARN`、`ERR`、`FATAL` 等日志等级。
* 聚合重复故障事件。
* 根据规则库进行初步故障诊断。
* 生成中文 AI 故障诊断报告。
* 导出 PDF 格式报告。
* 支持多个大模型服务：

  * 千问 / 阿里云百炼 Model Studio
  * OpenAI

---

### 3. 推荐运行环境

当前已测试环境：

```text
Ubuntu 20.04
Python 3.8
Streamlit
Playwright
阿里云百炼 / 千问 API
```

开发环境为 Windows，Ubuntu 兼容性通过 VirtualBox Ubuntu 虚拟机进行了测试。

---

### 4. Ubuntu 环境配置

创建并激活 Python 虚拟环境：

```bash
python3 -m venv ~/avtool-venv
source ~/avtool-venv/bin/activate
```

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

安装 Playwright 浏览器依赖：

```bash
python -m playwright install chromium
```

---

### 5. API Key 配置

在项目根目录创建 `.env` 文件。

示例：

```text
DASHSCOPE_API_KEY=your_qwen_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

`.env` 文件不要提交到 Git。

请确保 `.gitignore` 中包含：

```text
.env
__pycache__/
*.pyc
.venv/
```

如果部署环境在中国大陆或公司内网环境中，建议默认使用千问 / 阿里云百炼作为模型服务。

---

### 6. 启动工具

激活虚拟环境：

```bash
source ~/avtool-venv/bin/activate
```

进入项目目录：

```bash
cd /path/to/AV-error-report-generator
```

启动 Streamlit 应用：

```bash
streamlit run app.py
```

然后在浏览器中打开终端显示的本地地址。

---

### 7. 使用方法

1. 上传 `.log` 日志文件。
2. 选择大模型服务。
3. 点击生成报告按钮。
4. 等待日志分析和报告生成。
5. 下载生成的 PDF 报告。

---

### 8. 说明

* 工具不会直接把原始日志全文发送给大语言模型。
* 日志会先被解析成结构化 JSON 分析结果。
* 大语言模型接收的是结构化故障摘要，而不是完整原始日志。
* 这样可以减少 token 使用量，并降低模型幻觉风险。
* 生成的报告仍建议由工程师复核后再正式使用。

---

### 9. 已知问题

* PDF 生成依赖 Playwright 和 Chromium。
* 在 Windows 中，直接在 Streamlit 内调用 Playwright 可能因为事件循环 / 子进程冲突而失败。
* 当前通过单独的 `pdf_worker.py` 脚本进行 PDF 生成以规避该问题。
* Python 3.8 不支持 `str.removesuffix()`，因此代码中使用了兼容 Python 3.8 的字符串切片写法。
