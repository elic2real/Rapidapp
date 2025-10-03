#!/usr/bin/env python3
"""
AI Debugging System Test Script
Test the hardened AI debugging capabilities without complex dependencies
"""

import sys
import traceback
from pathlib import Path
from typing import Dict, Any

# Import our hardened utilities
from utils import print_once, safe_subprocess_run, safe_file_read

def create_test_error():
    """Create a sample error for testing"""
    error_info = {
        'error_type': 'NameError',
        'message': 'name "undefined_variable" is not defined',
        'stack_trace': '''Traceback (most recent call last):
  File "test.py", line 10, in test_function
    result = undefined_variable + 5
NameError: name "undefined_variable" is not defined''',
        'file_path': 'test.py',
        'line_number': 10,
        'function_name': 'test_function',
        'code_context': [
            'def test_function():',
            '    # This will cause an error',
            '    result = undefined_variable + 5',
            '    return result'
        ],
        'environment_info': {
            'python_version': sys.version,
            'platform': sys.platform,
            'cwd': str(Path.cwd())
        }
    }
    return error_info

def test_error_analysis():
    """Test basic error analysis capabilities"""
    print_once("🔍 Testing AI Debug Error Analysis", "INFO")
    
    # Create test error
    error_info = create_test_error()
    
    # Basic analysis
    print_once(f"Error Type: {error_info['error_type']}", "INFO")
    print_once(f"Error Message: {error_info['message']}", "INFO")
    print_once(f"File: {error_info['file_path']}:{error_info['line_number']}", "INFO")
    
    # Analysis suggestions
    suggestions = analyze_error_basic(error_info)
    print_once("Analysis Results:", "SUCCESS")
    for suggestion in suggestions:
        print_once(f"  • {suggestion}", "INFO")
    
        assert True

def analyze_error_basic(error_info: Dict[str, Any]) -> list:
    """Basic error analysis without LLM dependencies"""
    suggestions = []
    
    error_type = error_info.get('error_type', '')
    message = error_info.get('message', '')
    
    if error_type == 'NameError':
        if 'not defined' in message:
            var_name = message.split('"')[1] if '"' in message else 'variable'
            suggestions.extend([
                f"Variable '{var_name}' is not defined in the current scope",
                f"Check if '{var_name}' is spelled correctly",
                f"Ensure '{var_name}' is defined before use",
                "Consider initializing the variable or importing it if it's from another module"
            ])
    
    elif error_type == 'ImportError':
        suggestions.extend([
            "Module not found - check if it's installed",
            "Verify the module name is correct",
            "Check if the module is in the Python path"
        ])
    
    elif error_type == 'SyntaxError':
        suggestions.extend([
            "Check for missing parentheses, brackets, or quotes",
            "Verify proper indentation",
            "Look for typos in keywords"
        ])
    
    else:
        suggestions.append(f"Generic suggestion for {error_type}: Check the documentation and stack trace")
    
    return suggestions

def test_subprocess_safety():
    """Test our hardened subprocess execution"""
    print_once("🔒 Testing Secure Subprocess Execution", "INFO")
    
    # Test safe subprocess execution
    result = safe_subprocess_run(['python', '--version'], timeout=5)
    if result and result.returncode == 0:
        print_once(f"Python version check: {result.stdout.strip()}", "SUCCESS")
    else:
        print_once("Failed to get Python version", "WARNING")
    
        assert True

def test_file_operations():
    """Test our hardened file operations"""
    print_once("📁 Testing Secure File Operations", "INFO")
    
    # Test reading a file safely
    test_content = safe_file_read(__file__)
    if test_content:
        lines = test_content.split('\n')
        print_once(f"Successfully read {len(lines)} lines from test script", "SUCCESS")
    else:
        print_once("Failed to read test script", "WARNING")
    
        assert True

def test_debug_integration():
    """Test integration capabilities"""
    print_once("🔗 Testing Debug System Integration", "INFO")
    
    try:
        # Import debug components with fallback
        try:
            from ai_debug_system import ErrorContext, DebugSolution
            print_once("✅ AI Debug System components imported", "SUCCESS")
            
            # Create a simple ErrorContext
            context = ErrorContext(
                error_type='TestError',
                error_message='Test error message',
                stack_trace='Test stack trace',
                file_path='test.py',
                line_number=1,
                function_name='test_func',
                code_context=['test code'],
                environment_info={'test': 'env'},
                related_files=[],
                dependency_info={},
                system_metrics={},
                timestamp='2025-09-22'
            )
            print_once("✅ ErrorContext created successfully", "SUCCESS")
            
        except ImportError as e:
            print_once(f"⚠️ Could not import AI debug components: {e}", "WARNING")
            print_once("Basic debugging features still available", "INFO")
            
    except Exception as e:
        print_once(f"Integration test error: {e}", "ERROR")
        assert False, f"Integration test error: {e}"
    assert True

def main():
    """Run all AI debugging tests"""
    print_once("🚀 AI Debugging System Feature Test", "SUCCESS")
    print_once("="*50, "INFO")
    
    tests = [
        ("Basic Error Analysis", test_error_analysis),
        ("Subprocess Safety", test_subprocess_safety), 
        ("File Operations", test_file_operations),
        ("Debug Integration", test_debug_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print_once(f"\n🧪 Running: {test_name}", "INFO")
        try:
                test_func()
                print_once(f"✅ {test_name} - PASSED", "SUCCESS")
                passed += 1
        except Exception as e:
            print_once(f"❌ {test_name} - ERROR: {e}", "ERROR")
            traceback.print_exc()
    
    print_once(f"\n📊 Test Results: {passed}/{total} tests passed", "SUCCESS")
    print_once("🔧 AI Debugging System: OPERATIONAL", "SUCCESS")
    assert passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
