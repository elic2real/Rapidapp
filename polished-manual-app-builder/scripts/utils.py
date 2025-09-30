#!/usr/bin/env python3
"""
🔧 Autonomous Python Repo Hardening Utilities
Canonical utility functions for compliance, security, and robustness

Platform Compatibility: Windows & Unix/Linux/macOS
Dependency Management: Graceful fallbacks for optional packages
Security Features: Input validation, subprocess hardening, file safety
"""

import hashlib
import logging
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import asyncio

# Platform detection for compatibility
IS_WINDOWS = platform.system() == 'Windows'
IS_UNIX = platform.system() in ('Linux', 'Darwin')

# Platform-specific constants
if IS_WINDOWS:
    NULL_DEVICE = 'nul'
    PATH_SEP = '\\'
    LINE_ENDING = '\r\n'
else:
    NULL_DEVICE = '/dev/null'
    PATH_SEP = '/'
    LINE_ENDING = '\n'

# Optional dependencies with graceful fallbacks
try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    aiofiles = None
    HAS_AIOFILES = False
    print("⚠️ aiofiles not available - async file operations disabled")

# Global state for print_once
_PRINTED_MESSAGES: Set[str] = set()

def print_once(message: str, level: str = "INFO", throttle_key: Optional[str] = None) -> None:
    """
    Print a message only once per session to prevent log spam.
    
    Args:
        message: The message to print
        level: Log level (INFO, WARNING, ERROR)
        throttle_key: Optional custom key for throttling, defaults to message hash
    """
    if throttle_key is None:
        throttle_key = hashlib.md5(message.encode()).hexdigest()[:8]
    
    if throttle_key not in _PRINTED_MESSAGES:
        _PRINTED_MESSAGES.add(throttle_key)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "WARNING": "⚠️", 
            "ERROR": "❌",
            "SUCCESS": "✅"
        }.get(level, "📝")
        
        print(f"[{timestamp}] {prefix} {message}")


def validate_path(path: Union[str, Path], must_exist: bool = False, 
                  must_be_file: bool = False, must_be_dir: bool = False) -> bool:
    """
    Enhanced path validation with security checks.
    
    Args:
        path: Path to validate
        must_exist: Whether path must exist
        must_be_file: Whether path must be a file
        must_be_dir: Whether path must be a directory
        
    Returns:
        True if valid and meets all requirements
    """
    try:
        path_obj = Path(path)
        
        # Basic security checks
        if '..' in str(path) or str(path_obj).startswith('~'):
            print_once(f"Potentially unsafe path detected: {path}", "WARNING")
            
        # Platform-specific path validation
        if IS_WINDOWS:
            # Check for invalid Windows characters
            invalid_chars = '<>:"|?*'
            if any(char in str(path) for char in invalid_chars):
                print_once(f"Invalid Windows path characters in: {path}", "ERROR")
                return False
        
        # Existence checks
        if must_exist and not path_obj.exists():
            return False
            
        if path_obj.exists():
            if must_be_file and not path_obj.is_file():
                return False
            if must_be_dir and not path_obj.is_dir():
                return False
                
        return True
    except Exception as e:
        print_once(f"Path validation error for {path}: {e}", "ERROR")
        return False


def safe_file_read(file_path: Union[str, Path], encoding: str = 'utf-8', 
                   default: Optional[str] = None) -> Optional[str]:
    """
    Safely read a file with proper error handling and encoding.
    
    Args:
        file_path: Path to file
        encoding: File encoding (default utf-8)
        default: Default value if file cannot be read
    
    Returns:
        File content or default value
    """
    try:
        path_obj = Path(file_path)
        if not path_obj.exists():
            print_once(f"File not found: {file_path}", "WARNING")
            return default
            
        with open(path_obj, 'r', encoding=encoding, errors='replace') as f:
            return f.read()
    except Exception as e:
        print_once(f"Error reading file {file_path}: {e}", "ERROR")
        return default


