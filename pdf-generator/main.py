import os
from typing import List, Dict
from markdown_pdf import MarkdownPdf, Section


def generate_pdf_from_markdown(input_md_path: str, output_pdf_path: str = 'report.pdf') -> None:
    """
    Generates a PDF file from a Markdown report using markdown-pdf.

    :param input_md_path: Path to the input Markdown file
    :param output_pdf_path: Path to save the output PDF file
    """
    if not os.path.exists(input_md_path):
        raise FileNotFoundError(f"Markdown file not found: {input_md_path}")

    user_css = """
        @page {
            size: A4;
            margin: 3em;
        }
        body {
            font-family: "Raleway", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #545454;
        }
        h1 {
            font-family: "Raleway", sans-serif;
            font-weight: 700;
            color: #333;
            font-size: 1.6em;
            line-height: 1.3;
            margin-bottom: 0.8em;
        }
        h2 {
            font-family: "Raleway", sans-serif;
            font-weight: 600;
            color: #333;
            font-size: 1.3em;
            margin-top: 2em;
            margin-bottom: 0.6em;
        }
        h3 {
            font-family: "Raleway", sans-serif;
            font-weight: 600;
            color: #333;
            font-size: 1.15em;
            margin-top: 1em;
            margin-bottom: 0.6em;
        }
        p {
            margin-bottom: 1.5em;
        }
        strong, b {
            font-family: "Raleway", sans-serif;
            font-weight: 700;
        }
        em, i {
            font-family: "Raleway", sans-serif;
            font-style: italic;
        }
        a {
            color: #e74c3c;
            text-decoration: none;
        }
        blockquote {
            margin-left: 0;
            padding-left: 0.8em;
            border-left: 0.2em solid #e74c3c;
        }
        hr {
            height: 1px;
            border: 0;
            background-color: #dedede;
            margin: 0.7em 0;
        }
        code {
            background: #fcfcfc;
            border: 1px solid #dedede;
            border-radius: 0.3em;
            padding: 0.2em 0.5em;
            font-family: "Fira Code Retina", monospace;
            font-size: 0.7em;
        }
        pre code {
            display: block;
            width: 100%;
            line-height: 1.45em;
            padding: 1.2em 1em;
            margin: 0 0 1.5em;
        }
        .snippet-box {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: "Fira Code Retina", monospace;
            font-size: 0.75em;
            margin: 5px 0;
        }
        ul, ol {
            margin-bottom: 1.5em;
            padding-left: 1.5em;
        }
        ul li {
            list-style-type: none;
            text-indent: -0.45em;
        }
        ul li:before {
            content: "•";
            color: #e74c3c;
            display: inline-block;
            margin-right: 0.3em;
            font-size: 1.5em;
            vertical-align: middle;
        }
    """

    pdf = MarkdownPdf(toc_level=0)

    with open(input_md_path, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    pdf.add_section(Section(content), user_css=user_css)
    pdf.meta["title"] = "Secret Leak Report"

    dirname = os.path.dirname(output_pdf_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    pdf.save(output_pdf_path)


def generate_report(findings: List[Dict[str, str]], output_md_path: str = 'report.md') -> None:
    """
    Generates a beautiful Markdown report for potential secret leaks.

    :param findings: List of dictionaries, each containing:
        - 'file': Path to the file
        - 'line': Line number (as string)
        - 'description': Description of the finding
        - 'snippet': Code snippet
        - 'level': Risk level from 0 (green) to 255 (red)
    :param output_md_path: Path to save the Markdown file
    """
    dirname = os.path.dirname(output_md_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    def level_to_rgb(level: int) -> str:
        """Convert level (0-255) to RGB color string.
        0 = green (0x00FF00), 255 = red (0xFF0000)
        """
        level = max(0, min(255, level))
        r = level
        g = 255 - level
        b = 0
        return f"#{r:02X}{g:02X}{b:02X}"

    with open(output_md_path, 'w', encoding='utf-8') as md_file:
        # Header
        md_file.write('# Secret Leak Report\n\n')
        md_file.write('**Generated:** ' + os.popen('date').read().strip() + '\n\n')

        # Summary
        total_findings = len(findings)
        avg_level = sum(f.get('level', 0) for f in findings) / total_findings if total_findings > 0 else 0

        md_file.write('## Summary\n\n')
        md_file.write(f'- **Total findings:** {total_findings}\n')
        md_file.write(f'- **Average risk level:** {avg_level:.1f}/255\n\n')

        # Detailed Findings
        md_file.write('## Findings\n\n')

        for finding in findings:
            file_path = finding.get('file', 'N/A')
            line_num = finding.get('line', 'N/A')
            description = finding.get('description', 'Potential secret detected')
            snippet = finding.get('snippet', '')
            level = int(finding.get('level', 128))

            color = level_to_rgb(level)

            # Format: description with file and line, snippet highlighted with color
            # Use div with inline background-color for PDF compatibility
            md_file.write(f'{description} in `{file_path}` on line `{line_num}`:\n\n')
            md_file.write(f'<div class="snippet-box" style="background-color: {color}; color: #000000;">{snippet}</div>\n\n')

        md_file.write('---\n')
        md_file.write('*Generated automatically. Review findings and take appropriate action.*\n')

if __name__ == '__main__':
    sample_findings = [
        {'file': 'src/config.py', 'line': '42', 'description': 'Hardcoded API key detected', 'snippet': 'api_key = "sk-abc123"', 'level': 255},
        {'file': 'scripts/deploy.sh', 'line': '15', 'description': 'Token exposed in script', 'snippet': 'TOKEN="ghp_xxxxx"', 'level': 200},
        {'file': 'README.md', 'line': '10', 'description': 'Base64 encoded data', 'snippet': 'encoded = "aGVsbG8gd29ybGQ="', 'level': 50}
    ]
    generate_report(sample_findings, 'report.md')
    generate_pdf_from_markdown('report.md', 'report.pdf')
    print("Markdown report generated at 'report.md'")