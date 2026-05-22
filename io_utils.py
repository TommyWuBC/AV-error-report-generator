# io_utils.py

import json


def save_json_report(log_path, analysis_result):
    output_path = log_path.with_name(log_path.stem + "_analysis.json")

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(
            analysis_result,
            output_file,
            ensure_ascii=False,
            indent=4
        )

    return output_path

# io_utils.py

def save_markdown_report(log_path, report_text):
    report_path = log_path.with_name(log_path.stem + "_report.md")

    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_text)

    return report_path