import os
import sys
import json
from typing import List, Dict
import base64
from datetime import datetime
import html

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def parse_json() -> dict:
    """
    Parses JSON from stdin and returns a dictionary with findings and ignored items.

    Expected JSON format:
    {
        "findings": [
            {
                "file": "path/to/file",
                "line": "42",
                "description": "Description of finding",
                "snippet": "code snippet",
                "secret": "actual secret",
                "level": 255,
                "recommendation": "How to fix this issue"
            },
            ...
        ],
        "ignored": {
            "directories": ["node_modules", ".git", ...],
            "files": ["package-lock.json", "*.min.js", ...],
            "texts": ["password123", "test-key", ...]
        }
    }

    :return: Dictionary with 'findings' and 'ignored' keys
    """
    try:
        data = json.load(sys.stdin)
        
        if isinstance(data, list):
            return {
                "findings": data,
                "ignored": {
                    "directories": [],
                    "files": [],
                    "texts": []
                }
            }
        elif isinstance(data, dict):
            findings = data.get('findings', [])
            ignored = data.get('ignored', {})
            
            # Validate findings
            if not isinstance(findings, list):
                raise ValueError("'findings' must be a list")
            
            # Validate and normalize each finding
            for finding in findings:
                if not isinstance(finding, dict):
                    raise ValueError("Each finding must be a dictionary")
                finding.setdefault('file', 'N/A')
                finding.setdefault('line', 'N/A')
                finding.setdefault('description', 'Potential secret detected')
                finding.setdefault('snippet', '')
                finding.setdefault('secret', '')
                finding.setdefault('level', 128)
                finding.setdefault('recommendation', '')

                # TODO: SANITIZE EVERYTHING HERE PLZ
            
            # Ensure ignored has all required keys
            ignored_dict = {
                "directories": ignored.get('directories', []) if isinstance(ignored, dict) else [],
                "files": ignored.get('files', []) if isinstance(ignored, dict) else [],
                "texts": ignored.get('texts', []) if isinstance(ignored, dict) else []
            }
            
            return {
                "findings": findings,
                "ignored": ignored_dict
            }
        else:
            raise ValueError("JSON must be either a list of findings or an object with 'findings' and 'ignored'")
            
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing input: {e}", file=sys.stderr)
        sys.exit(1)


