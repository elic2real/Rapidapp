#!/usr/bin/env python3
"""
Next-Generation AI-Powered Debugging System
Advanced LLM integration with autonomous problem-solving capabilities
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from collections import defaultdict
import hashlib
import traceback

# Conditional imports with graceful fallbacks
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    aiohttp = None
    HAS_AIOHTTP = False
    print("⚠️ aiohttp not available - some async features disabled")

try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:
    aiofiles = None
    HAS_AIOFILES = False
    print("⚠️ aiofiles not available - async file operations disabled")

# Import canonical utilities
from utils import (
    print_once, safe_subprocess_run, validate_input, 
    clamp_value, safe_round, mask_sensitive_data
)

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelTier(Enum):
    """Model tier classifications for intelligent routing"""
    LIGHTWEIGHT = "lightweight"  # Fast responses, simple queries
    BALANCED = "balanced"        # General debugging, code analysis
    HEAVYWEIGHT = "heavyweight"  # Complex reasoning, architecture decisions
    SPECIALIZED = "specialized"  # Code-specific tasks

class TaskComplexity(Enum):
    """Task complexity levels for model selection"""
    SIMPLE = 1      # Basic syntax errors, imports
    MEDIUM = 2      # Logic errors, configuration issues
    COMPLEX = 3     # Architecture problems, performance issues
    EXPERT = 4      # System design, advanced optimization

@dataclass
class ErrorContext:
    """Rich error context for comprehensive analysis"""
    error_type: str
    error_message: str
    stack_trace: str
    file_path: str
    line_number: int
    function_name: str
    code_context: List[str]
    environment_info: Dict[str, Any]
    related_files: List[str]
    dependency_info: Dict[str, Any]
    system_metrics: Dict[str, Any]
    timestamp: str

@dataclass
class DebugSolution:
    """Structured debugging solution"""
    analysis: str
    hypothesis: List[str]
    solution_steps: List[str]
    prevention_tips: List[str]
    diagnostic_commands: List[str]
    confidence_score: float
    estimated_time: str
    risk_level: str
    validation_tests: List[str]
    rollback_plan: List[str]

class IntelligentLLMRouter:
    """Advanced LLM router with multi-provider support and intelligent model selection"""
    
    def __init__(self):
        self.providers = {
            'ollama_local': {
                'models': {
                    'llama3.2:latest': {'tier': ModelTier.BALANCED, 'context': 8192},
                    'mixtral:latest': {'tier': ModelTier.HEAVYWEIGHT, 'context': 32768},
                    'phi3:mini': {'tier': ModelTier.LIGHTWEIGHT, 'context': 4096},
                    'codellama:34b': {'tier': ModelTier.SPECIALIZED, 'context': 16384},
                    'deepseek-coder': {'tier': ModelTier.SPECIALIZED, 'context': 16384}
                },
                'latency': 'low',
                'cost': 0.0,
                'privacy': 'maximum',
                'availability': 'high',
                'base_url': 'http://127.0.0.1:11434'
            },
            'openai_api': {
                'models': {
                    'gpt-4': {'tier': ModelTier.HEAVYWEIGHT, 'context': 8192},
                    'gpt-3.5-turbo': {'tier': ModelTier.BALANCED, 'context': 4096}
                },
                'latency': 'medium',
                'cost': 0.02,  # per 1k tokens
                'capabilities': 'maximum',
                'fallback_priority': 1
            },
            'anthropic_claude': {
                'models': {
                    'claude-3-opus': {'tier': ModelTier.HEAVYWEIGHT, 'context': 100000},
                    'claude-3-sonnet': {'tier': ModelTier.BALANCED, 'context': 100000}
                },
                'reasoning': 'excellent',
                'safety': 'high',
                'fallback_priority': 2
            }
        }
        
        self.usage_stats = defaultdict(lambda: {'requests': 0, 'successes': 0, 'avg_latency': 0})
        self.model_performance = defaultdict(lambda: {'accuracy': 0.0, 'speed': 0.0})
    
    async def route_request(
        self, 
        task_type: str, 
        complexity: TaskComplexity, 
        privacy_level: str = "high",
        budget: float = 0.0,
        context_size: int = 4096
    ) -> Dict[str, Any]:
        """Intelligently route requests to optimal model/provider"""
        
        # Determine required model tier
        tier_mapping = {
            TaskComplexity.SIMPLE: ModelTier.LIGHTWEIGHT,
            TaskComplexity.MEDIUM: ModelTier.BALANCED,
            TaskComplexity.COMPLEX: ModelTier.HEAVYWEIGHT,
            TaskComplexity.EXPERT: ModelTier.SPECIALIZED
        }
        
        required_tier = tier_mapping[complexity]
        
        # Filter providers based on requirements
        suitable_providers = []
        
        for provider_name, provider_config in self.providers.items():
            # Check privacy requirements
            if privacy_level == "maximum" and provider_name != "ollama_local":
                continue
            
            # Check budget constraints
            if budget > 0 and provider_config.get('cost', 0) > budget:
                continue
            
            # Find suitable models in this provider
            for model_name, model_config in provider_config.get('models', {}).items():
                if (model_config['tier'] == required_tier and 
                    model_config['context'] >= context_size):
                    
                    suitable_providers.append({
                        'provider': provider_name,
                        'model': model_name,
                        'config': provider_config,
                        'model_config': model_config
                    })
        
        if not suitable_providers:
            # Fallback to best available
            return await self._get_fallback_provider(complexity)
        
        # Select best provider based on performance metrics
        best_provider = self._select_optimal_provider(suitable_providers)
        
        return best_provider
    
    def _select_optimal_provider(self, providers: List[Dict]) -> Dict[str, Any]:
        """Select optimal provider based on performance metrics"""
        scored_providers = []
        
        for provider in providers:
            provider_name = provider['provider']
            model_name = provider['model']
            
            stats = self.usage_stats[f"{provider_name}:{model_name}"]
            performance = self.model_performance[f"{provider_name}:{model_name}"]
            
            # Calculate composite score
            success_rate = stats['successes'] / max(stats['requests'], 1)
            accuracy_score = performance['accuracy']
            speed_score = 1 / max(stats['avg_latency'], 0.1)
            
            composite_score = (success_rate * 0.4 + accuracy_score * 0.4 + speed_score * 0.2)
            
            scored_providers.append((composite_score, provider))
        
        # Sort by score and return best
        scored_providers.sort(key=lambda x: x[0], reverse=True)
        return scored_providers[0][1] if scored_providers else providers[0]
    
    async def _get_fallback_provider(self, complexity: TaskComplexity) -> Dict[str, Any]:
        """Get fallback provider when no exact match found"""
        # Default to local Ollama for privacy
        return {
            'provider': 'ollama_local',
            'model': 'llama3.2:latest',
            'config': self.providers['ollama_local'],
            'model_config': self.providers['ollama_local']['models']['llama3.2:latest']
        }

class TreeOfThoughtsDebugger:
    """Implements Tree of Thoughts reasoning for complex debugging"""
    
    def __init__(self, llm_router: IntelligentLLMRouter):
        self.llm_router = llm_router
        self.max_depth = 3
        self.max_branches = 3
    
    async def solve_complex_error(self, error_context: ErrorContext) -> DebugSolution:
        """Solve complex errors using Tree of Thoughts methodology"""
        
        # Generate initial thought trees
        thought_trees = await self._generate_thought_trees(error_context)
        
        # Evaluate each path
        evaluations = []
        for tree in thought_trees:
            evaluation = await self._evaluate_thought_path(tree, error_context)
            evaluations.append(evaluation)
        
        # Select best path
        best_solution = self._select_optimal_solution(evaluations)
        
        # Validate solution
        validation_result = await self._validate_solution(best_solution, error_context)
        
        if validation_result['success']:
            return best_solution
        else:
            # Iterate with new constraints
            return await self._iterate_with_feedback(error_context, validation_result)
    
    async def _generate_thought_trees(self, error_context: ErrorContext) -> List[Dict]:
        """Generate multiple reasoning paths"""
        trees = []
        
        # Generate different hypothesis approaches
        approaches = [
            "root_cause_analysis",
            "pattern_matching", 
            "dependency_analysis",
            "environment_analysis"
        ]
        
        for approach in approaches:
            tree = await self._build_thought_tree(error_context, approach, 0)
            trees.append(tree)
        
        return trees
    
    async def _build_thought_tree(
        self, 
        error_context: ErrorContext, 
        approach: str, 
        depth: int
    ) -> Dict:
        """Build individual thought tree recursively"""
        
        if depth >= self.max_depth:
            return {'approach': approach, 'depth': depth, 'conclusion': 'max_depth_reached'}
        
        # Generate thoughts for this approach
        prompt = self._create_tree_prompt(error_context, approach, depth)
        
        provider = await self.llm_router.route_request(
            task_type="complex_debugging",
            complexity=TaskComplexity.COMPLEX,
            privacy_level="high"
        )
        
        response = await self._query_llm(prompt, provider)
        
        # Parse response into structured thoughts
        thoughts = self._parse_thought_response(response)
        
        # Build child nodes
        children = []
        for thought in thoughts[:self.max_branches]:
            child = await self._build_thought_tree(error_context, thought, depth + 1)
            children.append(child)
        
        return {
            'approach': approach,
            'depth': depth,
            'thoughts': thoughts,
            'children': children,
            'evaluation_score': 0.0
        }
    
    def _create_tree_prompt(self, error_context: ErrorContext, approach: str, depth: int) -> str:
        """Create prompts for Tree of Thoughts reasoning"""
        
        base_context = f"""
