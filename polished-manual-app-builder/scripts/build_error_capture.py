#!/usr/bin/env python3
"""
Automated Error Capture and Documentation System
Follows error prevention protocols by automatically adding new errors to the guide
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from utils import safe_subprocess_run, print_once

class AutoErrorCapture:
    """Automatically captures and documents errors according to our protocols"""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.error_guide_path = self.project_root / "docs" / "ERROR_PREVENTION_GUIDE.md"
        self.error_log_path = self.project_root / "logs" / "captured_errors.json"
        
        # Ensure logs directory exists
        self.error_log_path.parent.mkdir(exist_ok=True)
        
        # Load existing errors
        self.existing_errors = self._load_existing_errors()
        
    def _load_existing_errors(self) -> List[Dict[str, Any]]:
        """Load existing error log"""
        if self.error_log_path.exists():
            with open(self.error_log_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_error_log(self):
        """Save error log to file"""
        with open(self.error_log_path, 'w') as f:
            json.dump(self.existing_errors, f, indent=2, default=str)
    
    def capture_powershell_error(self, error_text: str, script_path: str) -> Optional[Dict[str, Any]]:
        """Capture PowerShell script error and add to documentation"""
        
        # Parse the error
        error_info = self._parse_powershell_error(error_text, script_path)
        
        # Check if this error already exists
        if not self._is_duplicate_error(error_info):
            # Add to error log
            self.existing_errors.append(error_info)
            self._save_error_log()
            
            # Add to error prevention guide
            self._add_to_error_guide(error_info)
            
            print(f"✅ New error captured and documented: {error_info['error_type']}")
            return error_info
        else:
            print("⚠️ Duplicate error type, skipping...")
            return None
    
    def _parse_powershell_error(self, error_text: str, script_path: str) -> Dict[str, Any]:
        """Parse PowerShell error information"""
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "script_path": script_path,
            "error_text": error_text,
            "error_type": "PowerShell Script Error",
            "category": "Development & Build Errors",
            "severity": "Medium",
            "language": "PowerShell"
        }
        
        # Parse specific error types
        if "Variable reference is not valid" in error_text:
            error_info.update({
                "error_type": "PowerShell Variable Reference Syntax Error",
                "error_code": "ERROR-504",
                "specific_issue": "Invalid variable reference with colon",
                "solution": "Use proper PowerShell variable expansion syntax"
            })
        elif "is not supported in this version of the language" in error_text:
            error_info.update({
                "error_type": "PowerShell Mixed Language Syntax Error", 
                "error_code": "ERROR-505",
                "specific_issue": "Mixing Python/other language syntax in PowerShell",
                "solution": "Separate code blocks and use proper execution methods"
            })
        elif "is assigned but never used" in error_text:
            error_info.update({
                "error_type": "PowerShell Unused Variable Warning",
                "error_code": "ERROR-506", 
                "specific_issue": "Variables assigned but not referenced",
                "solution": "Use variables or remove assignments"
            })
        elif "ParseException" in error_text:
            error_info.update({
                "error_type": "PowerShell Parse Exception",
                "error_code": "ERROR-507",
                "specific_issue": "Syntax error in PowerShell script",
                "solution": "Fix syntax errors and validate script"
            })
        
        # Extract line number if available
        line_match = re.search(r'line (\d+)', error_text)
        if line_match:
            error_info["line_number"] = str(int(line_match.group(1)))
        
        # Extract character position if available  
        char_match = re.search(r'char (\d+)', error_text)
        if char_match:
            error_info["character_position"] = str(int(char_match.group(1)))
        
        return error_info
    
    def _is_duplicate_error(self, new_error: Dict[str, Any]) -> bool:
        """Check if this error type already exists"""
        for existing in self.existing_errors:
            if (existing.get("error_type") == new_error.get("error_type") and
                existing.get("specific_issue") == new_error.get("specific_issue")):
                return True
        return False
    
    def _add_to_error_guide(self, error_info: Dict[str, Any]):
        """Add error to the prevention guide following our format"""
        
        if not self.error_guide_path.exists():
            print("❌ Error prevention guide not found!")
            return
        
        # Read current guide
        with open(self.error_guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the next error number
        error_numbers = re.findall(r'ERROR-(\d+):', content)
        next_number = max([int(n) for n in error_numbers]) + 1 if error_numbers else 507
        
        # Create new error entry
        new_entry = self._format_error_entry(error_info, f"ERROR-{next_number}")
        
        # Find insertion point (before "## 🚀 Runtime & Production Errors")
        insertion_point = content.find("## 🚀 Runtime & Production Errors")
        if insertion_point == -1:
            # Fallback: insert before last section
            insertion_point = content.find("## 📚 Additional Resources")
        
        if insertion_point != -1:
            # Insert the new error
            updated_content = (content[:insertion_point] + 
                             new_entry + "\n" +
                             content[insertion_point:])
            
            # Write back to file
            with open(self.error_guide_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ Added ERROR-{next_number} to prevention guide")
        else:
            print("❌ Could not find insertion point in error guide")
    
    def _format_error_entry(self, error_info: Dict[str, Any], error_code: str) -> str:
        """Format error entry according to our documentation standard"""
        
        # Generate solution based on error type
        solution = self._generate_solution(error_info)
        prevention = self._generate_prevention(error_info)
        
        entry = f"""
