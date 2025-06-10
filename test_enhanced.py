#!/usr/bin/env python3
"""
Test script for enhanced podcast generator features
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from podcast_mcp_server_enhanced import (
        extract_text_from_file,
        check_system_status,
        SUPPORTED_FORMATS
    )
    print("✅ Enhanced server module loaded successfully!")
except ImportError as e:
    print(f"❌ Failed to import enhanced server: {e}")
    sys.exit(1)

def test_system_status():
    """Test system status check"""
    print("\n🔍 Checking system status...")
    status = check_system_status()
    
    print("\nSystem Status:")
    for key, value in status.items():
        emoji = "✅" if value else "❌"
        print(f"  {emoji} {key}: {value}")
    
    return status

def test_file_extraction():
    """Test file extraction capabilities"""
    print("\n📄 Testing file extraction...")
    
    # Create a test text file
    test_file = "test_document.txt"
    with open(test_file, 'w') as f:
        f.write("""# Test Document

This is a test document for the podcast generator.
It contains some sample text that can be converted into a podcast.

Key points:
1. File extraction works
2. Text processing is functional
3. Ready for podcast generation
""")
    
    # Test extraction
    try:
        content = extract_text_from_file(test_file)
        print(f"✅ Successfully extracted {len(content)} characters from {test_file}")
        print(f"First 100 chars: {content[:100]}...")
        
        # Clean up
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def test_supported_formats():
    """Display supported file formats"""
    print("\n📁 Supported file formats:")
    for ext, desc in SUPPORTED_FORMATS.items():
        print(f"  • {ext}: {desc}")

async def test_basic_import():
    """Test that basic FastMCP functionality works"""
    print("\n🧪 Testing FastMCP import...")
    try:
        from fastmcp import FastMCP
        print("✅ FastMCP imported successfully")
        return True
    except ImportError as e:
        print(f"❌ FastMCP import failed: {e}")
        print("   Install with: pip install fastmcp")
        return False

def main():
    """Run all tests"""
    print("🎙️ Podcast Generator Enhanced - System Test\n")
    
    # Run tests
    all_passed = True
    
    # Test system status
    status = test_system_status()
    if not status.get("ready"):
        print("\n⚠️  System not fully ready. Check ElevenLabs API key.")
        all_passed = False
    
    # Test file formats
    test_supported_formats()
    
    # Test file extraction
    if not test_file_extraction():
        all_passed = False
    
    # Test FastMCP
    if not asyncio.run(test_basic_import()):
        all_passed = False
    
    # Summary
    print("\n" + "="*50)
    if all_passed and status.get("ready"):
        print("✅ All tests passed! System is ready for podcast generation.")
        print("\nNext steps:")
        print("1. Set ELEVENLABS_API_KEY environment variable")
        print("2. Run: python podcast_mcp_server_enhanced.py")
        print("3. Use with Claude Desktop or MCP client")
    else:
        print("⚠️  Some tests failed. Please check the requirements:")
        print("1. Install all dependencies: pip install -r requirements.txt")
        print("2. Set ELEVENLABS_API_KEY environment variable")
        print("3. Install ffmpeg for audio processing")

if __name__ == "__main__":
    main()