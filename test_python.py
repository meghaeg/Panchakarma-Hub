"""Simple script to test Python and internet connectivity"""

import sys
import urllib.request
import socket

def test_internet_connection():
    """Test if we can reach the internet"""
    print("🌐 Testing internet connection...")
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("✅ Internet connection is working")
        return True
    except OSError:
        print("❌ No internet connection")
        return False

def test_http_connection():
    """Test if we can make HTTP requests"""
    print("\n🔗 Testing HTTP connection...")
    try:
        response = urllib.request.urlopen('http://httpbin.org/ip', timeout=5)
        print(f"✅ HTTP connection successful. Response: {response.read().decode('utf-8')}")
        return True
    except Exception as e:
        print(f"❌ HTTP connection failed: {e}")
        return False

def test_packages():
    """Test if required packages are installed"""
    print("\n📦 Testing required packages...")
    packages = ['pymongo', 'flask', 'bcrypt', 'python-dotenv', 'pytz']
    missing = []
    
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg} is installed")
        except ImportError:
            print(f"❌ {pkg} is NOT installed")
            missing.append(pkg)
    
    if missing:
        print(f"\n⚠️  Missing packages. Install with: pip install {' '.join(missing)}")
    else:
        print("\n✅ All required packages are installed")
    
    return len(missing) == 0

def main():
    print("🔍 Running system tests...")
    print(f"Python version: {sys.version.split()[0]}")
    
    internet_ok = test_internet_connection()
    http_ok = test_http_connection() if internet_ok else False
    packages_ok = test_packages()
    
    print("\n📋 Test Summary:")
    print(f"- Internet Connection: {'✅' if internet_ok else '❌'}")
    print(f"- HTTP Connection: {'✅' if http_ok else '❌'}")
    print(f"- Required Packages: {'✅' if packages_ok else '❌'}")
    
    if not (internet_ok and http_ok and packages_ok):
        print("\n❌ Some tests failed. Please check the output above for details.")
        return 1
    
    print("\n✅ All tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
