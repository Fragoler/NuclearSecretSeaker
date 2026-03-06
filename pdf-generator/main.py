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
        @import url('https://fonts.googleapis.com/css?family=Raleway:400,400i,500,500i,600,600i,700,700i');
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
        table {
            width: 100%;
            margin-bottom: 1.5em;
            border-collapse: collapse;
        }
        table tr {
            border-bottom: 1px solid #dedede;
        }
        table th {
            font-weight: 700;
            background-color: #f5f5f5;
        }
        table td, table th {
            vertical-align: top;
            padding: 0.4em 0.8em;
            font-size: 0.95em;
            border: 1px solid #dedede;
        }
        thead tr {
            border-bottom: 2px solid #dedede;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
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
        - 'type': Type of secret (e.g., 'API Key')
        - 'risk': Risk level (e.g., 'High', 'Medium', 'Low')
        - 'snippet': Optional code snippet (defaults to empty if not provided)
    :param output_md_path: Path to save the Markdown file
    """
    dirname = os.path.dirname(output_md_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    
    with open(output_md_path, 'w', encoding='utf-8') as md_file:
        # Header
        md_file.write('# Отчет о Потенциальных Утечках Секретов\n\n')
        md_file.write('**Дата генерации:** ' + os.popen('date').read().strip() + '\n\n')
    
        risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for finding in findings:
            risk = finding.get('risk', 'Unknown')
            if risk in risk_counts:
                risk_counts[risk] += 1
        
        md_file.write('## Общая Статистика\n\n')
        md_file.write(f'- **Общее количество находок:** {len(findings)}\n')
        md_file.write(f'- **Высокий риск:** {risk_counts["High"]}\n')
        md_file.write(f'- **Средний риск:** {risk_counts["Medium"]}\n')
        md_file.write(f'- **Низкий риск:** {risk_counts["Low"]}\n\n')
        
        # Detailed Findings Table
        md_file.write('## Детальный Отчет\n\n')
        md_file.write('| Файл | Строка | Тип Секрета | Уровень Риска | Фрагмент Кода |\n')
        md_file.write('|------|--------|-------------|---------------|---------------|\n')
        
        for finding in findings:
            file_path = finding.get('file', 'N/A')
            line_num = finding.get('line', 'N/A')
            secret_type = finding.get('type', 'N/A')
            risk_level = finding.get('risk', 'N/A')
            snippet = finding.get('snippet', '')
            
            if risk_level == 'High':
                risk_colored = f'<span style="color: red; font-weight: bold;">{risk_level}</span>'
            elif risk_level == 'Low':
                risk_colored = f'<span style="color: lightgreen; font-weight: bold;">{risk_level}</span>'
            else:
                risk_colored = f'<span style="color: orange; font-weight: bold;">{risk_level}</span>'
            
            snippet_escaped = snippet.replace('|', '\\|') if snippet else 'N/A'
            
            md_file.write(f'| {file_path} | {line_num} | {secret_type} | {risk_colored} | `{snippet_escaped}` |\n')
                
        md_file.write('---\n')
        md_file.write('*Сгенерировано автоматически. Для вопросов обращайтесь к разработчику.*\n')

if __name__ == '__main__':
    sample_findings = [
        {'file': 'src/config.py', 'line': '42', 'type': 'API Key', 'risk': 'High', 'snippet': 'api_key = "sk-abc123"'},
        {'file': 'scripts/deploy.sh', 'line': '15', 'type': 'Token', 'risk': 'Medium'},
        {'file': 'README.md', 'line': '10', 'type': 'Base64 Data', 'risk': 'Low', 'snippet': 'encoded = "aGVsbG8gd29ybGQ="'}
    ]
    generate_report(sample_findings, 'report.md')
    generate_pdf_from_markdown('report.md', 'report.pdf')
    print("Markdown report generated at 'report.md'")