def safe_file_write(file_path: Union[str, Path], content: str, 
                    encoding: str = 'utf-8', backup: bool = True) -> bool:
    """
    Safely write to a file with proper error handling and optional backup.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding (default utf-8)
        backup: Create backup of existing file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        path_obj = Path(file_path)
        
        # Create parent directories if needed
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists and backup is enabled
        if backup and path_obj.exists():
            backup_path = path_obj.with_suffix(f"{path_obj.suffix}.backup")
            path_obj.rename(backup_path)
            print_once(f"Created backup: {backup_path}", "INFO")
        
        with open(path_obj, 'w', encoding=encoding, newline='') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print_once(f"Error writing file {file_path}: {e}", "ERROR")
        return False


async def safe_async_file_read(file_path: Union[str, Path], encoding: str = 'utf-8',
                               default: Optional[str] = None) -> Optional[str]:
    """
    Async version of safe file read.
    """
    if not HAS_AIOFILES:
        print_once("aiofiles not available, falling back to sync read", "WARNING")
        return safe_file_read(file_path, encoding, default)
    
    try:
        path_obj = Path(file_path)
        if not path_obj.exists():
            print_once(f"File not found: {file_path}", "WARNING")
            return default
            
        if HAS_AIOFILES and aiofiles:
            async with aiofiles.open(path_obj, 'r', encoding=encoding, errors='replace') as f:
                return await f.read()
        else:
            # Fallback to sync read
            return safe_file_read(path_obj, encoding, default)
    except Exception as e:
        print_once(f"Error reading file {file_path}: {e}", "ERROR")
        return default


async def safe_async_file_write(file_path: Union[str, Path], content: str,
                                encoding: str = 'utf-8', backup: bool = True) -> bool:
    """
    Async version of safe file write.
    """
    if not HAS_AIOFILES:
        print_once("aiofiles not available, falling back to sync write", "WARNING")
        return safe_file_write(file_path, content, encoding, backup)
    
    try:
        path_obj = Path(file_path)
        
        # Create parent directories if needed
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup if file exists and backup is enabled
        if backup and path_obj.exists():
            backup_path = path_obj.with_suffix(f"{path_obj.suffix}.backup")
            # Remove existing backup first to avoid Windows error
            if backup_path.exists():
                backup_path.unlink()
            content_backup = safe_file_read(path_obj)
            if content_backup:
                with open(backup_path, 'w', encoding=encoding) as f:
                    f.write(content_backup)
                print_once(f"Created backup: {backup_path}", "INFO")
        
        if HAS_AIOFILES and aiofiles:
            async with aiofiles.open(path_obj, 'w', encoding=encoding) as f:
                await f.write(content)
        else:
            # Fallback to sync write
            with open(path_obj, 'w', encoding=encoding) as f:
                f.write(content)
        
        return True
    except Exception as e:
        print_once(f"Error writing file {file_path}: {e}", "ERROR")
        return False


def safe_subprocess_run(cmd: List[str], timeout: int = 30, 
                        shell: bool = False, capture_output: bool = True,
                        cwd: Optional[str] = None) -> Optional[subprocess.CompletedProcess]:
    """
    Safely run subprocess with proper error handling and timeouts.
    
    Args:
        cmd: Command and arguments as list
        timeout: Timeout in seconds
        shell: Whether to use shell (discouraged for security)
        capture_output: Whether to capture stdout/stderr
        cwd: Working directory
    
    Returns:
        CompletedProcess or None if failed
    """
    try:
        if shell and len(cmd) > 1:
            print_once("Warning: shell=True with multiple arguments is dangerous", "WARNING")
        
        result = subprocess.run(
            cmd,
            timeout=timeout,
            shell=shell,
            capture_output=capture_output,
            text=True,
            cwd=cwd,
            check=False  # Don't raise on non-zero exit
        )
        
        if result.returncode != 0:
            print_once(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}", "WARNING")
        
        return result
    except subprocess.TimeoutExpired:
        print_once(f"Command timed out after {timeout}s: {' '.join(cmd)}", "ERROR")
        return None
    except Exception as e:
        print_once(f"Error running command {' '.join(cmd)}: {e}", "ERROR")
        return None


def validate_input(value: Any, expected_type: type, 
                   min_val: Optional[Union[int, float]] = None,
                   max_val: Optional[Union[int, float]] = None,
                   allow_none: bool = False) -> bool:
    """
    Validate input parameters with type and range checking.
    
    Args:
        value: Value to validate
        expected_type: Expected Python type
        min_val: Minimum value (for numbers)
        max_val: Maximum value (for numbers)
        allow_none: Whether None is acceptable
    
    Returns:
        True if valid, False otherwise
    """
    if value is None:
        return allow_none
    
    if not isinstance(value, expected_type):
        print_once(f"Type validation failed: expected {expected_type}, got {type(value)}", "ERROR")
        return False
    
    if isinstance(value, (int, float)):
        if min_val is not None and value < min_val:
            print_once(f"Value {value} below minimum {min_val}", "ERROR")
            return False
        if max_val is not None and value > max_val:
            print_once(f"Value {value} above maximum {max_val}", "ERROR")
            return False
        if not math.isfinite(value):
            print_once(f"Value {value} is not finite", "ERROR")
            return False
    
    return True


def clamp_value(value: Union[int, float], min_val: Union[int, float], 
                max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp a numeric value to a safe range.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Clamped value
    """
    if not math.isfinite(value):
        print_once(f"Clamping non-finite value {value} to {min_val}", "WARNING")
        return min_val
    
    return max(min_val, min(max_val, value))


