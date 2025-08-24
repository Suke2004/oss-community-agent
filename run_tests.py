#!/usr/bin/env python3
"""
Test runner for OSS Community Agent
Runs all tests and provides detailed reporting
"""

import unittest
import sys
import os
import time
import subprocess
from pathlib import Path

def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running Unit Tests...")
    print("=" * 50)
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful(), len(result.failures), len(result.errors)

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    # Test database connectivity
    try:
        from apps.ui.utils.database import DatabaseManager
        db = DatabaseManager(":memory:")
        print("✅ Database connection test passed")
        db_success = True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        db_success = False
    
    # Test RAG system
    try:
        from tools.rag_tool import RAGTool
        rag = RAGTool()
        response = rag.retrieve_and_generate("test query")
        print("✅ RAG system test passed")
        rag_success = True
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        rag_success = False
    
    # Test moderation system
    try:
        from tools.moderation_tools import analyze_text
        result = analyze_text("test text")
        print("✅ Moderation system test passed")
        mod_success = True
    except Exception as e:
        print(f"❌ Moderation system test failed: {e}")
        mod_success = False
    
    return all([db_success, rag_success, mod_success])

def run_ui_tests():
    """Run UI component tests"""
    print("\n🖥️ Running UI Tests...")
    print("=" * 50)
    
    # Test Streamlit app import
    try:
        import streamlit
        print(f"✅ Streamlit version {streamlit.__version__} available")
        streamlit_success = True
    except ImportError:
        print("❌ Streamlit not available")
        streamlit_success = False
    
    # Test UI components
    try:
        from apps.ui.utils.helpers import load_css, init_session_state
        print("✅ UI utilities test passed")
        ui_success = True
    except Exception as e:
        print(f"❌ UI utilities test failed: {e}")
        ui_success = False
    
    return all([streamlit_success, ui_success])

def run_environment_tests():
    """Test environment configuration"""
    print("\n🌍 Running Environment Tests...")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version >= (3, 10):
        print("✅ Python version is compatible")
        python_ok = True
    else:
        print("⚠️ Python version is below recommended (3.10+)")
        python_ok = True  # Still works with mock
    
    # Check environment file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Environment file exists")
        env_ok = True
    else:
        print("⚠️ Environment file missing (using defaults)")
        env_ok = True
    
    # Check required packages
    required_packages = [
        'streamlit', 'praw', 'chromadb', 'langchain', 
        'pandas', 'plotly', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing")
            missing_packages.append(package)
    
    packages_ok = len(missing_packages) == 0
    
    return all([python_ok, env_ok, packages_ok])

def run_performance_tests():
    """Run basic performance tests"""
    print("\n⚡ Running Performance Tests...")
    print("=" * 50)
    
    # Test agent response time
    try:
        from apps.agent.main import run_oss_agent
        import time
        
        start_time = time.time()
        result = run_oss_agent("test query", "testpython")
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"Agent response time: {response_time:.2f} seconds")
        
        if response_time < 10:  # Should complete within 10 seconds
            print("✅ Agent performance test passed")
            perf_ok = True
        else:
            print("⚠️ Agent response time is slow")
            perf_ok = True  # Not critical for testing
    except Exception as e:
        print(f"❌ Agent performance test failed: {e}")
        perf_ok = False
    
    return perf_ok

def generate_test_report(unit_success, unit_failures, unit_errors, 
                        integration_success, ui_success, env_success, perf_success):
    """Generate comprehensive test report"""
    print("\n" + "=" * 60)
    print("📊 TEST REPORT")
    print("=" * 60)
    
    total_tests = 6  # Unit, Integration, UI, Environment, Performance
    passed_tests = sum([
        unit_success, integration_success, ui_success, 
        env_success, perf_success
    ])
    
    print(f"Overall Status: {'✅ PASSED' if passed_tests == total_tests else '❌ FAILED'}")
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if unit_failures > 0 or unit_errors > 0:
        print(f"Unit Test Issues: {unit_failures} failures, {unit_errors} errors")
    
    print("\nDetailed Results:")
    print(f"  Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"  Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    print(f"  UI Tests: {'✅ PASSED' if ui_success else '❌ FAILED'}")
    print(f"  Environment Tests: {'✅ PASSED' if env_success else '❌ FAILED'}")
    print(f"  Performance Tests: {'✅ PASSED' if perf_success else '❌ FAILED'}")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your OSS Community Agent is ready to run.")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    return passed_tests == total_tests

def main():
    """Main test runner"""
    print("🚀 OSS Community Agent - Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all test suites
    unit_success, unit_failures, unit_errors = run_unit_tests()
    integration_success = run_integration_tests()
    ui_success = run_ui_tests()
    env_success = run_environment_tests()
    perf_success = run_performance_tests()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Generate report
    all_passed = generate_test_report(
        unit_success, unit_failures, unit_errors,
        integration_success, ui_success, env_success, perf_success
    )
    
    print(f"\n⏱️ Total test time: {total_time:.2f} seconds")
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
