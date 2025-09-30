#!/usr/bin/env python3
"""
Automated Error Learning System
Analyzes error patterns, suggests solutions, and updates the error prevention guide
"""

import json
import asyncio
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import aiofiles
from collections import defaultdict, Counter
import yaml

@dataclass
class ErrorPattern:
    pattern_hash: str
    error_type: str
    service: str
    context: str
    message: str
    first_seen: str
    last_seen: str
    occurrence_count: int
    resolved: bool
    solution: Optional[str]
    prevention_tips: List[str]
    related_errors: List[str]
    severity: str
    auto_suggested_solution: Optional[str] = None
    confidence_score: float = 0.0

@dataclass
class ErrorSolution:
    error_pattern: str
    solution_text: str
    prevention_steps: List[str]
    related_commands: List[str]
    confidence: float
    source: str  # 'auto_generated', 'manual', 'pattern_match'

class ErrorLearningEngine:
    """Main engine for learning from errors and updating the guide"""
    
    def __init__(self):
        self.logs_dir = Path("logs/errors")
        self.docs_dir = Path("docs")
        self.error_guide_path = self.docs_dir / "ERROR_PREVENTION_GUIDE.md"
        self.knowledge_base_path = self.logs_dir / "error_knowledge_base.json"
        self.patterns_cache = {}
        
        # Error pattern matchers
        self.solution_patterns = {
            # Database connection errors
            r"connection.*refused|connection.*timeout|database.*unavailable": {
                "solution": "Check database service status and connectivity",
                "commands": ["docker ps", "docker logs <db_container>", "docker compose restart <db_service>"],
                "prevention": ["Implement connection pooling", "Add health checks", "Set appropriate timeouts"]
            },
            
            # Port binding errors
            r"port.*already.*in.*use|address.*already.*in.*use": {
                "solution": "Stop conflicting services or change port configuration",
                "commands": ["netstat -tulpn | grep <port>", "docker compose down", "lsof -i :<port>"],
                "prevention": ["Use dynamic port allocation", "Check port availability before startup"]
            },
            
            # Docker errors
            r"docker.*not.*found|docker.*daemon.*not.*running": {
                "solution": "Start Docker service and ensure Docker is properly installed",
                "commands": ["systemctl start docker", "docker --version", "docker info"],
                "prevention": ["Add Docker to startup services", "Verify Docker installation"]
            },
            
            # Memory errors
            r"out.*of.*memory|memory.*allocation.*failed": {
                "solution": "Increase available memory or optimize memory usage",
                "commands": ["docker stats", "free -h", "docker compose restart"],
                "prevention": ["Set memory limits", "Implement memory monitoring", "Optimize data structures"]
            },
            
            # Permission errors
            r"permission.*denied|access.*denied": {
                "solution": "Check and fix file/directory permissions",
                "commands": ["ls -la", "chmod +x <file>", "chown <user>:<group> <file>"],
                "prevention": ["Set proper file permissions", "Use appropriate user contexts"]
            },
            
            # Network errors
            r"network.*unreachable|connection.*timed.*out": {
                "solution": "Check network connectivity and service availability",
                "commands": ["ping <host>", "curl -v <url>", "docker network ls"],
                "prevention": ["Implement retry logic", "Add network health checks"]
            }
        }
    
    async def analyze_and_learn(self):
        """Main method to analyze errors and update knowledge"""
        print("🧠 Starting automated error learning...")
        
        # Load existing patterns
        await self.load_knowledge_base()
        
        # Process new errors
        new_patterns = await self.process_pending_errors()
        
        # Analyze patterns and generate solutions
        for pattern in new_patterns:
            await self.analyze_pattern(pattern)
        
        # Update error guide
        if new_patterns:
            await self.update_error_guide(new_patterns)
        
        # Save updated knowledge base
        await self.save_knowledge_base()
        
        print(f"✅ Processed {len(new_patterns)} new error patterns")
    
    async def load_knowledge_base(self):
        """Load existing error knowledge base"""
        if self.knowledge_base_path.exists():
            async with aiofiles.open(self.knowledge_base_path, 'r') as f:
                data = json.loads(await f.read())
                self.patterns_cache = {
                    k: ErrorPattern(**v) for k, v in data.items()
                }
        else:
            self.patterns_cache = {}
    
    async def save_knowledge_base(self):
        """Save updated knowledge base"""
        self.knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            k: asdict(v) for k, v in self.patterns_cache.items()
        }
        
        async with aiofiles.open(self.knowledge_base_path, 'w') as f:
            await f.write(json.dumps(data, indent=2, default=str))
    
    async def process_pending_errors(self) -> List[ErrorPattern]:
        """Process pending error patterns from all services"""
        new_patterns = []
        
        # Process pending errors from all services
        for error_file in self.logs_dir.glob("pending-error-patterns.jsonl"):
            async with aiofiles.open(error_file, 'r') as f:
                async for line in f:
                    if line.strip():
                        try:
                            error_data = json.loads(line)
                            pattern = ErrorPattern(**error_data)
                            
                            # Check if we've seen this pattern before
                            if pattern.pattern_hash in self.patterns_cache:
                                # Update existing pattern
                                existing = self.patterns_cache[pattern.pattern_hash]
                                existing.occurrence_count += 1
                                existing.last_seen = pattern.last_seen
                            else:
                                # New pattern
                                self.patterns_cache[pattern.pattern_hash] = pattern
                                new_patterns.append(pattern)
                                
                        except Exception as e:
                            print(f"Error processing line: {e}")
            
            # Clear processed file
            await self.clear_file(error_file)
        
        return new_patterns
    
    async def analyze_pattern(self, pattern: ErrorPattern):
        """Analyze error pattern and generate solution suggestions"""
        # Try to match against known solution patterns
        error_text = f"{pattern.error_type} {pattern.message}".lower()
        
        best_match = None
        best_confidence = 0.0
        
        for pattern_regex, solution_data in self.solution_patterns.items():
            if re.search(pattern_regex, error_text, re.IGNORECASE):
                confidence = self.calculate_confidence(pattern_regex, error_text)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = solution_data
        
        if best_match and best_confidence > 0.7:
            pattern.auto_suggested_solution = best_match["solution"]
            pattern.prevention_tips = best_match["prevention"]
            pattern.confidence_score = best_confidence
        
        # Analyze related errors
        pattern.related_errors = await self.find_related_errors(pattern)
    
    def calculate_confidence(self, pattern_regex: str, error_text: str) -> float:
        """Calculate confidence score for pattern match"""
        matches = re.findall(pattern_regex, error_text, re.IGNORECASE)
        if not matches:
            return 0.0
        
        # Simple confidence based on match length and specificity
        match_length = sum(len(match) for match in matches)
        text_length = len(error_text)
        
        return min(1.0, match_length / text_length * 2)
    
    async def find_related_errors(self, pattern: ErrorPattern) -> List[str]:
        """Find related error patterns using similarity analysis"""
        related = []
        
        for hash_key, existing_pattern in self.patterns_cache.items():
            if hash_key == pattern.pattern_hash:
                continue
            
            # Check for similarity in error type, service, or context
            similarity_score = self.calculate_similarity(pattern, existing_pattern)
            
            if similarity_score > 0.6:
                related.append(hash_key)
        
        return related[:5]  # Limit to top 5 related errors
    
    def calculate_similarity(self, pattern1: ErrorPattern, pattern2: ErrorPattern) -> float:
        """Calculate similarity between two error patterns"""
        score = 0.0
        
        # Same service
        if pattern1.service == pattern2.service:
            score += 0.3
        
        # Same error type
        if pattern1.error_type == pattern2.error_type:
            score += 0.4
        
        # Similar context
        if pattern1.context in pattern2.context or pattern2.context in pattern1.context:
            score += 0.2
        
        # Similar message (basic text similarity)
        common_words = set(pattern1.message.lower().split()) & set(pattern2.message.lower().split())
        if common_words:
            word_similarity = len(common_words) / max(len(pattern1.message.split()), len(pattern2.message.split()))
            score += word_similarity * 0.1
        
        return min(1.0, score)
    
    async def update_error_guide(self, new_patterns: List[ErrorPattern]):
        """Update the ERROR_PREVENTION_GUIDE.md with new patterns"""
        if not self.error_guide_path.exists():
            print("Error guide not found, creating new one...")
            await self.create_initial_guide()
        
        # Read current guide
        async with aiofiles.open(self.error_guide_path, 'r', encoding='utf-8') as f:
            guide_content = await f.read()
        
        # Generate new error entries
        new_entries = []
        for pattern in new_patterns:
            if pattern.auto_suggested_solution:
                entry = await self.generate_error_entry(pattern)
                new_entries.append(entry)
        
        if new_entries:
            # Find insertion point (before the last section)
            insertion_point = guide_content.rfind("\n## 🤝 Contributing")
            if insertion_point == -1:
                insertion_point = len(guide_content)
            
            # Insert new entries
            new_section = f"\n\n## 🤖 Auto-Discovered Errors\n\n" + "\n\n".join(new_entries)
            updated_content = guide_content[:insertion_point] + new_section + guide_content[insertion_point:]
            
            # Write updated guide
            async with aiofiles.open(self.error_guide_path, 'w', encoding='utf-8') as f:
                await f.write(updated_content)
            
            print(f"📝 Added {len(new_entries)} new errors to guide")
    
    async def generate_error_entry(self, pattern: ErrorPattern) -> str:
        """Generate formatted error entry for the guide"""
        error_id = f"ERROR-AUTO-{pattern.pattern_hash[:8].upper()}"
        
        entry = f"""### {error_id}: {pattern.error_type} in {pattern.service}

**Error Message:** `{pattern.message}`

**Context:** {pattern.context}

**Severity:** {pattern.severity.upper()}

**Auto-Generated Solution:**
{pattern.auto_suggested_solution}

**Prevention Tips:**"""
        
        for tip in pattern.prevention_tips:
            entry += f"\n- {tip}"
        
        entry += f"""

**Occurrence Count:** {pattern.occurrence_count}
**First Seen:** {pattern.first_seen}
**Confidence Score:** {pattern.confidence_score:.2f}

**Quick Commands:**
```bash
# Check service status
docker ps | grep {pattern.service}

# View service logs  
docker logs polished-manual-app-builder-{pattern.service}-1

# Restart service if needed
docker compose restart {pattern.service}
```"""
        
        return entry
    
    async def clear_file(self, file_path: Path):
        """Clear contents of a file"""
        async with aiofiles.open(file_path, 'w') as f:
            await f.write("")
    
    async def create_initial_guide(self):
        """Create initial error guide if it doesn't exist"""
        initial_content = """# Error Prevention Guide

This guide is automatically updated with new error patterns and solutions.

## 🎯 Overview

This document serves as both an error prevention guide and a comprehensive error log for the Polished Manual App Builder project.
"""
        
        self.error_guide_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.error_guide_path, 'w') as f:
            await f.write(initial_content)


