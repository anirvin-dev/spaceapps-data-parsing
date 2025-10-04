#!/usr/bin/env python3
"""
Simple test script to verify the NASA Bioscience Summarizer pipeline structure.
This script tests the basic functionality without requiring all dependencies.
"""

import sys
import os
from pathlib import Path

def test_basic_imports():
    """Test basic Python imports that should be available."""
    try:
        import json
        import re
        import time
        import logging
        from pathlib import Path
        from typing import Dict, Any, List
        print("✅ Basic imports successful")
        return True
    except ImportError as e:
        print(f"❌ Basic import failed: {e}")
        return False

def test_file_structure():
    """Test that required files exist."""
    required_files = [
        "nasa_pipeline_all_in_one.py",
        "dashboard.py", 
        "requirements.txt",
        "README.md",
        "data/nasa_papers.csv"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_csv_structure():
    """Test CSV file structure."""
    csv_path = Path("data/nasa_papers.csv")
    if not csv_path.exists():
        print("❌ CSV file not found")
        return False
    
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            print("❌ CSV file too short")
            return False
        
        # Check header
        header = lines[0].strip()
        if "title" in header.lower() and "link" in header.lower():
            print("✅ CSV header looks correct")
        else:
            print("❌ CSV header missing required columns")
            return False
        
        print(f"✅ CSV file has {len(lines)-1} data rows")
        return True
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def test_pipeline_syntax():
    """Test that the main pipeline script has valid syntax."""
    try:
        with open("nasa_pipeline_all_in_one.py", 'r') as f:
            code = f.read()
        
        # Basic syntax check
        compile(code, "nasa_pipeline_all_in_one.py", "exec")
        print("✅ Pipeline script syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Pipeline script syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking pipeline syntax: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing NASA Bioscience Summarizer Pipeline")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("File Structure", test_file_structure),
        ("CSV Structure", test_csv_structure),
        ("Pipeline Syntax", test_pipeline_syntax)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The pipeline structure looks good.")
        print("\n📋 Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test with sample: python nasa_pipeline_all_in_one.py --mode full --sample 3")
        print("3. Run dashboard: python nasa_pipeline_all_in_one.py --mode serve")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