ERROR ANALYSIS - Tree of Thoughts Approach: {approach}
Depth: {depth}

Error: {error_context.error_message}
File: {error_context.file_path}:{error_context.line_number}
Function: {error_context.function_name}

Stack Trace:
{error_context.stack_trace}

Code Context:
{chr(10).join(error_context.code_context)}
"""
        
        approach_prompts = {
            "root_cause_analysis": """
Analyze the ROOT CAUSE of this error. Generate 3 distinct hypotheses:
1. What could have caused this error at the fundamental level?
2. What are the underlying system conditions that led to this?
3. What architectural decisions might have contributed?

For each hypothesis, provide:
- Probability estimate (0-100%)
- Supporting evidence from the context
- Specific validation test to prove/disprove
""",
            
            "pattern_matching": """
PATTERN MATCHING approach. Identify patterns similar to known errors:
1. What error patterns does this match in common debugging knowledge?
2. What similar issues have been solved before?
3. What are the typical solutions for this pattern?

Focus on:
- Error signature analysis
- Common occurrence contexts
- Standard resolution approaches
""",
            
            "dependency_analysis": """
DEPENDENCY ANALYSIS approach. Examine the dependency chain:
1. What dependencies could be causing this error?
2. How might version conflicts or missing packages contribute?
3. What environmental factors could be involved?

