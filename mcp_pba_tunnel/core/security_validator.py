import re
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation for MCP tools"""
    
    def __init__(self):
        self.blocked_patterns = [
            r'../', r'\.\..*', r'%2e%2e', r'%c0%ae',  # Path traversal
            r'<script', r'javascript:', r'on\w+\s*=',  # XSS
            r'union\s+select', r'drop\s+table', r'insert\s+into',  # SQL injection
            r'sudo', r'su', r'chmod', r'chown', r'passwd',  # Dangerous commands
        ]
        
        self.allowed_commands = [
            'ls', 'cat', 'grep', 'find', 'head', 'tail', 'wc', 'sort', 'uniq', 'cut', 'awk', 'sed'
        ]
    
    def validate_input(self, input_data: Any, max_length: int = 10000) -> bool:
        """Validate input data for security issues"""
        if isinstance(input_data, str):
            if len(input_data) > max_length:
                return False
            
            input_lower = input_data.lower()
            for pattern in self.blocked_patterns:
                if re.search(pattern, input_lower):
                    logger.warning(f"Blocked pattern detected: {pattern}")
                    return False
        
        return True
    
    def validate_file_path(self, file_path: str, allowed_paths: List[str] = None) -> bool:
        """Validate file path for security"""
        if not file_path:
            return False
            
        # Check for path traversal
        if '..' in file_path or '%2e%2e' in file_path.lower():
            return False
            
        # Check allowed paths
        if allowed_paths:
            path_obj = Path(file_path).resolve()
            for allowed_path in allowed_paths:
                if str(path_obj).startswith(str(Path(allowed_path).resolve())):
                    return True
            return False
            
        return True
    
    def validate_command(self, command: str) -> bool:
        """Validate terminal command for security"""
        if not command:
            return False
            
        # Check for dangerous commands
        command_parts = command.split()
        if not command_parts:
            return False
            
        base_command = command_parts[0]
        if base_command in self.allowed_commands:
            return True
            
        # Block dangerous commands
        dangerous_commands = ['rm', 'rmdir', 'del', 'format', 'dd', 'mkfs', 'mount', 'umount', 'sudo', 'su', 'chmod', 'chown', 'passwd']
        if base_command in dangerous_commands:
            logger.warning(f"Dangerous command blocked: {base_command}")
            return False
            
        return True
    
    def sanitize_output(self, output: str, max_length: int = 1000000) -> str:
        """Sanitize output for safe display"""
        if not output:
            return ""
            
        if len(output) > max_length:
            output = output[:max_length] + "... [output truncated]"
            
        # Remove potentially dangerous content
        output = re.sub(r'<script[^>]*>.*?</script>', '', output, flags=re.IGNORECASE | re.DOTALL)
        output = re.sub(r'javascript:', '', output, flags=re.IGNORECASE)
        output = re.sub(r'on\w+\s*=', '', output, flags=re.IGNORECASE)
        
        return output