### {error_code}: {error_info['error_type']}
**Symptom:** {error_info.get('specific_issue', 'Script execution failure')}

**Solution:**
```powershell
{solution}
```

**Prevention:**
{prevention}

**Root Cause:** {self._determine_root_cause(error_info)}

---
"""
        return entry
    
    def _generate_solution(self, error_info: Dict[str, Any]) -> str:
        """Generate solution code based on error type"""
        
        error_type = error_info.get('error_type', '')
        
        if "Variable Reference" in error_type:
            return """# ❌ Incorrect: Using $_ in string interpolation
Write-Log "Failed: $_" "ERROR"

# ✅ Correct: Use proper PowerShell variable expansion  
Write-Log "Failed: $($_.Exception.Message)" "ERROR"

# Alternative: Use separate variable
$ErrorMessage = $_.Exception.Message
Write-Log "Failed: $ErrorMessage" "ERROR" """

        elif "Mixed Language" in error_type:
            return """# ❌ Incorrect: Mixing Python syntax in PowerShell
from module import function

# ✅ Correct: Use Here-String with proper execution
$PythonScript = @"
from module import function
function()
"@
$PythonScript | python"""

        elif "Unused Variable" in error_type:
            return """# ❌ Incorrect: Assigning but not using variables
$Result = some-command

# ✅ Correct: Use variables or remove assignment
$Result = some-command
if ($Result) { Write-Host $Result }

# Or suppress output without assignment
$null = some-command"""

        else:
            return """# Check script syntax
Test-ScriptFileInfo -Path $ScriptPath

# Use strict mode for better error detection
Set-StrictMode -Version Latest

