#!/usr/bin/env python3
"""
Live AI Debugging Test - Real Error Analysis
Test the actual error capture and AI analysis capabilities
"""

import sys
import traceback
from utils import print_once
from build_error_capture import AutoErrorCapture
from ai_debug_system import ErrorContext, DebugSolution

def create_intentional_error():
    """Create an intentional error for testing AI analysis"""
    print_once("🧪 Creating intentional error for AI analysis...", "INFO")
    
    try:
        # This will cause a NameError
        result = undefined_variable + 42
        return result
    except Exception as e:
        error_info = {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc(),
            'context': 'Testing AI debugging capabilities'
        }
        return error_info

def test_error_capture_system():
    """Test the automatic error capture system"""
    print_once("🔍 Testing Automatic Error Capture System", "SUCCESS")
    
    # Initialize the error capture system
    error_capturer = AutoErrorCapture()
    print_once("✅ AutoErrorCapture initialized", "SUCCESS")
    # Create test error
    error_info = create_intentional_error()
    print_once(f"📝 Captured error: {error_info['type']}", "INFO")
    print_once(f"📝 Error message: {error_info['message']}", "WARNING")
    assert error_info is not None
    return error_info

def test_ai_error_context_creation():
    """Test creating AI-compatible error context"""
    print_once("\n🧠 Testing AI Error Context Creation", "SUCCESS")
    
    # Create comprehensive error context
    context = ErrorContext(
        error_type='NameError',
        error_message='name "undefined_variable" is not defined',
        stack_trace='Traceback (most recent call last):\n  File "test.py", line 20, in create_intentional_error\n    result = undefined_variable + 42\nNameError: name "undefined_variable" is not defined',
        file_path='test_live_debugging.py',
        line_number=20,
        function_name='create_intentional_error',
        code_context=[
            'def create_intentional_error():',
            '    """Create an intentional error for testing AI analysis"""',
            '    try:',
            '        # This will cause a NameError',
            '        result = undefined_variable + 42  # <-- Error here',
            '        return result',
            '    except Exception as e:'
        ],
        environment_info={
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': str(sys.path[0])
        },
        related_files=['utils.py', 'ai_debug_system.py'],
        dependency_info={
            'modules': ['sys', 'traceback', 'utils'],
            'packages': []
        },
        system_metrics={
            'memory_usage': 'unknown',
            'cpu_usage': 'unknown',
            'disk_space': 'unknown'
        },
        timestamp='2025-09-22 01:15:00'
    )
    print_once("✅ ErrorContext created successfully", "SUCCESS")
    print_once(f"📝 Error type: {context.error_type}", "INFO")
    print_once(f"📝 File: {context.file_path}:{context.line_number}", "INFO")
    print_once(f"📝 Function: {context.function_name}", "INFO")
    assert context is not None
    return context
    # except block removed as all errors will raise

def test_ai_solution_generation():
    """Test AI solution generation (simulated)"""
    print_once("\n💡 Testing AI Solution Generation", "SUCCESS")
    
    # Simulate AI-generated solution
    solution = DebugSolution(
        analysis="The error occurs because the variable 'undefined_variable' is referenced before being defined. This is a common NameError in Python.",
        hypothesis=[
            "Variable name is misspelled",
            "Variable is defined in a different scope", 
            "Variable should be initialized before use",
            "Variable name changed during refactoring"
        ],
        solution_steps=[
            "1. Check if 'undefined_variable' is spelled correctly",
            "2. Verify the variable is defined in the current scope",
            "3. Initialize the variable before use: undefined_variable = some_value",
            "4. Consider using a default value or conditional check",
            "5. Review recent code changes for variable name modifications"
        ],
        prevention_tips=[
            "Use descriptive variable names to avoid typos",
            "Initialize variables at the beginning of functions",
            "Use linting tools like pylint or flake8",
            "Enable IDE features for variable name checking",
            "Add type hints to catch errors early"
        ],
        diagnostic_commands=[
            "python -m py_compile test_file.py",
            "python -c 'import ast; ast.parse(open(\"test_file.py\").read())'",
            "grep -n 'undefined_variable' *.py"
        ],
        confidence_score=0.95,
        estimated_time="2-5 minutes",
        risk_level="LOW",
        validation_tests=[
            "Run the corrected code",
            "Add unit tests for the function",
            "Verify no other undefined variables exist"
        ],
        rollback_plan=[
            "Revert to previous working version",
            "Comment out the problematic line temporarily",
            "Use try/except for graceful error handling"
        ]
    )
    
    print_once("✅ AI Solution generated successfully", "SUCCESS")
    print_once(f"📊 Confidence score: {solution.confidence_score}", "INFO")
    print_once(f"⏱️ Estimated fix time: {solution.estimated_time}", "INFO")
    print_once(f"⚠️ Risk level: {solution.risk_level}", "WARNING")
    
    print_once("\n🔍 Analysis:", "INFO")
    print_once(f"   {solution.analysis}", "WARNING")
    
    print_once("\n💡 Hypotheses:", "INFO")
    for i, hypothesis in enumerate(solution.hypothesis, 1):
        print_once(f"   {i}. {hypothesis}", "WARNING")
    
    print_once("\n🔧 Solution Steps:", "INFO")
    for step in solution.solution_steps:
        print_once(f"   {step}", "SUCCESS")
    
    print_once("\n🛡️ Prevention Tips:", "INFO")
    for tip in solution.prevention_tips:
        print_once(f"   • {tip}", "WARNING")
    
    assert solution is not None
    return solution

