import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def call_openai_report(prompt, model="gpt-4.1-mini"):
    client = OpenAI()

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    return response.output_text


def call_qwen_report(prompt, model="qwen3.6-flash"):
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is not set. Please set it before running the program."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一名低速无人驾驶清扫车运维故障诊断助手，请输出中文 Markdown 报告。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return response.choices[0].message.content


def generate_ai_report(prompt, provider="qwen"):
    if provider == "qwen":
        return call_qwen_report(prompt)

    if provider == "openai":
        return call_openai_report(prompt)

    raise ValueError(f"Unsupported LLM provider: {provider}")