class ErrorAnalytics:
    """Analytics for error patterns and trends"""
    
    def __init__(self, learning_engine: ErrorLearningEngine):
        self.engine = learning_engine
    
    async def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        patterns = self.engine.patterns_cache.values()
        
        # Basic statistics
        total_patterns = len(patterns)
        resolved_patterns = sum(1 for p in patterns if p.resolved)
        resolution_rate = resolved_patterns / total_patterns if total_patterns > 0 else 0
        
        # Severity distribution
        severity_counts = Counter(p.severity for p in patterns)
        
        # Service distribution
        service_counts = Counter(p.service for p in patterns)
        
        # Most common errors
        common_errors = Counter(p.error_type for p in patterns).most_common(10)
        
        # Recent trends (last 7 days)
        recent_date = datetime.now() - timedelta(days=7)
        recent_patterns = [
            p for p in patterns 
            if datetime.fromisoformat(p.last_seen.replace('Z', '+00:00')) > recent_date
        ]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_error_patterns": total_patterns,
                "resolved_patterns": resolved_patterns,
                "resolution_rate": resolution_rate,
                "recent_patterns_7d": len(recent_patterns)
            },
            "severity_distribution": dict(severity_counts),
            "service_distribution": dict(service_counts),
            "common_error_types": common_errors,
            "recent_activity": len(recent_patterns),
            "auto_solution_coverage": sum(1 for p in patterns if p.auto_suggested_solution) / total_patterns if total_patterns > 0 else 0
        }


async def main():
    """Main function to run the error learning system"""
    engine = ErrorLearningEngine()
    analytics = ErrorAnalytics(engine)
    
    # Run learning cycle
    await engine.analyze_and_learn()
    
    # Generate analytics report
    report = await analytics.generate_analytics_report()
    
    # Save analytics report
    report_path = Path("logs/errors/analytics_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiofiles.open(report_path, 'w') as f:
        await f.write(json.dumps(report, indent=2, default=str))
    
    print("📊 Analytics report generated")
    print(f"   Total patterns: {report['summary']['total_error_patterns']}")
    print(f"   Resolution rate: {report['summary']['resolution_rate']:.1%}")
    print(f"   Auto-solution coverage: {report['auto_solution_coverage']:.1%}")

if __name__ == "__main__":
    asyncio.run(main())
