from pathlib import Path
from pprint import pprint
from analyzer import analyze_log_file
from report import generate_markdown_report, build_llm_prompt
from io_utils import save_json_report, save_markdown_report, save_ai_report
from llm import generate_ai_report
import argparse
from pdf_export import markdown_to_pdf
from io_utils import get_pdf_report_path


def main():
    parser = argparse.ArgumentParser(
        description="Analyze ROS log and generate fault diagnosis reports."
    )
    parser.add_argument(
        "log_file",
        help="Path to the ROS log file to analyze"
    )
    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider to use, e.g. openai or qwen"
    )
    args = parser.parse_args()
    log_path = Path(args.log_file)

    analysis_result = analyze_log_file(log_path)

    pprint(analysis_result)

    json_path = save_json_report(log_path, analysis_result)

    report_text = generate_markdown_report(analysis_result)
    report_path = save_markdown_report(log_path, report_text)

    print(f"Analysis JSON saved to: {json_path}")
    print(f"Report saved to: {report_path}")
    prompt = build_llm_prompt(analysis_result)
    ai_report_text = generate_ai_report(prompt, provider="qwen")
    ai_report_path = save_ai_report(log_path, ai_report_text)
    print(f"AI report saved to: {ai_report_path}")
    pdf_path = get_pdf_report_path(log_path)
    markdown_to_pdf(ai_report_text, pdf_path)
    print(f"AI PDF report saved to: {pdf_path}")


if __name__ == "__main__":
    main()