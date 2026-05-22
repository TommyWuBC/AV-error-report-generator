from pathlib import Path
from pprint import pprint
from analyzer import analyze_log_file
from report import generate_markdown_report
from io_utils import save_json_report, save_markdown_report

def main():
    log_path = Path("nav_node.log")

    analysis_result = analyze_log_file(log_path)

    pprint(analysis_result)

    json_path = save_json_report(log_path, analysis_result)

    report_text = generate_markdown_report(analysis_result)
    report_path = save_markdown_report(log_path, report_text)

    print(f"Analysis JSON saved to: {json_path}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()