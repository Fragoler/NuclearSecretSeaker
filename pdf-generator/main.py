import os
import sys
import json
from typing import List, Dict
import base64


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def parse_json() -> List[Dict[str, str]]:
    """
    Parses JSON from stdin and returns a list of findings.

    Expected JSON format:
    [
        {
            "file": "path/to/file",
            "line": "42",
            "description": "Description of finding",
            "snippet": "code snippet",
            "level": 255
        },
        ...
    ]

    :return: List of finding dictionaries
    """
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, list):
            raise ValueError("JSON must be a list of findings")

        # Validate and normalize each finding
        for finding in data:
            if not isinstance(finding, dict):
                raise ValueError("Each finding must be a dictionary")
            finding.setdefault('file', 'N/A')
            finding.setdefault('line', 'N/A')
            finding.setdefault('description', 'Potential secret detected')
            finding.setdefault('snippet', '')
            finding.setdefault('level', 128)

        return data
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)


def generate_html_report(
    findings: List[Dict[str, str]],
    output_html_path: str = 'report.html',
    background_image_path: str = 'background.png'
) -> None:
    """
    Generates an HTML report with background image.

    :param findings: List of finding dictionaries
    :param output_html_path: Path to save the HTML file
    :param background_image_path: Path to background image (optional)
    """
    def level_to_rgb(level: int) -> str:
        level = max(0, min(255, level))
        r = level
        g = 255 - level
        b = 0
        return f"#{r:02X}{g:02X}{b:02X}"

    # Encode background image as base64 if it exists
    bg_image_data = ""
    if background_image_path and os.path.exists(resource_path(background_image_path)):
        with open(resource_path(background_image_path), 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
            bg_image_data = f"data:image/jpeg;base64,{img_data}"

    # Calculate summary
    total_findings = len(findings)
    avg_level = sum(f.get('level', 0) for f in findings) / total_findings if total_findings > 0 else 0

    # Build findings HTML
    findings_html = ""
    for finding in findings:
        file_path = finding.get('file', 'N/A')
        line_num = finding.get('line', 'N/A')
        description = finding.get('description', 'Potential secret detected')
        snippet = finding.get('snippet', '')
        level = int(finding.get('level', 128))
        color = level_to_rgb(level)

        findings_html += f'''
        <div class="finding">
            <p class="finding-desc">{description} in <code>{file_path}</code> on line <code>{line_num}</code>:</p>
            <span class="snippet" style="background-color: {color}; border-color: {color};">{snippet}</span>
        </div>
        '''

    # Background image CSS or empty
    bg_css = ""
    if bg_image_data:
        bg_css = f'''
        .background-image {{
            position: fixed;
            top: 0;
            right: 0;
            width: auto;
            height: auto;
            max-width: 900px;
            z-index: -1;
            opacity: 1;
        }}
        '''

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Leak Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css?family=Raleway:400,400i,500,500i,600,600i,700,700i');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "Raleway", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #545454;
            max-width: 46em;
            margin: 2em auto;
            padding: 1.6em 3.15em;
            background-color: #fff;
        }}
        
        {bg_css}
        
        h1 {{
            font-family: "Raleway", sans-serif;
            font-weight: 700;
            color: #333;
            font-size: 1.6em;
            line-height: 1.3;
            margin-bottom: 0.8em;
        }}
        
        h2 {{
            font-family: "Raleway", sans-serif;
            font-weight: 600;
            color: #333;
            font-size: 1.3em;
            margin-top: 2em;
            margin-bottom: 0.6em;
        }}
        
        p {{
            margin-bottom: 1.5em;
        }}
        
        code {{
            display: inline;
            background: #fcfcfc;
            border: 1px solid #dedede;
            border-radius: 0.3em;
            padding: 0.2em 0.5em;
            font-family: "Fira Code Retina", monospace;
            font-size: 0.85em;
        }}
        
        .snippet {{
            display: inline-block;
            border: 1px solid;
            border-radius: 0.3em;
            padding: 0.2em 0.5em;
            font-family: "Fira Code Retina", monospace;
            font-size: 0.85em;
            margin: 0.5em 0;
        }}
        
        .finding {{
            margin-bottom: 1.5em;
        }}
        
        .finding-desc {{
            margin-bottom: 0.5em;
        }}
        
        .finding-desc code {{
            background: transparent;
            border: none;
            padding: 0;
            font-size: 1em;
        }}
        
        hr {{
            height: 1px;
            border: 0;
            background-color: #dedede;
            margin: 1.5em 0;
        }}
        
        .summary {{
            background: #f9f9f9;
            padding: 1em;
            border-radius: 0.5em;
            margin-bottom: 1.5em;
        }}
        
        .summary ul {{
            list-style: none;
            margin: 0;
        }}
        
        .summary li {{
            margin-bottom: 0.5em;
        }}
    </style>
</head>
<body>
    {"<img class=\"background-image\" src=\"" + bg_image_data + "\" alt=\"\">" if bg_image_data else ""}
    
    <h1>Secret Leak Report</h1>
    <p><strong>Generated:</strong> {os.popen('date').read().strip()}</p>
    
    <h2>Summary</h2>
    <div class="summary">
        <ul>
            <li><strong>Total findings:</strong> {total_findings}</li>
            <li><strong>Average risk level:</strong> {avg_level:.1f}/255</li>
        </ul>
    </div>
    
    <h2>Findings</h2>
    {findings_html}
    
    <hr>
    <p><em>Generated automatically. Review findings and take appropriate action.</em></p>
</body>
</html>'''

    dirname = os.path.dirname(output_html_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(output_html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)


if __name__ == '__main__':
    findings = parse_json()

    generate_html_report(findings, 'report.html')
    print("Report generated: report.html", file=sys.stderr)