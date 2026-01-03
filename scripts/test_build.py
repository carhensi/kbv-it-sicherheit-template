#!/usr/bin/env python3
"""
Minimal unit tests for build.py and generate_changelog.py
Run with: python3 test_build.py (no pytest required)
"""

import sys
from datetime import datetime
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import functions to test
try:
    from build import generate_version_from_date, translate_month
    from generate_changelog import format_date_german, escape_latex
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_translate_month():
    """Test German month translation"""
    assert translate_month("January 2025") == "Januar 2025"
    assert translate_month("December 2024") == "Dezember 2024"
    assert translate_month("May 2025") == "Mai 2025"
    print("✅ test_translate_month passed")


def test_generate_version_from_date():
    """Test version generation from date"""
    version, doc_date, valid, review = generate_version_from_date("2025-09-01")
    
    assert version == "2025.09.01"
    assert "September" in doc_date
    assert "2028" in valid  # 3 years validity
    assert "2027" in review  # 2 years review
    print("✅ test_generate_version_from_date passed")


def test_generate_version_invalid_date():
    """Test error handling for invalid date"""
    try:
        generate_version_from_date("invalid-date")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    print("✅ test_generate_version_invalid_date passed")


def test_format_date_german():
    """Test German date formatting"""
    assert format_date_german("2025-09-01") == "01.09.2025"
    assert format_date_german("2024-12-31") == "31.12.2024"
    print("✅ test_format_date_german passed")


def test_escape_latex():
    """Test LaTeX special character escaping"""
    assert escape_latex("Test & Co.") == r"Test \& Co."
    assert escape_latex("50% done") == r"50\% done"
    assert escape_latex("Price: $100") == r"Price: \$100"
    print("✅ test_escape_latex passed")


def main():
    """Run all tests"""
    print("🧪 Running unit tests...")
    
    tests = [
        test_translate_month,
        test_generate_version_from_date,
        test_generate_version_invalid_date,
        test_format_date_german,
        test_escape_latex,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    if failed == 0:
        print(f"✅ All {len(tests)} tests passed!")
        return 0
    else:
        print(f"❌ {failed}/{len(tests)} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
