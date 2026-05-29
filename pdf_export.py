import asyncio
from pathlib import Path

import markdown
from playwright.async_api import async_playwright


async def markdown_to_pdf_async(markdown_text, output_path):
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
            table {{
                border-collapse: collapse;
                width: 100%;
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
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    output_path = Path(output_path)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="load")
        await page.pdf(
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
        await browser.close()

    return output_path


def markdown_to_pdf(markdown_text, output_path):
    return asyncio.run(markdown_to_pdf_async(markdown_text, output_path))