Analyze:
- Import chains and module dependencies
- Version compatibility issues
- Environment configuration problems
""",
            
            "environment_analysis": """
ENVIRONMENT ANALYSIS approach. Focus on system and runtime environment:
1. What environmental factors could cause this error?
2. How might platform differences contribute?
3. What runtime conditions could lead to this failure?

Consider:
- Platform-specific behaviors
- Runtime configuration
- Resource availability and limits
"""
        }
        
        return base_context + approach_prompts.get(approach, approach_prompts["root_cause_analysis"])

class ReActDebugger:
    """Implements ReAct (Reasoning + Acting) pattern for autonomous debugging"""
    
    def __init__(self, llm_router: IntelligentLLMRouter):
        self.llm_router = llm_router
        self.max_iterations = 10
        self.action_executor = DebugActionExecutor()
    
    async def autonomous_debug(self, error_context: ErrorContext) -> DebugSolution:
        """Autonomous debugging using ReAct pattern"""
        
        current_state = {
            'error_context': error_context,
            'observations': [],
            'hypotheses': [],
            'actions_taken': [],
            'iteration': 0,
            'solved': False
        }
        
        while not current_state['solved'] and current_state['iteration'] < self.max_iterations:
            # THINK: Analyze current state
            thought = await self._reason_about_state(current_state)
            
            # ACT: Take concrete action
            action = await self._decide_action(thought, current_state)
            observation = await self._execute_action(action, current_state)
            
            # OBSERVE: Update understanding
            current_state = await self._update_state(observation, current_state)
            
            # REFLECT: Learn from results
            reflection = await self._reflect_on_outcome(action, observation, current_state)
            
            current_state['iteration'] += 1
            
            # Check if problem is solved
            if self._is_problem_solved(current_state):
                current_state['solved'] = True
        
        return await self._generate_final_solution(current_state)
    
    async def _reason_about_state(self, state: Dict) -> str:
        """Reason about current debugging state"""
        
        prompt = f"""
