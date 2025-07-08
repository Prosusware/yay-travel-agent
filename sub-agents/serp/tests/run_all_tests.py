#!/usr/bin/env python3
"""
Test runner for all SerpApi MCP tools.
"""
import asyncio
import subprocess
import sys
import os

async def run_test(test_name, test_file):
    """Run a single test and return result"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_name} test...")
    print(f"{'='*60}")
    
    try:
        # Run the test using uv
        result = subprocess.run(
            ["uv", "run", "python", test_file],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        success = result.returncode == 0 and "TEST PASSED" in result.stdout
        return success
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name} test timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running {test_name} test: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting SerpApi MCP Tools Test Suite")
    print("=" * 60)
    
    tests = [
        ("Flights", "tests/test_flights.py"),
        ("Hotels", "tests/test_hotels.py"),
        ("Maps", "tests/test_maps.py"),
        ("Amazon", "tests/test_amazon.py")
    ]
    
    results = {}
    
    for test_name, test_file in tests:
        success = await run_test(test_name, test_file)
        results[test_name] = success
    
    # Print summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(tests)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<10} {status}")
        if success:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The MCP server tools are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)