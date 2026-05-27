from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright


def markdown_to_pdf(markdown_text, output_path):
    html_body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code"]
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: "Microsoft YaHei", "SimSun", sans-serif;
                line-height: 1.6;
                font-size: 12px;
                margin: 32px;
            }}

            h1, h2, h3 {{
                color: #222;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 12px 0;
                font-size: 10px;
            }}

            th, td {{
                border: 1px solid #999;
                padding: 6px;
                vertical-align: top;
            }}

            th {{
                background: #f2f2f2;
            }}

            code {{
                font-family: Consolas, monospace;
                font-size: 10px;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    output_path = Path(output_path)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={
                "top": "16mm",
                "right": "14mm",
                "bottom": "16mm",
                "left": "14mm",
            },
        )
        browser.close()

    return output_path