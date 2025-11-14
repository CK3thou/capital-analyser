"""
Setup Verification Script
Run this to verify your configuration before running the analyzer
"""

import sys
import os


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro}")
        print("  Requires Python 3.7 or higher")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    missing = []
    
    # Check requests
    try:
        import requests
        print(f"  ✓ requests ({requests.__version__})")
    except ImportError:
        print("  ✗ requests - NOT INSTALLED")
        missing.append("requests")
    
    # Check dateutil
    try:
        import dateutil
        print(f"  ✓ python-dateutil")
    except ImportError:
        print("  ✗ python-dateutil - NOT INSTALLED")
        missing.append("python-dateutil")
    
    if missing:
        print("\n  Install missing packages with:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def check_config_file():
    """Check if config.py exists and is configured"""
    print("\nChecking configuration file...", end=" ")
    
    if not os.path.exists("config.py"):
        print("✗ config.py NOT FOUND")
        print("\n  Create it from template:")
        print("  PowerShell: Copy-Item config_template.py config.py")
        print("  Then edit config.py with your credentials")
        return False
    
    print("✓ config.py exists")
    
    # Try to import and check values
    try:
        import config
        
        print("\nChecking configuration values...")
        
        # Check API_KEY
        if hasattr(config, 'API_KEY'):
            if config.API_KEY and config.API_KEY != "your-api-key-here":
                print("  ✓ API_KEY is set")
            else:
                print("  ✗ API_KEY not configured (still has placeholder value)")
                return False
        else:
            print("  ✗ API_KEY not found in config.py")
            return False
        
        # Check USERNAME
        if hasattr(config, 'USERNAME'):
            if config.USERNAME and config.USERNAME != "your-email-or-username":
                print("  ✓ USERNAME is set")
            else:
                print("  ✗ USERNAME not configured (still has placeholder value)")
                return False
        else:
            print("  ✗ USERNAME not found in config.py")
            return False
        
        # Check PASSWORD
        if hasattr(config, 'PASSWORD'):
            if config.PASSWORD and config.PASSWORD != "your-password":
                print("  ✓ PASSWORD is set")
            else:
                print("  ✗ PASSWORD not configured (still has placeholder value)")
                return False
        else:
            print("  ✗ PASSWORD not found in config.py")
            return False
        
        # Check USE_DEMO
        if hasattr(config, 'USE_DEMO'):
            env = "DEMO" if config.USE_DEMO else "LIVE"
            print(f"  ✓ Environment: {env}")
        else:
            print("  ⚠ USE_DEMO not found (will default to DEMO)")
        
        # Check CATEGORIES
        if hasattr(config, 'CATEGORIES'):
            print(f"  ✓ Categories: {', '.join(config.CATEGORIES)}")
        else:
            print("  ⚠ CATEGORIES not found (will use defaults)")
        
        return True
        
    except Exception as e:
        print(f"\n  ✗ Error loading config.py: {str(e)}")
        return False


def check_api_connection():
    """Test API connection (optional - requires config)"""
    print("\nTesting API connection...")
    
    try:
        from capital_analyzer import CapitalAPI
        import config
        
        print("  Creating session...", end=" ")
        api = CapitalAPI(
            api_key=config.API_KEY,
            identifier=config.USERNAME,
            password=config.PASSWORD,
            demo=getattr(config, 'USE_DEMO', True)
        )
        
        if api.create_session():
            print("✓ SUCCESS!")
            print(f"  Session tokens received")
            print(f"  CST: {api.cst[:20]}...")
            print(f"  Security Token: {api.security_token[:20]}...")
            return True
        else:
            print("✗ FAILED")
            print("  Check your API_KEY, USERNAME, and PASSWORD")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False


def main():
    """Run all verification checks"""
    print("="*60)
    print("Capital.com Market Analyzer - Setup Verification")
    print("="*60)
    
    checks = []
    
    # Run checks
    checks.append(("Python Version", check_python_version()))
    checks.append(("Dependencies", check_dependencies()))
    checks.append(("Configuration", check_config_file()))
    
    # Only test API if previous checks passed
    if all(result for _, result in checks):
        print("\n" + "="*60)
        response = input("All checks passed! Test API connection? (y/n): ")
        if response.lower() in ['y', 'yes']:
            checks.append(("API Connection", check_api_connection()))
    
    # Print summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name:20s}: {status}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ All checks passed! You're ready to run the analyzer.")
        print("\nNext step:")
        print("  python run_analyzer.py")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("  - QUICKSTART.md")
        print("  - README_ANALYZER.md")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
