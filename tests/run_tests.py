#!/usr/bin/env python3
"""
Main test runner script for minecraft-launcher-lib
Run all tests with various configurations and generate coverage reports
"""

import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run all tests with different configurations"""

    # Basic test run
    print("Running basic tests...")
    result = pytest.main(["tests/", "-v", "--tb=short", "--color=yes"])

    if result != 0:
        print("❌ Basic tests failed!")
        return result

    print("✅ Basic tests passed!")

    # Run with coverage
    print("\nRunning tests with coverage...")
    coverage_result = pytest.main(
        [
            "tests/",
            "--cov=launcher_core",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml",
            "-v",
        ]
    )

    if coverage_result != 0:
        print("❌ Coverage tests failed!")
        return coverage_result

    print("✅ Coverage tests passed!")

    # Run specific test categories
    test_categories = [
        ("Core functionality", "tests/test_core.py"),
        ("Microsoft Account", "tests/test_microsoft_account.py"),
        ("Install & Command", "tests/test_install_command.py"),
        ("Mod Loaders", "tests/test_mod_loaders.py"),
        ("Utils & Runtime", "tests/test_utils_runtime.py"),
        ("Mojang & Config", "tests/test_mojang_config.py"),
    ]

    for category, test_file in test_categories:
        print(f"\nRunning {category} tests...")
        result = pytest.main([test_file, "-v"])
        if result != 0:
            print(f"❌ {category} tests failed!")
            return result
        print(f"✅ {category} tests passed!")

    print("\n🎉 All tests passed successfully!")
    return 0


def run_specific_tests():
    """Run specific test patterns"""

    # Test patterns
    patterns = [
        ("Async functions", "-k", "async"),
        ("Authentication", "-k", "auth"),
        ("Installation", "-k", "install"),
        ("Microsoft", "-k", "microsoft"),
        ("Mojang", "-k", "mojang"),
    ]

    for description, flag, pattern in patterns:
        print(f"\nRunning {description} tests...")
        result = pytest.main(["tests/", flag, pattern, "-v"])
        if result != 0:
            print(f"❌ {description} tests failed!")
        else:
            print(f"✅ {description} tests passed!")


def run_performance_tests():
    """Run performance-focused tests"""
    print("\nRunning performance tests...")
    result = pytest.main(["tests/", "--benchmark-only", "-v"])

    if result != 0:
        print("❌ Performance tests failed!")
    else:
        print("✅ Performance tests passed!")


def run_quick_tests():
    """Run quick tests only (exclude slow tests)"""
    print("\nRunning quick tests...")
    result = pytest.main(["tests/", "-m", "not slow", "-v"])

    if result != 0:
        print("❌ Quick tests failed!")
        return result

    print("✅ Quick tests passed!")
    return 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run minecraft-launcher-lib tests")
    parser.add_argument(
        "--mode",
        choices=["all", "quick", "coverage", "specific", "performance"],
        default="all",
        help="Test mode to run",
    )
    parser.add_argument(
        "--pattern", help="Test pattern to match (for specific mode)"
    )

    args = parser.parse_args()

    print(f"🚀 Starting tests in {args.mode} mode...")
    print("=" * 50)

    try:
        if args.mode == "all":
            return run_tests()
        elif args.mode == "quick":
            return run_quick_tests()
        elif args.mode == "coverage":
            return pytest.main(
                [
                    "tests/",
                    "--cov=launcher_core",
                    "--cov-report=html:htmlcov",
                    "--cov-report=term-missing",
                    "--cov-report=xml:coverage.xml",
                    "-v",
                ]
            )
        elif args.mode == "specific":
            run_specific_tests()
            return 0
        elif args.mode == "performance":
            run_performance_tests()
            return 0
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
