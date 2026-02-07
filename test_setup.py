#!/usr/bin/env python3
"""
Test script to verify the research pipeline setup
"""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    try:
        import flask
        import requests
        import PyPDF2
        from werkzeug.utils import secure_filename
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_api_key():
    """Test that Groq API key is set"""
    print("\nTesting API key configuration...")
    api_key = os.environ.get('GROQ_API_KEY', '')
    if api_key:
        print(f"✅ GROQ_API_KEY is set (length: {len(api_key)})")
        return True
    else:
        print("❌ GROQ_API_KEY not set")
        print("Set it with: export GROQ_API_KEY='your-key-here'")
        print("Or create a .env file")
        return False

def test_groq_connection():
    """Test connection to Groq API"""
    print("\nTesting Groq API connection...")
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        print("⚠️  Skipping (no API key)")
        return False
    
    try:
        import requests
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Groq API connection successful")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        '.env.example'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Research Pipeline Setup Test")
    print("=" * 60)
    
    results = []
    results.append(("File Structure", test_file_structure()))
    results.append(("Imports", test_imports()))
    results.append(("API Key", test_api_key()))
    results.append(("Groq Connection", test_groq_connection()))
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(result[1] for result in results[:-1])  # Exclude connection test
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Setup complete! Ready to run the pipeline.")
        print("\nStart the server with:")
        print("  python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    print("=" * 60)

if __name__ == '__main__':
    main()