DEBUGGING STATE ANALYSIS

Current Iteration: {state['iteration']}
Error: {state['error_context'].error_message}

Previous Actions: {len(state['actions_taken'])}
{chr(10).join([f"- {action['type']}: {action['result'][:100]}..." for action in state['actions_taken'][-3:]])}

Current Hypotheses:
{chr(10).join([f"- {h['description']} (confidence: {h['confidence']})" for h in state['hypotheses'][-3:]])}

Recent Observations:
{chr(10).join([f"- {obs['description']}" for obs in state['observations'][-3:]])}

REASONING TASK:
Analyze the current state and determine:
1. What do we know so far?
2. What are the most promising hypotheses?
3. What information are we still missing?
4. What should be our next investigation step?

Provide a structured analysis focusing on the most logical next step.
"""
        
        provider = await self.llm_router.route_request(
            task_type="reasoning",
            complexity=TaskComplexity.MEDIUM
        )
        
        return await self._query_llm(prompt, provider)
    
    async def _decide_action(self, thought: str, state: Dict) -> Dict[str, Any]:
        """Decide on next action based on reasoning"""
        
        available_actions = [
            "examine_code",
            "check_dependencies", 
            "run_diagnostic",
            "test_hypothesis",
            "gather_environment_info",
            "analyze_logs",
            "check_configuration"
        ]
        
        prompt = f"""
ACTION DECISION

Based on this reasoning:
{thought}

Available Actions:
{chr(10).join([f"- {action}" for action in available_actions])}

Choose the MOST APPROPRIATE action and specify:
1. Action type (from available actions)
2. Specific parameters for the action
3. Expected outcome
4. How this will advance our debugging

