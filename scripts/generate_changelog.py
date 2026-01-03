#!/usr/bin/env python3
"""
Generate LaTeX changelog from CHANGELOG.md
Parses Keep a Changelog format and creates LaTeX table
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, TypedDict

# Add scripts directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import safe_file_read, safe_file_write, ensure_dir

# Constants
LATEX_ESCAPES = {
    '&': r'\&', '%': r'\%', '_': r'\_', '#': r'\#', '$': r'\$',
    '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'
}

LATEX_HEADER = [
    r'\section{Anhang – Changelog und Versionsverlauf}',
    r'\label{sec:anhang-changelog}',
    '',
    r'\subsection*{Versionshistorie}',
    '',
    r'\small',
    r'\begin{longtable}{p{3cm} >{\raggedright\arraybackslash}p{10cm}}',
    r'  \toprule',
    r'  \textbf{Version} & \textbf{Änderungen} \\',
    r'  \midrule',
    r'  \endhead',
    '',
]

LATEX_FOOTER = [
    r'  \bottomrule',
    r'\end{longtable}',
    '',
]


class ChangelogEntry(TypedDict):
    """Type definition for changelog entry"""
    version: str
    date: str
    changes: Dict[str, List[str]]


def parse_changelog(changelog_path: Path) -> List[ChangelogEntry]:
    """Parse CHANGELOG.md and extract version entries"""
    content = safe_file_read(changelog_path)
    
    # Find all version entries
    version_pattern = r'## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})'
    versions = re.findall(version_pattern, content)
    
    if not versions:
        return []
    
    entries: List[ChangelogEntry] = []
    
    # Split content by version headers
    sections = re.split(r'## \[[^\]]+\] - \d{4}-\d{2}-\d{2}', content)[1:]
    
    for i, (version, date) in enumerate(versions):
        if i < len(sections):
            section_content = sections[i].strip()
            
            # Extract changes by category
            changes: Dict[str, List[str]] = {}
            current_category: str | None = None
            
            for line in section_content.split('\n'):
                line = line.strip()
                if line.startswith('### '):
                    current_category = line[4:].strip()
                    changes[current_category] = []
                elif line.startswith('- ') and current_category:
                    changes[current_category].append(line[2:].strip())
            
            entries.append({
                'version': version,
                'date': date,
                'changes': changes
            })
    
    return entries


def format_date_german(date_str: str) -> str:
    """Convert YYYY-MM-DD to German format (DD.MM.YYYY)"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except ValueError:
        return date_str


def escape_latex(text: str) -> str:
    """Escape LaTeX special characters"""
    for char, escaped in LATEX_ESCAPES.items():
        text = text.replace(char, escaped)
    return text


def generate_latex_changelog(entries: List[ChangelogEntry], max_entries: int = 10) -> str:
    """Generate LaTeX table from changelog entries"""
    latex_lines = LATEX_HEADER.copy()
    
    # Add actual entries (newest first)
    for entry in entries[:max_entries]:
        date_german = format_date_german(entry['date'])
        version = entry['version']
        
        # Create summary
        total_changes = sum(len(items) for items in entry['changes'].values())
        
        if version == "2025.09.01":
            changes_text = (
                f"Initial Release der vollständigen IT-Sicherheitsdokumentation "
                f"nach §390 SGB V mit {total_changes} implementierten "
                f"Sicherheitsmaßnahmen und Richtlinien"
            )
        else:
            categories = list(entry['changes'].keys())
            if categories:
                main_category = categories[0]
                changes_text = f"{main_category}: {total_changes} Änderungen"
            else:
                changes_text = "Keine Änderungen dokumentiert"
        
        # Escape LaTeX special characters
        changes_text = escape_latex(changes_text)
        
        latex_lines.append(f'  {version} & {changes_text} \\\\')
        latex_lines.append('')
    
    # Add empty rows for future entries
    for _ in range(5):
        latex_lines.append(r'  & \\[1cm]')
        latex_lines.append('')
    
    latex_lines.extend(LATEX_FOOTER)
    return '\n'.join(latex_lines)


def main() -> None:
    # Paths - robust path detection
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Always use project root for consistency
    changelog_path = project_root / 'CHANGELOG.md'
    output_path = project_root / 'tex' / 'includes' / '993_anhang-changelog.tex'
    
    # Parse changelog
    try:
        entries = parse_changelog(changelog_path)
    except (FileNotFoundError, IOError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not entries:
        print("⚠️  Warning: No changelog entries found", file=sys.stderr)
        # Create empty changelog
        entries = []
    
    # Generate LaTeX
    latex_content = generate_latex_changelog(entries)
    
    # Write output
    ensure_dir(output_path)
    safe_file_write(output_path, latex_content)
    
    print(f"✅ Generated changelog: {output_path}")
    print(f"📊 Found {len(entries)} version entries")


if __name__ == '__main__':
    main()