# Validate PowerShell syntax
$ParseErrors = $null
[System.Management.Automation.PSParser]::Tokenize($ScriptContent, [ref]$ParseErrors)
if ($ParseErrors) { Write-Error "Syntax errors found" }"""
    
    def _generate_prevention(self, error_info: Dict[str, Any]) -> str:
        """Generate prevention guidelines"""
        
        error_type = error_info.get('error_type', '')
        
        common_prevention = [
            "- Use PowerShell ISE or VS Code with PowerShell extension",
            "- Enable script analysis with PSScriptAnalyzer",
            "- Test scripts with `Set-StrictMode -Version Latest`",
            "- Use proper error handling with try/catch blocks"
        ]
        
        specific_prevention = []
        
        if "Variable Reference" in error_type:
            specific_prevention.extend([
                "- Always use `$($_.Exception.Message)` instead of `$_` in strings",
                "- Use subexpression syntax `$()` for complex variable references"
            ])
        elif "Mixed Language" in error_type:
            specific_prevention.extend([
                "- Separate PowerShell and other language code blocks", 
                "- Use Here-Strings or temporary files for multi-language execution"
            ])
        elif "Unused Variable" in error_type:
            specific_prevention.extend([
                "- Remove unnecessary variable assignments",
                "- Use `$null = command` to suppress output without assignment"
            ])
        
        all_prevention = specific_prevention + common_prevention
        return "\n".join(all_prevention)
    
    def _determine_root_cause(self, error_info: Dict[str, Any]) -> str:
        """Determine root cause based on error type"""
        
        error_type = error_info.get('error_type', '')
        
        if "Variable Reference" in error_type:
            return "Invalid PowerShell variable reference syntax in string interpolation"
        elif "Mixed Language" in error_type:
            return "Attempting to execute non-PowerShell syntax directly in PowerShell"
        elif "Unused Variable" in error_type:
            return "Variables assigned but never referenced in script execution"
        else:
            return "PowerShell syntax or execution error"

def capture_terminal_error():
    """Capture error from terminal output and add to documentation"""
    
    if len(sys.argv) < 3:
        print("Usage: python build_error_capture.py <script_path> <error_text>")
        return
    
    script_path = sys.argv[1]
    error_text = sys.argv[2]
    
    # Initialize error capture system
    capture_system = AutoErrorCapture()
    
    # Capture the error
    if "powershell" in script_path.lower() or ".ps1" in script_path.lower():
        captured = capture_system.capture_powershell_error(error_text, script_path)
        
        if captured:
            print("\n🎉 ERROR CAPTURE COMPLETE!")
            print(f"Error Code: {captured.get('error_code', 'N/A')}")
            print(f"Error Type: {captured['error_type']}")
            print(f"Added to: {capture_system.error_guide_path}")
            print(f"Logged to: {capture_system.error_log_path}")
        
        # Update error learning system
        try:
            learning_script = capture_system.project_root / "scripts" / "error_learning_engine.py"
            if learning_script.exists():
                safe_subprocess_run([sys.executable, str(learning_script), "--update-from-capture"],
                                   timeout=60)
        except Exception as e:
            print(f"⚠️ Could not update learning system: {e}")

def capture_from_terminal_id(terminal_id: Optional[str] = None) -> None:
    """Capture error from specific terminal output"""
    
    if not terminal_id:
        # Try to get terminal ID from environment or default
        terminal_id = os.environ.get('VSCODE_TERMINAL_ID', '48388')
    
    try:
        # This would integrate with VS Code terminal API
        # For now, we'll use the current approach
        print(f"Monitoring terminal {terminal_id} for errors...")
        print("Manual error capture available via command line")
        
    except Exception as e:
        print(f"Could not access terminal {terminal_id}: {e}")

# Auto-capture PowerShell errors when this script is imported
def setup_auto_capture():
    """Setup automatic error capture for the project"""
    
    capture_system = AutoErrorCapture()
    
    # Create auto-capture wrapper scripts
    wrapper_script = capture_system.project_root / "scripts" / "run-with-error-capture.ps1"
    
    wrapper_content = """
# PowerShell Error Capture Wrapper
param([string]$ScriptPath, [string[]]$Arguments)

try {
    if ($Arguments) {
        & $ScriptPath @Arguments
    } else {
        & $ScriptPath
    }
} catch {
    $ErrorDetails = $_.Exception.Message + "`n" + $_.ScriptStackTrace
    python "scripts/build_error_capture.py" $ScriptPath $ErrorDetails
    throw
}
"""
    
    with open(wrapper_script, 'w') as f:
        f.write(wrapper_content)
    
    print(f"✅ Auto-capture wrapper created: {wrapper_script}")
    print("Usage: ./scripts/run-with-error-capture.ps1 'your-script.ps1'")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_auto_capture()
    elif len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        terminal_id = sys.argv[2] if len(sys.argv) > 2 else None
        capture_from_terminal_id(terminal_id)
    else:
        capture_terminal_error()
    
    print("Error capture test completed")


def main() -> None:
    """Main function for running error capture tests"""
    # Test basic error capture functionality
    capture_system = AutoErrorCapture()
    
    # You can test with actual errors here
    test_error = "The variable 'TestVariable' is assigned but never used"
    test_script = "test_script.ps1"
    
    captured = capture_system.capture_powershell_error(test_error, test_script)
    if captured:
        print(f"✅ Test error captured: {captured['error_type']}")
    else:
        print("⚠️ No error captured in test")


if __name__ == "__main__":
    main()
