"""
Quick start script for the ISRI Backend API
Run this to verify the setup is correct
"""
import sys
import os

def check_imports():
    """Check if all required modules can be imported"""
    print("🔍 Checking imports...")
    
    try:
        from models.input_models import ComprehensiveInput
        print("✓ Models imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import models: {e}")
        return False
    
    try:
        from services import (
            calculate_barrier_scores,
            calculate_cost_factor_scores,
            calculate_kpi_scores,
            calculate_impact_values,
            get_top_n_barriers
        )
        print("✓ Services imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import services: {e}")
        return False
    
    try:
        from utils.pdf_utils import create_pdf_from_markdown
        print("✓ Utilities imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import utilities: {e}")
        return False
    
    try:
        from config.settings import MISTRAL_API_KEY, MONGODB_URI
        print("✓ Config imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    return True


def check_dependencies():
    """Check if all required packages are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'httpx',
        'pymongo',
        'weasyprint',
        'markdown2'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_environment():
    """Check environment variables"""
    print("\n🔐 Checking environment...")
    
    from config.settings import OPENROUTER_API_KEY, MONGODB_URI
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        print("⚠️  OPENROUTER_API_KEY not configured properly")
        print("   Set it in .env file or environment variables")
        print("   Get it from: https://openrouter.ai/keys")
    else:
        print("✓ OPENROUTER_API_KEY configured")
    
    print(f"✓ MONGODB_URI: {MONGODB_URI}")
    
    return True


def test_mongodb():
    """Test MongoDB connection"""
    print("\n🗄️  Testing MongoDB connection...")
    
    try:
        from services.database_service import DatabaseService
        db = DatabaseService()
        # Try a simple operation
        db.db.list_collection_names()
        db.close()
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("   Make sure MongoDB is running")
        print("   Run: mongosh (to check)")
        return False


def main():
    """Run all checks"""
    print("=" * 50)
    print("ISRI Backend Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Import Check", check_imports),
        ("Dependencies Check", check_dependencies),
        ("Environment Check", check_environment),
        ("MongoDB Check", test_mongodb)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to start the server.")
        print("\nRun: python app.py")
        print("Or: uvicorn app:app --reload")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
