
#!/usr/bin/env python3
"""
CSV to HTML Table Converter

This script takes a CSV file as input from the command line and outputs
a clean HTML table with proper styling and headings.

Usage:
    python csv_to_html.py input.csv [output.html]
    python csv_to_html.py input.csv --stdout

If no output file is specified, the HTML will be printed to stdout.
"""

import csv
import sys
import argparse
import os
from html import escape


def csv_to_html(csv_file_path, output_file=None, title=None):
    """
    Convert CSV file to HTML table with styling

    Args:
        csv_file_path (str): Path to the input CSV file
        output_file (str, optional): Path to output HTML file
        title (str, optional): Title for the HTML page

    Returns:
        str: HTML content if output_file is None
    """

    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    # Use filename as default title if none provided
    if title is None:
        title = os.path.splitext(os.path.basename(csv_file_path))[0].replace('_', ' ').title()

    # Read CSV data
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.reader(csvfile, delimiter=delimiter)
            rows = list(reader)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    if not rows:
        raise ValueError("CSV file is empty")

    # Generate HTML
    html_content = generate_html(rows, title)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML table saved to: {output_file}")
    else:
        return html_content


def generate_html(rows, title):
    """
    Generate complete HTML document with styled table

    Args:
        rows (list): List of CSV rows
        title (str): Page title

    Returns:
        str: Complete HTML document
    """

    # CSS styles for the table
    css_styles = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 300;
            font-size: 2.2em;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 6px;
            overflow: hidden;
        }

        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            padding: 15px 12px;
            text-align: left;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            transition: background-color 0.2s ease;
        }

        tr:hover {
            background-color: #f8f9fa;
        }

        tr:nth-child(even) {
            background-color: #fafafa;
        }

        tr:nth-child(even):hover {
            background-color: #f0f0f0;
        }

        .table-info {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }

        .empty-cell {
            color: #999;
            font-style: italic;
        }

        @media (max-width: 768px) {
            body {
                margin: 10px;
            }

            .container {
                padding: 15px;
            }

            table {
                font-size: 12px;
            }

            th, td {
                padding: 8px 6px;
            }

            h1 {
                font-size: 1.8em;
            }
        }
    </style>
    """

    # Start building HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    {css_styles}
</head>
<body>
    <div class="container">
        <h1>{escape(title)}</h1>
        <table>
"""

    # Add table headers (first row)
    if rows:
        html += "            <thead>\n                <tr>\n"
        for header in rows[0]:
            html += f"                    <th>{escape(str(header).strip())}</th>\n"
        html += "                </tr>\n            </thead>\n"

    # Add table body
    html += "            <tbody>\n"
    for row in rows[1:]:  # Skip header row
        html += "                <tr>\n"
        for cell in row:
            cell_content = str(cell).strip()
            if not cell_content:
                html += "                    <td><span class=\"empty-cell\">—</span></td>\n"
            else:
                html += f"                    <td>{escape(cell_content)}</td>\n"
        html += "                </tr>\n"

    html += "            </tbody>\n        </table>\n"

    # Add table info
    total_rows = len(rows) - 1 if len(rows) > 1 else 0
    total_cols = len(rows[0]) if rows else 0
    html += f"""        <div class="table-info">
            Table contains {total_rows} rows and {total_cols} columns
        </div>
    </div>
</body>
</html>"""

    return html


def main():
    """Main function to handle command line arguments and execute conversion"""

    parser = argparse.ArgumentParser(
        description="Convert CSV files to clean HTML tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.csv                    # Print HTML to stdout
  %(prog)s data.csv output.html        # Save HTML to file
  %(prog)s data.csv --stdout           # Explicitly print to stdout
  %(prog)s data.csv -t "Sales Data"    # Custom table title
        """
    )

    parser.add_argument('csv_file', help='Input CSV file path')
    parser.add_argument('output_file', nargs='?', help='Output HTML file path (optional)')
    parser.add_argument('--stdout', action='store_true',
                       help='Output HTML to stdout instead of file')
    parser.add_argument('-t', '--title', help='Custom title for the HTML table')

    args = parser.parse_args()

    try:
        # Determine output method
        if args.stdout or args.output_file is None:
            # Print to stdout
            html_content = csv_to_html(args.csv_file, title=args.title)
            print(html_content)
        else:
            # Save to file
            csv_to_html(args.csv_file, args.output_file, title=args.title)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
EOF