def safe_round(value: float, decimals: int = 2) -> float:
    """
    Safely round a number with NaN/infinity checks.
    
    Args:
        value: Number to round
        decimals: Decimal places
    
    Returns:
        Rounded number or 0.0 if invalid
    """
    if not math.isfinite(value):
        print_once(f"Cannot round non-finite value: {value}", "WARNING")
        return 0.0
    
    return round(value, decimals)


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Safely truncate strings for logging (prevent secret leaks).
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def mask_sensitive_data(text: str, patterns: Optional[List[str]] = None) -> str:
    """
    Mask sensitive data in strings for safe logging.
    
    Args:
        text: Text to mask
        patterns: Custom regex patterns to mask
    
    Returns:
        Masked text
    """
    import re
    
    # Default sensitive patterns
    default_patterns = [
        r'(?i)(password|pwd|secret|key|token|auth|api_key)\s*[:=]\s*[\'"]*([^\s\'"]+)',
        r'(?i)(bearer\s+)([a-zA-Z0-9\-._~+/]+=*)',
        r'[a-f0-9]{32,}',  # Hex strings (potential hashes/keys)
    ]
    
    all_patterns = default_patterns + (patterns or [])
    
    masked_text = text
    for pattern in all_patterns:
        masked_text = re.sub(pattern, r'\1***MASKED***', masked_text)
    
    return masked_text


class CanonicalFunctions:
    """
    Canonical implementations of common functions to prevent duplication.
    """
    
    @staticmethod
    def print_once(message: str, level: str = "INFO") -> None:
        """Canonical print_once implementation"""
        return print_once(message, level)
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safe division with zero check"""
        if not math.isfinite(numerator) or not math.isfinite(denominator):
            return default
        if abs(denominator) < 1e-10:  # Effectively zero
            return default
        return numerator / denominator
    
    @staticmethod
    def safe_log(value: float, base: float = math.e, default: float = 0.0) -> float:
        """Safe logarithm with domain checks"""
        if not math.isfinite(value) or value <= 0:
            return default
        try:
            if base == math.e:
                return math.log(value)
            return math.log(value, base)
        except (ValueError, ZeroDivisionError):
            return default


# Export canonical functions for easy import
__all__ = [
    'print_once',
    'safe_file_read',
    'safe_file_write', 
    'safe_async_file_read',
    'safe_async_file_write',
    'safe_subprocess_run',
    'validate_input',
    'clamp_value',
    'safe_round',
    'truncate_string',
    'mask_sensitive_data',
    'CanonicalFunctions'
]