Respond in JSON format:
{{
    "action_type": "action_name",
    "parameters": {{"key": "value"}},
    "expected_outcome": "description",
    "reasoning": "why this action"
}}
"""
        
        provider = await self.llm_router.route_request(
            task_type="planning",
            complexity=TaskComplexity.MEDIUM
        )
        
        response = await self._query_llm(prompt, provider)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback action
            return {
                "action_type": "examine_code",
                "parameters": {"focus": "error_location"},
                "expected_outcome": "better understanding of error context",
                "reasoning": "fallback action due to parsing error"
            }

class DebugActionExecutor:
    """Executes debugging actions safely"""
    
    def __init__(self):
        self.safe_commands = {
            'examine_code': self._examine_code,
            'check_dependencies': self._check_dependencies,
            'run_diagnostic': self._run_diagnostic,
            'test_hypothesis': self._test_hypothesis,
            'gather_environment_info': self._gather_environment_info,
            'analyze_logs': self._analyze_logs,
            'check_configuration': self._check_configuration
        }
    
    async def execute_action(self, action: Dict[str, Any], context: ErrorContext) -> Dict[str, Any]:
        """Execute a debugging action safely"""
        
        action_type = action.get('action_type')
        parameters = action.get('parameters', {})
        
        if action_type not in self.safe_commands:
            return {
                'success': False,
                'error': f'Unknown action type: {action_type}',
                'result': None
            }
        
        try:
            result = await self.safe_commands[action_type](parameters, context)
            return {
                'success': True,
                'result': result,
                'action': action
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'result': None,
                'action': action
            }
    
    async def _examine_code(self, params: Dict, context: ErrorContext) -> str:
        """Examine code around error location"""
        try:
            file_path = Path(context.file_path)
            if not file_path.exists():
                return f"File not found: {context.file_path}"
            
            # Use conditional aiofiles or fallback to sync
            if HAS_AIOFILES and aiofiles:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    lines = await f.readlines()
            else:
                # Fallback to sync file reading
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            start_line = max(0, context.line_number - 10)
            end_line = min(len(lines), context.line_number + 10)
            
            code_snippet = []
            for i in range(start_line, end_line):
                marker = ">>> " if i == context.line_number - 1 else "    "
                code_snippet.append(f"{i+1:3d}:{marker}{lines[i].rstrip()}")
            
            return "\n".join(code_snippet)
            
        except Exception as e:
            return f"Error examining code: {e}"
    
    async def _check_dependencies(self, params: Dict, context: ErrorContext) -> str:
        """Check Python dependencies"""
        try:
            result = safe_subprocess_run(['pip', 'list'], timeout=30)
            if result and result.stdout:
                return result.stdout
            return "Error: Could not retrieve pip list"
        except Exception as e:
            print_once(f"Error checking dependencies: {e}", "ERROR")
            return f"Error checking dependencies: {e}"
    
    async def _run_diagnostic(self, params: Dict, context: ErrorContext) -> str:
        """Run diagnostic commands"""
        diagnostic_type = params.get('type', 'general')
        
        diagnostics = {
            'network': [['ping', 'localhost']],
            'database': [['python', '-c', 'print("Database check")']],
            'imports': [['python', '-c', 'import sys; print(len(sys.path))']],
            'general': [['python', '--version']]
        }
        
        commands = diagnostics.get(diagnostic_type, diagnostics['general'])
        results = []
        
        for cmd in commands:
            try:
                result = safe_subprocess_run(cmd, timeout=10)
                if result:
                    cmd_str = ' '.join(cmd)
                    results.append(f"Command: {cmd_str}")
                    if result.stdout:
                        results.append(f"Output: {result.stdout.strip()}")
                    if result.stderr:
                        results.append(f"Error: {result.stderr.strip()}")
                else:
                    results.append(f"Command failed: {' '.join(cmd)}")
            except Exception as e:
                print_once(f"Error running diagnostic: {e}", "ERROR")
                results.append(f"Error: {e}")
        
        return '\n'.join(results)
    
    async def _test_hypothesis(self, params: Dict, context: ErrorContext) -> str:
        """Test a specific hypothesis"""
        hypothesis = params.get('hypothesis', '')
        test_type = params.get('test_type', 'code_execution')
        
        if test_type == 'code_execution':
            test_code = params.get('code', 'print("No test code provided")')
            try:
                # Execute test code safely
                import subprocess
                result = subprocess.run(
                    ['python', '-c', test_code], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                return f"Hypothesis: {hypothesis}\nTest Result: {result.stdout}\nErrors: {result.stderr}"
            except Exception as e:
                return f"Hypothesis test failed: {e}"
        
        return f"Hypothesis logged: {hypothesis}"
    
    async def _gather_environment_info(self, params: Dict, context: ErrorContext) -> str:
        """Gather environment information"""
        import platform
        import sys
        import os
        
        info = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'working_directory': os.getcwd(),
            'environment_variables': dict(os.environ),
            'path': sys.path
        }
        
        # Filter sensitive environment variables
        sensitive_vars = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']
        filtered_env = {
            k: v for k, v in info['environment_variables'].items()
            if not any(sensitive in k.upper() for sensitive in sensitive_vars)
        }
        info['environment_variables'] = filtered_env
        
        return json.dumps(info, indent=2)
    
    async def _analyze_logs(self, params: Dict, context: ErrorContext) -> str:
        """Analyze log files"""
        log_paths = params.get('paths', ['error_monitor.log', 'ai_debug.log'])
        results = []
        
        for log_path in log_paths:
            try:
                log_file = Path(log_path)
                if log_file.exists():
                    async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    # Get last 20 lines
                    lines = content.split('\n')
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    results.append(f"Log: {log_path}\n{chr(10).join(recent_lines)}")
                else:
                    results.append(f"Log not found: {log_path}")
            except Exception as e:
                results.append(f"Error reading log {log_path}: {e}")
        
        return "\n\n".join(results)
    
    async def _check_configuration(self, params: Dict, context: ErrorContext) -> str:
        """Check configuration files"""
        config_files = params.get('files', ['config.py', 'settings.py', '.env'])
        results = []
        
        for config_file in config_files:
            try:
                config_path = Path(config_file)
                if config_path.exists():
                    async with aiofiles.open(config_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    # Mask sensitive data
                    masked_content = self._mask_sensitive_data(content)
                    results.append(f"Config: {config_file}\n{masked_content}")
                else:
                    results.append(f"Config not found: {config_file}")
            except Exception as e:
                results.append(f"Error reading config {config_file}: {e}")
        
        return "\n\n".join(results)
    
    def _mask_sensitive_data(self, content: str) -> str:
        """Mask sensitive data in configuration"""
        # Mask common sensitive patterns
        patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', r'password = "***MASKED***"'),
            (r'secret\s*=\s*["\']([^"\']+)["\']', r'secret = "***MASKED***"'),
            (r'key\s*=\s*["\']([^"\']+)["\']', r'key = "***MASKED***"'),
            (r'token\s*=\s*["\']([^"\']+)["\']', r'token = "***MASKED***"')
        ]
        
        masked_content = content
        for pattern, replacement in patterns:
            masked_content = re.sub(pattern, replacement, masked_content, flags=re.IGNORECASE)
        
        return masked_content

class NextGenAIDebugger:
    """Main orchestrator for the next-generation AI debugging system"""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logs_dir = self.project_root / "logs" / "ai_debug"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.llm_router = IntelligentLLMRouter()
        self.tree_debugger = TreeOfThoughtsDebugger(self.llm_router)
        self.react_debugger = ReActDebugger(self.llm_router)
        self.action_executor = DebugActionExecutor()
        
        # Performance tracking
        self.session_stats = {
            'start_time': datetime.now(),
            'errors_processed': 0,
            'solutions_generated': 0,
            'success_rate': 0.0
        }
    
    async def analyze_error(self, error_info: Dict[str, Any], approach: str = "auto") -> DebugSolution:
        """Main entry point for error analysis"""
        
        # Create rich error context
        error_context = await self._create_error_context(error_info)
        
        # Determine approach based on complexity
        if approach == "auto":
            approach = self._determine_optimal_approach(error_context)
        
        # Route to appropriate debugging method
        if approach == "tree_of_thoughts":
            solution = await self.tree_debugger.solve_complex_error(error_context)
        elif approach == "react":
            solution = await self.react_debugger.autonomous_debug(error_context)
        else:
            solution = await self._traditional_analysis(error_context)
        
        # Post-process and validate solution
        final_solution = await self._post_process_solution(solution, error_context)
        
        # Update statistics
        self.session_stats['errors_processed'] += 1
        if final_solution.confidence_score > 0.7:
            self.session_stats['solutions_generated'] += 1
        
        self.session_stats['success_rate'] = (
            self.session_stats['solutions_generated'] / 
            max(self.session_stats['errors_processed'], 1)
        )
        
        # Save analysis results
        await self._save_analysis_results(error_context, final_solution)
        
        return final_solution
    
    async def _create_error_context(self, error_info: Dict[str, Any]) -> ErrorContext:
        """Create comprehensive error context"""
        
        # Extract basic error information
        error_type = error_info.get('error_type', 'Unknown')
        error_message = error_info.get('error_message', 'No message provided')
        stack_trace = error_info.get('traceback', 'No traceback available')
        
        # Parse stack trace for file/line info
        file_path, line_number, function_name = self._parse_stack_trace(stack_trace)
        
        # Get code context
        code_context = await self._get_code_context(file_path, line_number)
        
        # Gather environment info
        environment_info = await self._gather_comprehensive_environment()
        
        # Find related files
        related_files = await self._find_related_files(file_path, error_type)
        
        # Get dependency information
        dependency_info = await self._analyze_dependencies()
        
        # Collect system metrics
        system_metrics = await self._collect_system_metrics()
        
        return ErrorContext(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            code_context=code_context,
            environment_info=environment_info,
            related_files=related_files,
            dependency_info=dependency_info,
            system_metrics=system_metrics,
            timestamp=datetime.now().isoformat()
        )
    
    def _determine_optimal_approach(self, error_context: ErrorContext) -> str:
        """Determine the best debugging approach for this error"""
        
        # Analyze error characteristics
        complexity_score = self._calculate_complexity_score(error_context)
        
        if complexity_score > 8:
            return "tree_of_thoughts"  # Most complex errors
        elif complexity_score > 5:
            return "react"  # Medium complexity, needs investigation
        else:
            return "traditional"  # Simple errors
    
    def _calculate_complexity_score(self, error_context: ErrorContext) -> int:
        """Calculate complexity score (1-10) based on error characteristics"""
        score = 0
        
        # Stack trace depth
        stack_depth = len(error_context.stack_trace.split('\n'))
        score += min(stack_depth // 10, 3)
        
        # Error type complexity
        complex_types = ['AttributeError', 'TypeError', 'RuntimeError', 'SystemError']
        if error_context.error_type in complex_types:
            score += 2
        
        # File complexity (number of related files)
        score += min(len(error_context.related_files) // 5, 2)
        
        # Environment complexity
        if len(error_context.environment_info) > 10:
            score += 1
        
        # Dependency complexity
        if len(error_context.dependency_info) > 20:
            score += 1
        
        # System resource issues
        cpu_usage = error_context.system_metrics.get('cpu_percent', 0)
        memory_usage = error_context.system_metrics.get('memory_percent', 0)
        if cpu_usage > 80 or memory_usage > 80:
            score += 1
        
        return min(score, 10)
    
    async def _traditional_analysis(self, error_context: ErrorContext) -> DebugSolution:
        """Traditional LLM-based error analysis for simpler issues"""
        
        prompt = self._create_traditional_prompt(error_context)
        
        provider = await self.llm_router.route_request(
            task_type="error_analysis",
            complexity=TaskComplexity.MEDIUM,
            privacy_level="high"
        )
        
        response = await self._query_llm(prompt, provider)
        
        # Parse response into structured solution
        return self._parse_solution_response(response)
    
    def _create_traditional_prompt(self, error_context: ErrorContext) -> str:
        """Create comprehensive prompt for traditional analysis"""
        
        return f"""# EXPERT DEBUGGING SYSTEM v2.0