def generate_html_report(
    data: dict,
    output_html_path: str = 'report.html',
    background_image_path: str = 'background.png'
) -> None:
    """
    Generates an HTML report with findings and ignored items.

    :param data: Dictionary with 'findings' and 'ignored' keys
    :param output_html_path: Path to save the HTML file
    :param background_image_path: Path to background image (optional)
    """
    findings = data.get('findings', [])
    ignored = data.get('ignored', {
        "directories": [],
        "files": [],
        "texts": []
    })

    def level_to_category(level: int) -> str:
        """Convert numeric level (0-255) to risk category."""
        pct = (level / 255) * 100
        if pct >= 80:
            return "CRITICAL"
        elif pct >= 60:
            return "HIGH"
        elif pct >= 40:
            return "MEDIUM"
        elif pct >= 20:
            return "LOW"
        else:
            return "VERY LOW"

    def level_to_rgb(level: int) -> str:
        """Convert level to RGB color (red-green gradient)."""
        level = max(0, min(255, level))
        r = level
        g = 255 - level
        b = 0
        return f"#{r:02X}{g:02X}{b:02X}"

    def level_to_border_color(level: int) -> str:
        """Get border color based on risk category."""
        pct = (level / 255) * 100
        if pct >= 80:
            return "#dc3545"  # Red for CRITICAL
        elif pct >= 60:
            return "#fd7e14"  # Orange for HIGH
        elif pct >= 40:
            return "#ffc107"  # Yellow for MEDIUM
        elif pct >= 20:
            return "#28a745"  # Green for LOW
        else:
            return "#6c757d"  # Gray for VERY LOW

    # Encode background image as base64 if it exists
    bg_image_data = ""
    if background_image_path and os.path.exists(resource_path(background_image_path)):
        with open(resource_path(background_image_path), 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
            bg_image_data = f"data:image/png;base64,{img_data}"

    # Calculate summary
    total_findings = len(findings)
    avg_level = (sum(f.get('level', 0) for f in findings) / total_findings) * 100 / 255 if total_findings > 0 else 0
    avg_level_category = level_to_category(int((avg_level / 100) * 255)) if total_findings > 0 else "N/A"

    # Build findings HTML
    findings_html = ""
    for finding in findings:
        file_path = finding.get('file', 'N/A')
        line_num = finding.get('line', 'N/A')
        description = finding.get('description', 'Potential secret detected')
        snippet = html.escape(finding.get('snippet', ''))
        secret = html.escape(finding.get('secret', ''))
        recommendation = finding.get('recommendation', '')
        level = int(finding.get('level', 128))
        category = level_to_category(level)
        bg_color = level_to_rgb(level)
        border_color = level_to_border_color(level)

        recommendation_icon = ''
        if recommendation and recommendation.strip():
            recommendation_escaped = html.escape(recommendation)
            recommendation_icon = f'<div class="recommendation-icon tooltip" data-tooltip="{recommendation_escaped}">?</div>'

        findings_html += f'''
        <div class="finding">
            <div class="finding-header">
                <span class="risk-badge" style="background-color: {border_color};">{category}</span>
                <p class="finding-desc">{description} in <code>{file_path}</code> on line <code>{line_num}</code></p>
                {recommendation_icon}
            </div>
            <span class="snippet" style="background-color: {bg_color}20; border-color: {border_color};">{snippet}</span>
            {f'<div class="secret"><strong>Secret:</strong> <code>{secret}</code></div>' if secret else ''}
        </div>
        '''

    # Build ignored items HTML
    ignored_html = ""
    if ignored.get('directories') or ignored.get('files') or ignored.get('texts'):
        ignored_html = '''
        <h2>Ignored Items</h2>
        <div class="ignored">
        '''
        
        if ignored.get('directories'):
            ignored_html += '''
            <div>
                <h3>Ignored Directories</h3>
                <ul>
            '''
            for directory in ignored['directories']:
                ignored_html += f'<li><code>{directory}</code></li>'
            ignored_html += '</ul></div>'
        
        if ignored.get('files'):
            ignored_html += '''
            <div>
                <h3>Ignored Files</h3>
                <ul>
            '''
            for file_pattern in ignored['files']:
                ignored_html += f'<li><code>{file_pattern}</code></li>'
            ignored_html += '</ul></div>'
        
        if ignored.get('texts'):
            ignored_html += '''
            <div>
                <h3>Ignored Text Patterns</h3>
                <ul>
            '''
            for text in ignored['texts']:
                ignored_html += f'<li><code>{text}</code></li>'
            ignored_html += '</ul></div>'
        
        ignored_html += '</div>'

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

    # Generate current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        
        h3 {{
            font-family: "Raleway", sans-serif;
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
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
            display: block;
            border: 2px solid;
            border-radius: 0.3em;
            padding: 0.2em 0.5em;
            font-family: "Fira Code Retina", monospace;
            font-size: 0.85em;
            margin: 0.5em 0;
            opacity: 0.9;
            width: fit-content;
            min-width: min(100%, 300px);
        }}
        
        .secret {{
            margin: 0.5em 0;
            padding: 0.5em;
            background: #fff0f0;
            border: 1px solid #ffcdcd;
            border-radius: 0.3em;
        }}
        
        .finding {{
            margin-bottom: 2.5em;
        }}
        
        .finding-desc code {{
            background: transparent;
            border: none;
            padding: 0;
            font-size: 1em;
        }}
        
        .finding-header {{
            display: flex;
            align-items: center;
            gap: 0.8em;
            margin-bottom: 0.5em;
            flex-wrap: wrap;
        }}

        .finding-header .risk-badge {{
            margin-left: 0;
            flex-shrink: 0;
        }}

        .finding-desc {{
            margin-bottom: 0;
            flex: 1;
            min-width: 200px;
        }}

        .recommendation-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #6c757d;
            color: white;
            font-size: 14px;
            font-weight: bold;
            cursor: help;
            margin-left: 8px;
            flex-shrink: 0;
            transition: background-color 0.2s;
        }}

        .recommendation-icon:hover {{
            background-color: #545b62;
        }}

        /* Tooltip styles */
        .tooltip {{
            position: relative;
        }}

        .tooltip:hover::after {{
            content: attr(data-tooltip);
            position: absolute;
            right: 0;
            top: 100%;
            background: #333;
            color: #fff;
            padding: 0.5em 1em;
            border-radius: 0.3em;
            font-size: 0.85em;
            white-space: pre-wrap;
            max-width: 300px;
            width: max-content;
            z-index: 1000;
            margin-top: 0.5em;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            border: 1px solid #444;
        }}

        .tooltip:hover::before {{
            content: '';
            position: absolute;
            right: 10px;
            top: 100%;
            border: 6px solid transparent;
            border-bottom-color: #333;
            margin-top: -12px;
            z-index: 1000;
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

        .risk-badge {{
            display: inline-block;
            padding: 0.2em 0.6em;
            border-radius: 0.3em;
            font-size: 0.75em;
            font-weight: 600;
            margin-left: 0.5em;
            color: #fff;
        }}

        .avg-risk {{
            display: inline-block;
            padding: 0.3em 0.8em;
            border-radius: 0.3em;
            font-weight: 600;
            color: #fff;
        }}
        
        .ignored {{
            background: #f5f5f5;
            padding: 1em;
            border-radius: 0.5em;
            margin-top: 1em;
        }}

        .ignored ul {{
            list-style: none;
            margin: 0.5em 0 1em 0;
        }}

        .ignored li {{
            display: inline-block;
            margin: 0.2em 0.5em 0.2em 0;
            max-width: 100%;
            word-break: break-all;
        }}

        .ignored li code {{
            background: #fff;
            word-break: break-all;
            overflow-wrap: break-word;
        }}
    </style>
</head>
<body>
    {f'<img class="background-image" src="{bg_image_data}" alt="">' if bg_image_data else ''}

    <h1>Secret Leak Report</h1>
    <p><strong>Generated:</strong> {current_time}</p>

    <h2>Summary</h2>
    <div class="summary">
        <ul>
            <li><strong>Total findings:</strong> {total_findings}</li>
            <li><strong>Average risk level:</strong> <span class="avg-risk" style="background-color: {level_to_border_color(int((avg_level / 100) * 255)) if total_findings > 0 else '#6c757d'};">{avg_level:.1f}% ({avg_level_category})</span></li>
        </ul>
    </div>
    
    <h2>Findings</h2>
    {findings_html if findings else '<p>No findings.</p>'}
    
    {ignored_html}
    
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