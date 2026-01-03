#!/usr/bin/env python3
"""
Build script for IT-Sicherheitsdokumentation
- Updates version information
- Generates changelog from CHANGELOG.md
- Builds PDF with latexmk
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

# Add scripts directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import safe_file_read, safe_file_write, run_script

# Constants
GERMAN_MONTHS = {
    'January': 'Januar', 'February': 'Februar', 'March': 'März',
    'April': 'April', 'May': 'Mai', 'June': 'Juni',
    'July': 'Juli', 'August': 'August', 'September': 'September',
    'October': 'Oktober', 'November': 'November', 'December': 'Dezember'
}

VERSION_PATTERNS = [
    (r'\\newcommand\{\\DocumentVersion\}\{[^}]+\}', r'\\newcommand{{\\DocumentVersion}}{{{version}}}'),
    (r'\\newcommand\{\\DocumentDate\}\{[^}]+\}', r'\\newcommand{{\\DocumentDate}}{{{document_date}}}'),
    (r'\\newcommand\{\\ValidUntil\}\{[^}]+\}', r'\\newcommand{{\\ValidUntil}}{{{valid_until}}}'),
    (r'\\newcommand\{\\NextReview\}\{[^}]+\}', r'\\newcommand{{\\NextReview}}{{{next_review}}}'),
]


def get_metadata_path(tex_path: Path) -> Path:
    """Get metadata.tex path"""
    return tex_path.parent / 'config' / 'metadata.tex'


def translate_month(date_str: str) -> str:
    """Translate English month names to German"""
    for en, de in GERMAN_MONTHS.items():
        date_str = date_str.replace(en, de)
    return date_str


def update_version_in_metadata(
    tex_path: Path,
    version: str,
    document_date: str,
    valid_until: str,
    next_review: str
) -> None:
    """Update version information in metadata.tex"""
    metadata_path = get_metadata_path(tex_path)
    content = safe_file_read(metadata_path)
    
    # Update version definitions using template patterns
    replacements = {
        'version': version,
        'document_date': document_date,
        'valid_until': valid_until,
        'next_review': next_review
    }
    
    for pattern, template in VERSION_PATTERNS:
        replacement = template.format(**replacements)
        content = re.sub(pattern, replacement, content)
    
    safe_file_write(metadata_path, content)
    print(f"✅ Updated version to {version} in {metadata_path}")


def generate_version_from_date(date_str: str | None = None) -> Tuple[str, str, str, str]:
    """Generate version and related dates from input date"""
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Invalid date format '{date_str}'. Use YYYY-MM-DD: {e}")
    else:
        date_obj = datetime.now()
    
    version = date_obj.strftime('%Y.%m.%d')
    document_date = translate_month(date_obj.strftime('%d. %B %Y'))
    
    # Calculate validity (3 years from release)
    valid_until_date = date_obj + timedelta(days=3*365)
    valid_until = valid_until_date.strftime('%d.%m.%Y')
    
    # Calculate next review (2 years from release)
    next_review_date = date_obj + timedelta(days=2*365)
    next_review = translate_month(next_review_date.strftime('%B %Y'))
    
    return version, document_date, valid_until, next_review


def get_current_version(tex_path: Path) -> str:
    """Extract current version from metadata.tex"""
    metadata_path = get_metadata_path(tex_path)
    content = safe_file_read(metadata_path)
    
    match = re.search(r'\\newcommand\{\\DocumentVersion\}\{([^}]+)\}', content)
    if match:
        return match.group(1)
    raise ValueError("DocumentVersion not found in metadata.tex")


def build_pdf(tex_dir: Path) -> bool:
    """Build PDF using latexmk"""
    try:
        result = subprocess.run(
            ['latexmk', '-lualatex', '-interaction=nonstopmode', '-f', 'main.tex'],
            cwd=tex_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            pdf_path = tex_dir / 'main.pdf'
            if pdf_path.exists():
                print(f"✅ PDF built successfully: {pdf_path}")
                return True
            else:
                print("❌ Build succeeded but PDF not found")
                return False
        else:
            print("❌ LaTeX build failed:")
            print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
            return False
            
    except FileNotFoundError:
        print("❌ latexmk not found. Please install LaTeX distribution.")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Build timeout (>5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description='Build IT-Sicherheitsdokumentation')
    parser.add_argument('--version-date', help='Version date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--no-build', action='store_true', help='Only update version, do not build PDF')
    parser.add_argument('--print-version', action='store_true', help='Print current version and exit')
    parser.add_argument('--changelog-only', action='store_true', help='Only regenerate changelog')
    
    args = parser.parse_args()
    
    # Paths
    project_root = Path(__file__).parent.parent
    tex_dir = project_root / 'tex'
    main_tex = tex_dir / 'main.tex'
    
    # Print version and exit
    if args.print_version:
        try:
            version = get_current_version(main_tex)
            print(version)
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Only regenerate changelog
    if args.changelog_only:
        try:
            run_script(project_root / 'scripts' / 'generate_changelog.py')
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print(f"❌ Changelog generation failed: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Generate version information
    try:
        version, document_date, valid_until, next_review = generate_version_from_date(args.version_date)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"📝 Version: {version}")
    print(f"📅 Document Date: {document_date}")
    print(f"⏰ Valid Until: {valid_until}")
    print(f"🔄 Next Review: {next_review}")
    
    # Update metadata.tex
    if not main_tex.exists():
        print(f"❌ Error: {main_tex} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        update_version_in_metadata(main_tex, version, document_date, valid_until, next_review)
    except (FileNotFoundError, IOError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate changelog
    print("📝 Generating changelog...")
    try:
        run_script(project_root / 'scripts' / 'generate_changelog.py')
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Changelog generation failed: {e}", file=sys.stderr)
    
    # Build PDF
    if not args.no_build:
        print("🔨 Building PDF...")
        if not build_pdf(tex_dir):
            sys.exit(1)


if __name__ == '__main__':
    main()