## ROLE DEFINITION
You are an elite software debugging specialist with 20+ years experience.

## ERROR ANALYSIS FRAMEWORK

### ERROR DETAILS
- **Type**: {error_context.error_type}
- **Message**: {error_context.error_message}
- **File**: {error_context.file_path}:{error_context.line_number}
- **Function**: {error_context.function_name}

### STACK TRACE
```
{error_context.stack_trace}
```

### CODE CONTEXT
```python
{chr(10).join(error_context.code_context)}
```

### ENVIRONMENT
- **Platform**: {error_context.environment_info.get('platform', 'Unknown')}
- **Python**: {error_context.environment_info.get('python_version', 'Unknown')}
- **Dependencies**: {len(error_context.dependency_info)} packages

### SYSTEM METRICS
- **CPU**: {error_context.system_metrics.get('cpu_percent', 0)}%
- **Memory**: {error_context.system_metrics.get('memory_percent', 0)}%

## REQUIRED OUTPUT FORMAT (JSON)
```json
{{
  "analysis": "Root cause analysis",
  "hypotheses": [
    {{
      "description": "Primary hypothesis",
      "probability": 0.8,
      "supporting_evidence": ["evidence1", "evidence2"],
      "validation_tests": ["test1", "test2"]
    }}
  ],
  "solution_steps": [
    "Step 1: Specific action",
    "Step 2: Another action"
  ],
  "prevention_tips": ["tip1", "tip2"],
  "diagnostic_commands": ["cmd1", "cmd2"],
  "confidence_score": 0.85,
  "estimated_time": "15 minutes",
  "risk_level": "low",
  "validation_tests": ["validation1"],
  "rollback_plan": ["rollback1"]
}}
```

