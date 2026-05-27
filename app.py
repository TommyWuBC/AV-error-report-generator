import tempfile
from pathlib import Path

import streamlit as st

from analyzer import analyze_log_file
from report import build_llm_prompt
from llm import generate_ai_report
from io_utils import (
    save_json_report,
    save_markdown_report,
)
from pdf_export import markdown_to_pdf
from io_utils import get_pdf_report_path

st.set_page_config(page_title="AV Fault Diagnosis Tool")

st.title("低速无人驾驶清扫车故障诊断工具")

uploaded_file = st.file_uploader(
    "上传日志文件",
    type=["log"]
)

provider_display = st.selectbox(
    "选择大模型服务",
    ["千问", "OpenAI"]
)

provider_map = {
    "千问": "qwen",
    "OpenAI": "openai",
}

provider = provider_map[provider_display]

if uploaded_file is not None:

    if st.button("生成诊断报告"):

        with st.spinner("正在分析日志..."):

            temp_dir = Path(tempfile.mkdtemp())

            log_path = temp_dir / uploaded_file.name

            with open(log_path, "wb") as f:
                f.write(uploaded_file.read())

            #first converts to json file
            analysis_result = analyze_log_file(log_path)

            save_json_report(log_path, analysis_result)

            prompt = build_llm_prompt(analysis_result)

            #generates markdown text
            ai_report = generate_ai_report(
                prompt,
                provider=provider
            )

            #produces the md file
            report_path = save_markdown_report(
                log_path,
                ai_report
            )
        pdf_path = get_pdf_report_path(log_path)
        markdown_to_pdf(ai_report, pdf_path)
        st.success("诊断完成")

        st.download_button(
            "下载 Markdown 报告",
            data=ai_report,
            file_name=pdf_path.name,
            mime="text/markdown"
        )

        st.json(analysis_result)