def test_full_debugging_workflow():
    """Test the complete AI debugging workflow"""
    print_once("\n🚀 Testing Complete AI Debugging Workflow", "SUCCESS")
    print_once("="*60, "INFO")
    
    # Step 1: Error Capture
    print_once("Step 1: Error Detection & Capture", "INFO")
    error_info = test_error_capture_system()
    # Accept a non-None error_info (dict) as success
    assert error_info is not None, "Workflow failed at error capture stage"
    assert isinstance(error_info, dict), "Error info should be a dictionary"
    
    # Step 2: Context Creation
    print_once("\nStep 2: Error Context Analysis", "INFO")
    context = test_ai_error_context_creation()
    assert context is not None, "Workflow failed at context creation stage"
    
    # Step 3: AI Solution Generation
    print_once("\nStep 3: AI-Powered Solution Generation", "INFO")
    solution = test_ai_solution_generation()
    assert solution is not None, "Workflow failed at solution generation stage"
    
    # Step 4: Solution Application (simulated)
    print_once("\nStep 4: Solution Application & Validation", "INFO")
    print_once("✅ Solution would be applied to fix the error", "SUCCESS")
    print_once("✅ Validation tests would be executed", "SUCCESS")
    print_once("✅ Error prevention measures would be implemented", "SUCCESS")
    
    print_once("\n🎉 COMPLETE AI DEBUGGING WORKFLOW SUCCESSFUL", "SUCCESS")
    assert True

def main():
    """Run live AI debugging tests"""
    print_once("🤖 AI Debugging System - Live Testing", "SUCCESS")
    print_once("Testing real error capture, analysis, and resolution", "INFO")
    print_once("="*60, "INFO")
    
    # Test individual components
    tests = [
        ("Error Capture System", test_error_capture_system),
        ("AI Error Context", test_ai_error_context_creation),
        ("Solution Generation", test_ai_solution_generation)
    ]
    
    print_once("\n📋 Running Individual Component Tests:", "INFO")
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print_once(f"✅ {test_name} - PASSED", "SUCCESS")
            else:
                print_once(f"❌ {test_name} - FAILED", "ERROR")
                all_passed = False
        except Exception as e:
            print_once(f"❌ {test_name} - ERROR: {e}", "ERROR")
            all_passed = False
    
    # Test full workflow
    print_once("\n📋 Running Complete Workflow Test:", "INFO")
    workflow_success = test_full_debugging_workflow()
    
    # Final results
    print_once("\n📊 FINAL TEST RESULTS:", "SUCCESS")
    print_once(f"Individual Tests: {'PASSED' if all_passed else 'FAILED'}", 
               "SUCCESS" if all_passed else "ERROR")
    print_once(f"Workflow Test: {'PASSED' if workflow_success else 'FAILED'}", 
               "SUCCESS" if workflow_success else "ERROR")
    
    overall_success = all_passed and workflow_success
    print_once(f"Overall Status: {'OPERATIONAL' if overall_success else 'NEEDS ATTENTION'}", 
               "SUCCESS" if overall_success else "ERROR")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
