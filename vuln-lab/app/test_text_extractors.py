#!/usr/bin/env python3
"""
Test script for the text extraction functionality.
Tests different file formats and extraction methods.
"""

import sys
import os
from text_extractors import extract_text_from_file, get_text_extractor

def test_extractor_availability():
    """Test which extractors are available."""
    print("=== Testing Extractor Availability ===")
    extractor = get_text_extractor()
    print(f"Available extractors: {extractor.available_extractors}")
    print(f"Supported extensions: {extractor.get_supported_extensions()}")
    print()

def test_txt_extraction():
    """Test TXT file extraction."""
    print("=== Testing TXT Extraction ===")
    
    # Create a sample TXT file
    test_content = """John Doe
Senior Software Engineer

Experience:
- 5 years of Python development
- Flask and Django frameworks
- Machine learning with scikit-learn

Education:
- BS Computer Science, University of Tech

Skills: Python, JavaScript, SQL, Git"""
    
    test_file = "test_resume.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        extracted = extract_text_from_file(file_path=test_file)
        print(f"Successfully extracted {len(extracted)} characters")
        print(f"First 100 chars: {extracted[:100]}...")
        
        # Test with file content
        with open(test_file, 'rb') as f:
            content = f.read()
        extracted_from_bytes = extract_text_from_file(file_content=content, filename=test_file)
        print(f"Extraction from bytes matches file: {extracted == extracted_from_bytes}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
    print()

def test_unsupported_format():
    """Test extraction of unsupported format."""
    print("=== Testing Unsupported Format ===")
    
    # Create a sample binary file
    test_file = "test.bin"
    with open(test_file, 'wb') as f:
        f.write(b'\x00\x01\x02\x03\x04\x05')
    
    try:
        extracted = extract_text_from_file(file_path=test_file)
        print(f"Extracted: {extracted}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
    print()

def main():
    """Run all tests."""
    print("Text Extractor Test Suite")
    print("=" * 40)
    
    test_extractor_availability()
    test_txt_extraction()
    test_unsupported_format()
    
    print("Test completed!")

if __name__ == "__main__":
    main()
