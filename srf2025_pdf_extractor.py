#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRF2025 Conference PDF Contributions Extractor

Author: Ming Liu
Date: September 29, 2025
Description: Extract contributions from SRF2025 conference PDF and create
             interactive data explorer similar to IBIC2025.

PDF Source: contributions.pdf (SRF2025 conference proceedings)
Features:
- PDF text extraction from page 2 to end
- Contribution information parsing
- Session-based organization
- Multi-format data export (JSON, CSV, HTML)
- Interactive web interface
"""

import os
import re
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import PyPDF2
import pandas as pd

class SRF2025PDFExtractor:
    """
    PDF extractor for SRF2025 conference contributions.

    This extractor reads the SRF2025 contributions PDF and extracts
    paper information organized by sessions and types.
    """

    def __init__(self, pdf_path: str = "contributions.pdf", output_dir: str = "SRF2025_Data"):
        """
        Initialize the SRF2025 PDF extractor.

        Args:
            pdf_path: Path to the contributions PDF file
            output_dir: Directory to store extracted data
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.contributions = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('srf2025_extractor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

    def extract_contributions(self) -> List[Dict[str, Any]]:
        """
        Extract all contributions from the PDF.

        Returns:
            List of contribution dictionaries
        """
        self.logger.info(f"Opening PDF: {self.pdf_path}")

        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)

                self.logger.info(f"PDF has {total_pages} pages, processing pages 2-{total_pages}")

                # Process pages from 2 to end (skip title page)
                for page_num in range(1, total_pages):  # 0-indexed, so page 1 is actually page 2
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()

                        if text.strip():  # Only process non-empty pages
                            contribution = self.parse_contribution_page(text, page_num + 1)
                            if contribution:
                                self.contributions.append(contribution)
                                self.logger.info(f"Extracted contribution: {contribution['contribution_code']} - {contribution['title'][:50]}...")

                    except Exception as e:
                        self.logger.error(f"Error processing page {page_num + 1}: {e}")
                        continue

        except Exception as e:
            self.logger.error(f"Error opening PDF: {e}")
            return []

        self.logger.info(f"Successfully extracted {len(self.contributions)} contributions")
        return self.contributions

    def parse_contribution_page(self, text: str, page_num: int) -> Optional[Dict[str, Any]]:
        """
        Parse a single contribution page.

        Args:
            text: Extracted text from the page
            page_num: Page number (for debugging)

        Returns:
            Dictionary containing contribution information
        """
        contribution = {
            'contribution_id': '',
            'contribution_code': '',
            'type': '',
            'title': '',
            'date_time': '',
            'abstract': '',
            'footnotes': '',
            'session': '',
            'session_code': '',
            'page_number': page_num
        }

        try:
            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]

            # Extract contribution ID
            id_match = re.search(r'Contribution ID:\s*(\d+)', text)
            if id_match:
                contribution['contribution_id'] = id_match.group(1)

            # Extract contribution code
            code_match = re.search(r'Contribution code:\s*([A-Z]+\d+)', text)
            if code_match:
                contribution['contribution_code'] = code_match.group(1)

                # Determine session from contribution code
                if len(contribution['contribution_code']) >= 3:
                    session_code = contribution['contribution_code'][:3]
                    contribution['session_code'] = session_code
                    contribution['session'] = self.get_session_name(session_code)

            # Extract type
            type_match = re.search(r'Type:\s*([^\n]+)', text)
            if type_match:
                contribution['type'] = type_match.group(1).strip()

            # Extract date and time
            datetime_match = re.search(r'(\w+day, \w+ \d+, \d{4} \d+:\d+\s*[AP]M.*?)(?:\(|$)', text)
            if datetime_match:
                contribution['date_time'] = datetime_match.group(1).strip()

            # Find the title - it usually comes after the contribution code and type
            # Look for the first substantial line that could be a title
            title_found = False
            abstract_start = False
            abstract_lines = []

            for i, line in enumerate(lines):
                # Skip header information
                if any(skip in line.lower() for skip in ['contribution id:', 'contribution code:', 'type:', 'srf2025', 'report of contributions']):
                    continue

                # Look for date/time line to identify where content starts
                if re.search(r'\w+day, \w+ \d+, \d{4}', line):
                    continue

                # First substantial line after headers is likely the title
                if not title_found and len(line) > 10 and not line.startswith('http'):
                    contribution['title'] = line
                    title_found = True
                    continue

                # After title, collect abstract until we hit "Footnotes" or similar
                if title_found and not abstract_start:
                    if line.lower().startswith(('footnotes', 'funding')):
                        break
                    elif len(line) > 20:  # Substantial content line
                        abstract_lines.append(line)
                        abstract_start = True
                    elif abstract_start and len(line) > 5:
                        abstract_lines.append(line)

            # Join abstract lines
            if abstract_lines:
                contribution['abstract'] = ' '.join(abstract_lines)

            # Extract footnotes if present
            footnotes_match = re.search(r'Footnotes(.*?)(?=Contribution|$)', text, re.DOTALL)
            if footnotes_match:
                contribution['footnotes'] = footnotes_match.group(1).strip()

        except Exception as e:
            self.logger.error(f"Error parsing page {page_num}: {e}")
            return None

        # Only return if we have essential information
        if contribution['contribution_code'] and contribution['title']:
            return contribution

        return None

    def get_session_name(self, session_code: str) -> str:
        """
        Get session name from session code.

        Args:
            session_code: Three-letter session code (e.g., 'MOA', 'TUB')

        Returns:
            Full session name
        """
        session_map = {
            'MOA': 'Monday Opening and Awards',
            'MOB': 'Monday Oral Session B',
            'MOC': 'Monday Oral Session C',
            'MOD': 'Monday Oral Session D',
            'MOE': 'Monday Oral Session E',
            'MOF': 'Monday Oral Session F',
            'MOG': 'Monday Oral Session G',
            'MOH': 'Monday Oral Session H',
            'MOI': 'Monday Oral Session I',
            'MOJ': 'Monday Oral Session J',
            'MOK': 'Monday Oral Session K',
            'MOL': 'Monday Oral Session L',
            'MOM': 'Monday Oral Session M',
            'MON': 'Monday Oral Session N',
            'MOO': 'Monday Oral Session O',
            'MOP': 'Monday Poster Session',
            'TUA': 'Tuesday Oral Session A',
            'TUB': 'Tuesday Oral Session B',
            'TUC': 'Tuesday Oral Session C',
            'TUD': 'Tuesday Oral Session D',
            'TUE': 'Tuesday Oral Session E',
            'TUF': 'Tuesday Oral Session F',
            'TUG': 'Tuesday Oral Session G',
            'TUH': 'Tuesday Oral Session H',
            'TUI': 'Tuesday Oral Session I',
            'TUJ': 'Tuesday Oral Session J',
            'TUK': 'Tuesday Oral Session K',
            'TUL': 'Tuesday Oral Session L',
            'TUM': 'Tuesday Oral Session M',
            'TUN': 'Tuesday Oral Session N',
            'TUO': 'Tuesday Oral Session O',
            'TUP': 'Tuesday Poster Session',
            'WEA': 'Wednesday Oral Session A',
            'WEB': 'Wednesday Oral Session B',
            'WEC': 'Wednesday Oral Session C',
            'WED': 'Wednesday Oral Session D',
            'WEE': 'Wednesday Oral Session E',
            'WEF': 'Wednesday Oral Session F',
            'WEG': 'Wednesday Oral Session G',
            'WEH': 'Wednesday Oral Session H',
            'WEI': 'Wednesday Oral Session I',
            'WEJ': 'Wednesday Oral Session J',
            'WEK': 'Wednesday Oral Session K',
            'WEL': 'Wednesday Oral Session L',
            'WEM': 'Wednesday Oral Session M',
            'WEN': 'Wednesday Oral Session N',
            'WEO': 'Wednesday Oral Session O',
            'WEP': 'Wednesday Poster Session',
            'THA': 'Thursday Oral Session A',
            'THB': 'Thursday Oral Session B',
            'THC': 'Thursday Oral Session C',
            'THD': 'Thursday Oral Session D',
            'THE': 'Thursday Oral Session E',
            'THF': 'Thursday Oral Session F',
            'THG': 'Thursday Oral Session G',
            'THH': 'Thursday Oral Session H',
            'THI': 'Thursday Oral Session I',
            'THJ': 'Thursday Oral Session J',
            'THK': 'Thursday Oral Session K',
            'THL': 'Thursday Oral Session L',
            'THM': 'Thursday Oral Session M',
            'THN': 'Thursday Oral Session N',
            'THO': 'Thursday Oral Session O',
            'THP': 'Thursday Poster Session',
            'FRA': 'Friday Oral Session A',
            'FRB': 'Friday Oral Session B',
            'FRC': 'Friday Oral Session C',
            'FRD': 'Friday Oral Session D',
            'FRE': 'Friday Oral Session E',
            'FRF': 'Friday Oral Session F',
            'FRG': 'Friday Oral Session G',
            'FRH': 'Friday Oral Session H',
            'FRI': 'Friday Oral Session I',
            'FRJ': 'Friday Oral Session J',
            'FRK': 'Friday Oral Session K',
            'FRL': 'Friday Oral Session L',
            'FRM': 'Friday Oral Session M',
            'FRN': 'Friday Oral Session N',
            'FRO': 'Friday Oral Session O',
            'FRP': 'Friday Poster Session'
        }

        return session_map.get(session_code, f"Session {session_code}")

    def save_data(self):
        """Save extracted data in multiple formats."""
        if not self.contributions:
            self.logger.warning("No contributions to save")
            return

        # Create sessions data structure
        sessions = {}
        for contrib in self.contributions:
            session_code = contrib['session_code']
            if session_code not in sessions:
                sessions[session_code] = {
                    'session_info': {
                        'id': session_code,
                        'name': contrib['session'],
                        'prefix': session_code
                    },
                    'papers': []
                }
            sessions[session_code]['papers'].append(contrib)

        # Convert to list
        all_sessions_data = list(sessions.values())

        # Save JSON
        json_file = self.output_dir / "SRF2025_Complete_Index.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'scrape_info': {
                    'extraction_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_contributions': len(self.contributions),
                    'sessions_processed': len(all_sessions_data),
                    'source': 'contributions.pdf'
                },
                'sessions': all_sessions_data
            }, f, ensure_ascii=False, indent=2)

        # Save CSV
        csv_file = self.output_dir / "SRF2025_All_Contributions.csv"
        df = pd.DataFrame(self.contributions)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # Save summary
        summary_file = self.output_dir / "SRF2025_Extraction_Report.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("SRF2025 Conference Contributions Extraction Report\n")
            f.write("=" * 60 + "\n")
            f.write(f"Extraction time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source PDF: {self.pdf_path}\n")
            f.write(f"Total contributions: {len(self.contributions)}\n")
            f.write(f"Sessions: {len(all_sessions_data)}\n\n")

            f.write("Session breakdown:\n")
            f.write("-" * 40 + "\n")
            for session_data in all_sessions_data:
                session = session_data['session_info']
                papers = session_data['papers']
                f.write(f"{session['prefix']}: {session['name']} ({len(papers)} contributions)\n")

        self.logger.info(f"Data saved to {self.output_dir}")

    def create_html_explorer(self):
        """Create HTML explorer similar to IBIC2025."""
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRF2025 Data Explorer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}

        .filter-bar {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .filter-bar input,
        .filter-bar select {{
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }}

        .contributions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }}

        .contribution-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }}

        .contribution-card:hover {{
            transform: translateY(-5px);
        }}

        .contribution-header {{
            border-bottom: 2px solid #eee;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }}

        .contribution-code {{
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 8px;
        }}

        .contribution-title {{
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }}

        .session-tag {{
            background: #e74c3c;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            display: inline-block;
        }}

        .contribution-meta {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}

        .contribution-abstract {{
            font-size: 14px;
            line-height: 1.5;
            color: #555;
            margin-bottom: 15px;
            max-height: 120px;
            overflow: hidden;
            position: relative;
        }}

        .contribution-abstract.expanded {{
            max-height: none;
        }}

        .expand-btn {{
            color: #3498db;
            cursor: pointer;
            font-size: 12px;
            text-decoration: underline;
        }}

        .loading {{
            text-align: center;
            padding: 50px;
            font-size: 18px;
            color: #7f8c8d;
        }}

        .stats-summary {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SRF2025 Data Explorer</h1>
            <p>Interactive Conference Contributions Database</p>
        </div>

        <div class="stats-summary">
            <div id="stats-display">Loading statistics...</div>
        </div>

        <div class="filter-bar">
            <input type="text" id="search-input" placeholder="Search contributions, titles, abstracts...">
            <select id="session-filter">
                <option value="">All Sessions</option>
            </select>
            <select id="type-filter">
                <option value="">All Types</option>
                <option value="Invited Oral Presentation">Invited Oral</option>
                <option value="Oral Presentation">Oral Presentation</option>
                <option value="Poster">Poster</option>
            </select>
            <button onclick="clearFilters()"
                style="padding: 10px 15px; background: #e74c3c; color: white; border: none; border-radius: 6px; cursor: pointer;">Clear
                Filters</button>
        </div>

        <div class="loading" id="loading">Loading SRF2025 conference data...</div>
        <div class="contributions-grid" id="contributions-grid" style="display: none;"></div>
    </div>

    <script>
        let allContributions = [];
        let filteredContributions = [];

        // Load data from JSON
        async function loadData() {{
            try {{
                const response = await fetch('SRF2025_Data/SRF2025_Complete_Index.json');
                const data = await response.json();

                // Extract contributions from sessions
                allContributions = [];
                data.sessions.forEach(sessionData => {{
                    sessionData.papers.forEach(contribution => {{
                        contribution.session_name = sessionData.session_info.name;
                        contribution.session_prefix = sessionData.session_info.prefix;
                        allContributions.push(contribution);
                    }});
                }});

                filteredContributions = [...allContributions];
                updateStats();
                populateFilters();
                renderContributions();

                document.getElementById('loading').style.display = 'none';
                document.getElementById('contributions-grid').style.display = 'grid';

            }} catch (error) {{
                document.getElementById('loading').innerHTML = 'Error loading data: ' + error.message;
            }}
        }}

        function updateStats() {{
            const totalContributions = allContributions.length;
            const filteredCount = filteredContributions.length;

            document.getElementById('stats-display').innerHTML = `
                <strong>Showing ${{filteredCount}} of ${{totalContributions}} contributions</strong>
            `;
        }}

        function populateFilters() {{
            const sessionFilter = document.getElementById('session-filter');
            const sessions = [...new Set(allContributions.map(c => c.session_name))].sort();

            sessions.forEach(session => {{
                const option = document.createElement('option');
                option.value = session;
                option.textContent = session;
                sessionFilter.appendChild(option);
            }});
        }}

        function renderContributions() {{
            const grid = document.getElementById('contributions-grid');
            grid.innerHTML = '';

            filteredContributions.forEach(contribution => {{
                const card = createContributionCard(contribution);
                grid.appendChild(card);
            }});
        }}

        function createContributionCard(contribution) {{
            const card = document.createElement('div');
            card.className = 'contribution-card';

            const abstractPreview = contribution.abstract ?
                (contribution.abstract.length > 200 ? contribution.abstract.substring(0, 200) + '...' : contribution.abstract) :
                'No abstract available';

            const typeText = contribution.type || 'Not specified';

            card.innerHTML = `
                <div class="contribution-header">
                    <div class="contribution-code">${{contribution.contribution_code}}</div>
                    <div class="contribution-title">${{contribution.title}}</div>
                    <span class="session-tag">${{contribution.session_prefix}}</span>
                </div>

                <div class="contribution-meta">
                    <div><strong>Type:</strong> ${{typeText}}</div>
                    <div><strong>Session:</strong> ${{contribution.session_name}}</div>
                    ${{contribution.date_time ? `<div><strong>Date/Time:</strong> ${{contribution.date_time}}</div>` : ''}}
                </div>

                <div class="contribution-abstract" id="abstract-${{contribution.contribution_id}}">
                    ${{abstractPreview}}
                    ${{contribution.abstract && contribution.abstract.length > 200 ?
                    `<div class="expand-btn" onclick="toggleAbstract('${{contribution.contribution_id}}')">Read more</div>` :
                    ''}}
                </div>
            `;

            return card;
        }}

        function toggleAbstract(contributionId) {{
            const abstractEl = document.getElementById(`abstract-${{contributionId}}`);
            const contribution = allContributions.find(c => c.contribution_id === contributionId);

            if (abstractEl.classList.contains('expanded')) {{
                abstractEl.classList.remove('expanded');
                abstractEl.innerHTML = contribution.abstract.substring(0, 200) + '...' +
                    '<div class="expand-btn" onclick="toggleAbstract(\'' + contributionId + '\')">Read more</div>';
            }} else {{
                abstractEl.classList.add('expanded');
                abstractEl.innerHTML = contribution.abstract +
                    '<div class="expand-btn" onclick="toggleAbstract(\'' + contributionId + '\')">Show less</div>';
            }}
        }}

        function applyFilters() {{
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const sessionFilter = document.getElementById('session-filter').value;
            const typeFilter = document.getElementById('type-filter').value;

            filteredContributions = allContributions.filter(contribution => {{
                const matchesSearch = !searchTerm ||
                    contribution.title.toLowerCase().includes(searchTerm) ||
                    contribution.contribution_code.toLowerCase().includes(searchTerm) ||
                    (contribution.abstract && contribution.abstract.toLowerCase().includes(searchTerm)) ||
                    (contribution.type && contribution.type.toLowerCase().includes(searchTerm));

                const matchesSession = !sessionFilter || contribution.session_name === sessionFilter;
                const matchesType = !typeFilter || contribution.type === typeFilter;

                return matchesSearch && matchesSession && matchesType;
            }});

            updateStats();
            renderContributions();
        }}

        function clearFilters() {{
            document.getElementById('search-input').value = '';
            document.getElementById('session-filter').value = '';
            document.getElementById('type-filter').value = '';
            filteredContributions = [...allContributions];
            updateStats();
            renderContributions();
        }}

        // Event listeners
        document.getElementById('search-input').addEventListener('input', applyFilters);
        document.getElementById('session-filter').addEventListener('change', applyFilters);
        document.getElementById('type-filter').addEventListener('change', applyFilters);

        // Load data when page loads
        loadData();
    </script>
</body>
</html>'''

        html_file = Path("srf2025_data_explorer.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"HTML explorer created: {html_file}")

    def run(self):
        """Run the complete extraction process."""
        self.logger.info("Starting SRF2025 PDF contributions extraction")

        start_time = time.time()

        # Extract contributions
        contributions = self.extract_contributions()

        if contributions:
            # Save data
            self.save_data()

            # Create HTML explorer
            self.create_html_explorer()

            elapsed_time = time.time() - start_time
            self.logger.info(f"\n🎉 Extraction completed! Time elapsed: {elapsed_time:.2f} seconds")
            self.logger.info(f"📊 Final statistics:")
            self.logger.info(f"  ✅ Contributions extracted: {len(contributions)}")
            self.logger.info(f"  💾 Data saved to: {self.output_dir}")
            self.logger.info(f"  🌐 HTML explorer: srf2025_data_explorer.html")
        else:
            self.logger.error("No contributions were extracted")


def main():
    """Main function to run the SRF2025 PDF extractor."""
    print("SRF2025 Conference PDF Contributions Extractor")
    print("=" * 60)
    print("Extracting contributions from SRF2025 conference PDF")
    print("Author: Ming Liu")
    print()

    extractor = SRF2025PDFExtractor()
    extractor.run()


if __name__ == "__main__":
    main()