Execute comprehensive analysis and provide expert debugging solution.
"""
    
    async def _query_llm(self, prompt: str, provider: Dict[str, Any]) -> str:
        """Query LLM with the provided prompt"""
        
        provider_name = provider['provider']
        model_name = provider['model']
        
        if provider_name == 'ollama_local':
            return await self._query_ollama(prompt, model_name, provider['config'])
        elif provider_name == 'openai_api':
            return await self._query_openai(prompt, model_name)
        elif provider_name == 'anthropic_claude':
            return await self._query_claude(prompt, model_name)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    async def _query_ollama(self, prompt: str, model: str, config: Dict) -> str:
        """Query local Ollama installation"""
        
        base_url = config.get('base_url', 'http://127.0.0.1:11434')
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent debugging
                "top_p": 0.9
            }
        }
        
        timeout_strategies = [60, 120, 300]  # Progressive timeouts for complex analysis
        
        for timeout in timeout_strategies:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    async with session.post(f"{base_url}/api/chat", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["message"]["content"]
                        else:
                            error_text = await response.text()
                            logger.error(f"Ollama HTTP {response.status}: {error_text}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Ollama timeout after {timeout}s, trying longer timeout...")
                continue
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                break
        
        raise Exception("Failed to get response from Ollama after multiple attempts")
    
    async def _save_analysis_results(self, error_context: ErrorContext, solution: DebugSolution):
        """Save comprehensive analysis results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"debug_analysis_{timestamp}.json"
        filepath = self.logs_dir / filename
        
        analysis_data = {
            'timestamp': timestamp,
            'error_context': asdict(error_context),
            'solution': asdict(solution),
            'session_stats': self.session_stats
        }
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(analysis_data, indent=2, default=str))
        
        logger.info(f"Analysis results saved to: {filepath}")

