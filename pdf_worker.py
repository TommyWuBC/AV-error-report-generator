import sys
from pathlib import Path

from pdf_export import markdown_to_pdf


def main():
    input_md_path = Path(sys.argv[1])
    output_pdf_path = Path(sys.argv[2])

    markdown_text = input_md_path.read_text(encoding="utf-8")

    markdown_to_pdf(markdown_text, output_pdf_path)


if __name__ == "__main__":
    main()