# Convenience functions and decorators
async def ai_debug_error(error_info: Dict[str, Any], approach: str = "auto") -> DebugSolution:
    """Convenience function for AI debugging"""
    debugger = NextGenAIDebugger()
    return await debugger.analyze_error(error_info, approach)

def ai_debug_decorator(approach: str = "auto"):
    """Decorator for automatic AI debugging of function errors"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                error_info = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc(),
                    'function_name': func.__name__,
                    'arguments': {'args': args, 'kwargs': kwargs}
                }
                
                solution = await ai_debug_error(error_info, approach)
                
                logger.info(f"AI Debug Solution: {solution.analysis}")
                logger.info(f"Confidence: {solution.confidence_score}")
                
                raise  # Re-raise original exception
        
        return wrapper
    return decorator

# CLI interface
async def main():
    """CLI interface for the AI debugging system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Next-Generation AI Debugging System')
    parser.add_argument('--error', '-e', help='Error message to analyze')
    parser.add_argument('--file', '-f', help='Python file with error')
    parser.add_argument('--line', '-l', type=int, help='Line number of error')
    parser.add_argument('--approach', '-a', choices=['auto', 'tree_of_thoughts', 'react', 'traditional'], 
                       default='auto', help='Debugging approach')
    parser.add_argument('--test', '-t', action='store_true', help='Test with sample error')
    
    args = parser.parse_args()
    
    debugger = NextGenAIDebugger()
    
    if args.test:
        # Test with sample error
        error_info = {
            'error_type': 'HTTPConnectionError',
            'error_message': 'HTTPConnectionPool(host="localhost", port=8000): Read timed out',
            'traceback': 'Traceback (most recent call last):\n  File "test.py", line 10, in test_function\n    response = requests.get("http://localhost:8000")\nHTTPConnectionError: Read timed out',
            'function_name': 'test_function'
        }
        
        solution = await debugger.analyze_error(error_info, args.approach)
        
        print(f"\n🤖 AI Debug Solution:")
        print(f"Analysis: {solution.analysis}")
        print(f"Confidence: {solution.confidence_score}")
        print(f"Steps: {solution.solution_steps}")
        
    elif args.error:
        error_info = {
            'error_type': 'Unknown',
            'error_message': args.error,
            'traceback': f'Error in {args.file or "unknown"}:{args.line or 0}',
            'function_name': 'unknown'
        }
        
        solution = await debugger.analyze_error(error_info, args.approach)
        
        print(f"\n🤖 AI Debug Solution:")
        print(f"Analysis: {solution.analysis}")
        print(f"Confidence: {solution.confidence_score}")
        
    else:
        print("🤖 Next-Generation AI Debugging System")
        print("Use --error to analyze an error message")
        print("Use --test to test with sample error")
        print("Use @ai_debug_decorator for automatic debugging")

if __name__ == "__main__":
    asyncio.run(main())
