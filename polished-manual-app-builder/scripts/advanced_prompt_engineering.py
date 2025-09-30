#!/usr/bin/env python3
"""
Advanced Prompt Engineering Framework for AI Debugging
Implements sophisticated prompting techniques for optimal debugging results
"""

import json
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class PromptType(Enum):
    """Types of prompts for different debugging scenarios"""
    ERROR_ANALYSIS = "error_analysis"
    CODE_REVIEW = "code_review" 
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    SOLUTION_DESIGN = "solution_design"
    PATTERN_RECOGNITION = "pattern_recognition"
    PREVENTION_STRATEGY = "prevention_strategy"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT_REASONING = "react_reasoning"

class ExpertiseLevel(Enum):
    """Expertise levels for role-based prompting"""
    JUNIOR = "junior"
    SENIOR = "senior"
    ARCHITECT = "architect"
    SPECIALIST = "specialist"

@dataclass
class PromptContext:
    """Context information for prompt generation"""
    error_type: str
    complexity_level: int
    domain: str
    tech_stack: List[str]
    urgency: str
    privacy_level: str
    user_expertise: ExpertiseLevel

class AdvancedPromptEngineer:
    """Advanced prompt engineering system with multiple techniques"""
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path("scripts/ai_debug_config.json")
        self.config = self._load_config()
        
        # Master prompt templates
        self.prompt_templates = self._initialize_prompt_templates()
        
        # Dynamic prompt components
        self.role_definitions = self._load_role_definitions()
        self.framework_templates = self._load_framework_templates()
        self.expertise_modifiers = self._load_expertise_modifiers()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration for prompt engineering"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for prompt engineering"""
        return {
            "ai_debug_config": {
                "prompt_engineering": {
                    "max_context_length": 8000,
                    "temperature": 0.7,
                    "model_preferences": ["gpt-4", "claude-3", "gemini-pro"],
                    "fallback_enabled": True
                }
            }
        }
    
    def _load_role_definitions(self) -> Dict[str, str]:
        """Load role definitions for prompt engineering"""
        return {
            "debugger": "Expert code debugger with deep Python knowledge and systematic problem-solving approach",
            "analyst": "Systematic problem analyzer who breaks down complex issues into manageable components", 
            "fixer": "Solution implementer focused on best practices and robust code quality",
            "teacher": "Patient explainer who makes complex concepts accessible for learning",
            "architect": "System designer who considers scalability, maintainability, and performance",
            "security_expert": "Security specialist focused on identifying and preventing vulnerabilities"
        }
    
    def _load_framework_templates(self) -> Dict[str, str]:
        """Load framework-specific prompt templates"""
        return {
            "tree_of_thoughts": """
Using Tree of Thoughts reasoning:
1. Generate multiple hypotheses for the problem
2. Evaluate each hypothesis systematically  
3. Explore the most promising paths
4. Synthesize the best solution
""",
            "react": """
Using ReAct (Reasoning + Acting) framework:
1. Reason about the current situation
2. Act on the reasoning with specific steps
3. Observe the results
4. Iterate until solution is found
""",
            "chain_of_thought": """
Using Chain of Thought reasoning:
1. Break down the problem step-by-step
2. Show intermediate reasoning steps
3. Build logical progression to solution
4. Verify each step before proceeding
"""
        }
    
    def _load_expertise_modifiers(self) -> Dict[str, str]:
        """Load expertise level modifiers for prompts"""
        return {
            "beginner": "Explain concepts simply with examples and avoid technical jargon",
            "intermediate": "Provide moderate detail with some technical explanations",
            "advanced": "Use technical precision and assume familiarity with concepts",
            "expert": "Focus on edge cases, optimizations, and advanced considerations"
        }
                    "temperature_settings": {
                        "debugging": 0.1,
                        "explanation": 0.3,
                        "creative_problem_solving": 0.7,
                        "code_generation": 0.2
                    },
                    "response_formats": {
                        "structured_json": True,
                        "include_confidence": True,
                        "include_alternatives": True,
                        "include_prevention": True,
                        "include_validation": True
                    }
                }
            }
        }
    
    def create_expert_prompt(
        self,
        prompt_type: PromptType,
        context: PromptContext,
        error_data: Dict[str, Any],
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create expert-level prompts using advanced techniques"""
        
        # Select appropriate template
        template = self.prompt_templates[prompt_type]
        
        # Build role definition
        role = self._build_dynamic_role(context)
        
        # Create structured framework
        framework = self._build_analysis_framework(prompt_type, context)
        
        # Add domain-specific knowledge
        domain_knowledge = self._inject_domain_knowledge(context)
        
        # Build constraints and requirements
        constraints = self._build_constraints(context)
        
        # Create output format specification
        output_format = self._build_output_format(prompt_type, context)
        
        # Assemble the complete prompt
        complete_prompt = template.format(
            role_definition=role,
            analysis_framework=framework,
            domain_knowledge=domain_knowledge,
            constraints=constraints,
            output_format=output_format,
            error_context=self._format_error_context(error_data),
            additional_context=self._format_additional_context(additional_context or {}),
            expertise_level=context.user_expertise.value,
            tech_stack=", ".join(context.tech_stack),
            urgency_level=context.urgency,
            complexity_score=context.complexity_level
        )
        
        return complete_prompt
    
    def _initialize_prompt_templates(self) -> Dict[PromptType, str]:
        """Initialize master prompt templates"""
        return {
            PromptType.ERROR_ANALYSIS: """
# 🤖 EXPERT DEBUGGING SYSTEM v3.0

{role_definition}

## 📊 ANALYSIS FRAMEWORK
{analysis_framework}

## 🧠 DOMAIN EXPERTISE
{domain_knowledge}

## ⚡ CURRENT CONTEXT
**Tech Stack**: {tech_stack}
**Urgency Level**: {urgency_level}
**Complexity Score**: {complexity_score}/10
**User Expertise**: {expertise_level}

## 🔍 ERROR INVESTIGATION
{error_context}

{additional_context}

## 📋 CONSTRAINTS & REQUIREMENTS
{constraints}

## 📤 REQUIRED OUTPUT FORMAT
{output_format}

**Execute comprehensive expert analysis using the framework above.**
""",
            
            PromptType.TREE_OF_THOUGHTS: """
# 🌳 TREE OF THOUGHTS DEBUGGING SYSTEM

{role_definition}

## 🎯 TREE OF THOUGHTS METHODOLOGY
You will explore multiple reasoning paths simultaneously to solve this complex problem.

### PHASE 1: THOUGHT GENERATION
Generate exactly 3 distinct reasoning approaches:
1. **Root Cause Analysis Path**: Focus on fundamental causes
2. **Pattern Recognition Path**: Compare with known error patterns  
3. **System Interaction Path**: Analyze component interactions

### PHASE 2: THOUGHT EVALUATION
For each path, evaluate:
- **Viability Score** (0-10): How likely is this path to succeed?
- **Evidence Strength** (0-10): How much evidence supports this path?
- **Implementation Complexity** (0-10): How difficult to implement?

### PHASE 3: THOUGHT SELECTION
Select the highest-scoring path and elaborate with:
- Detailed step-by-step analysis
- Concrete validation methods
- Alternative approaches if primary fails

{analysis_framework}

## 🔍 PROBLEM CONTEXT
{error_context}

{additional_context}

## 📤 TREE OF THOUGHTS OUTPUT FORMAT
```json
{{
  "thought_paths": [
    {{
      "approach": "root_cause_analysis",
      "reasoning": "detailed reasoning for this path",
      "viability_score": 8,
      "evidence_strength": 7,
      "implementation_complexity": 5,
      "detailed_analysis": "step by step analysis",
      "validation_methods": ["method1", "method2"]
    }}
  ],
  "selected_path": {{
    "approach": "selected approach name",
    "detailed_solution": "comprehensive solution",
    "implementation_steps": ["step1", "step2"],
    "validation_plan": ["validation1", "validation2"],
    "fallback_options": ["option1", "option2"]
  }},
  "confidence_assessment": {{
    "overall_confidence": 0.85,
    "risk_factors": ["factor1", "factor2"],
    "success_probability": 0.90
  }}
}}
```

**Execute Tree of Thoughts analysis now.**
""",
            
            PromptType.REACT_REASONING: """
# 🔄 REACT DEBUGGING SYSTEM (Reasoning + Acting)

{role_definition}

## 🎯 REACT METHODOLOGY
You will alternate between REASONING and ACTING to solve this problem systematically.

### REACT CYCLE STRUCTURE:
1. **THOUGHT**: Analyze the current situation
2. **ACTION**: Decide what to investigate/test next
3. **OBSERVATION**: Process the results
4. **REFLECTION**: Learn from the outcome
5. **REPEAT**: Continue until solved

{analysis_framework}

## 🔍 INITIAL PROBLEM STATE
{error_context}

{additional_context}

## 📋 AVAILABLE ACTIONS
- `examine_code`: Analyze specific code sections
- `run_diagnostic`: Execute diagnostic commands
- `test_hypothesis`: Test a specific theory
- `check_environment`: Investigate system/environment
- `analyze_dependencies`: Check package/module issues
- `review_logs`: Examine log files
- `validate_config`: Check configuration files

## 📤 REACT OUTPUT FORMAT
```json
{{
  "react_cycle": [
    {{
      "step": 1,
      "thought": "Analysis of current situation",
      "action": {{
        "type": "examine_code",
        "parameters": {{"focus": "error_location"}},
        "reasoning": "Why this action"
      }},
      "observation": "What we learned from the action",
      "reflection": "How this changes our understanding"
    }}
  ],
  "final_solution": {{
    "root_cause": "identified root cause",
    "solution_steps": ["step1", "step2"],
    "validation_plan": ["test1", "test2"],
    "prevention_strategy": ["prevent1", "prevent2"]
  }},
  "learning_outcomes": ["learning1", "learning2"]
}}
```

**Begin REACT debugging cycle now.**
""",
            
            PromptType.HYPOTHESIS_GENERATION: """
# 🧪 HYPOTHESIS GENERATION SYSTEM

{role_definition}

## 🎯 HYPOTHESIS GENERATION FRAMEWORK
Generate multiple competing hypotheses about the error cause, ranked by probability.

{analysis_framework}

### HYPOTHESIS CRITERIA:
- **Specificity**: Concrete, testable predictions
- **Falsifiability**: Can be proven wrong with evidence
- **Probability**: Likelihood based on available evidence
- **Scope**: Breadth of explanation provided

## 🔍 ERROR EVIDENCE
{error_context}

{additional_context}

## 📤 HYPOTHESIS OUTPUT FORMAT
```json
{{
  "hypotheses": [
    {{
      "id": "H1",
      "description": "Specific hypothesis description",
      "probability": 0.65,
      "supporting_evidence": ["evidence1", "evidence2"],
      "contradicting_evidence": ["contra1"],
      "test_strategy": "How to test this hypothesis",
      "implications": "What this means if true",
      "solution_approach": "How to fix if confirmed"
    }}
  ],
  "hypothesis_ranking": ["H1", "H2", "H3"],
  "confidence_assessment": {{
    "strongest_hypothesis_confidence": 0.65,
    "evidence_quality": "high|medium|low",
    "additional_data_needed": ["data1", "data2"]
  }}
}}
```

**Generate expert hypotheses now.**
"""
        }
    
    def _build_dynamic_role(self, context: PromptContext) -> str:
        """Build dynamic role definition based on context"""
        
        base_roles = {
            ExpertiseLevel.JUNIOR: "You are a skilled software developer with 2-3 years of experience",
            ExpertiseLevel.SENIOR: "You are a senior software engineer with 8+ years of experience across multiple domains",
            ExpertiseLevel.ARCHITECT: "You are a principal software architect with 15+ years of experience designing complex systems",
            ExpertiseLevel.SPECIALIST: "You are a specialized expert with deep knowledge in specific technical domains"
        }
        
        base_role = base_roles[context.user_expertise]
        
        # Add domain-specific expertise
        domain_expertise = {
            "web_development": "specializing in web applications, API design, and frontend/backend integration",
            "data_science": "with expertise in data analysis, machine learning, and statistical computing",
            "systems_programming": "focused on systems programming, performance optimization, and low-level development",
            "devops": "specializing in infrastructure, deployment, monitoring, and automation",
            "security": "with deep knowledge of cybersecurity, secure coding, and threat assessment"
        }
        
        domain_addon = domain_expertise.get(context.domain, "with broad technical knowledge")
        
        # Add tech stack specific knowledge
        tech_knowledge = f"Your current expertise covers: {', '.join(context.tech_stack)}"
        
        # Add urgency context
        urgency_context = {
            "LOW": "You have time for thorough analysis and comprehensive solutions.",
            "MEDIUM": "You need to balance thoroughness with reasonable response time.",
            "HIGH": "You must provide rapid, actionable solutions while maintaining accuracy.",
            "CRITICAL": "This is a production emergency requiring immediate, safe resolution."
        }
        
        urgency_addon = urgency_context.get(context.urgency, "")
        
        return f"""
## 👨‍💻 EXPERT ROLE DEFINITION

{base_role} {domain_addon}.

{tech_knowledge}

**Expertise Level**: {context.user_expertise.value.title()}
**Domain Focus**: {context.domain.replace('_', ' ').title()}
**Current Context**: {urgency_addon}

Your approach should be:
- **Methodical**: Follow systematic debugging practices
- **Evidence-based**: Base conclusions on concrete evidence
- **Practical**: Provide actionable, implementable solutions
- **Educational**: Explain reasoning to help prevent future issues
- **Safety-conscious**: Consider potential risks and side effects
"""
    
    def _build_analysis_framework(self, prompt_type: PromptType, context: PromptContext) -> str:
        """Build structured analysis framework"""
        
        frameworks = {
            PromptType.ERROR_ANALYSIS: """
### 🔍 SYSTEMATIC ERROR ANALYSIS FRAMEWORK

**Phase 1: Error Classification (30 seconds)**
- Categorize error type and severity
- Assess immediate impact and scope
- Determine urgency level

**Phase 2: Evidence Collection (2 minutes)**
- Gather all available error information
- Identify patterns and anomalies
- Collect environmental context

**Phase 3: Hypothesis Formation (3 minutes)**
- Generate 3-5 potential root causes
- Rank by probability and evidence
- Identify missing information

**Phase 4: Solution Design (5 minutes)**
- Design targeted solution approach
- Consider implementation complexity
- Plan validation and testing strategy

**Phase 5: Risk Assessment (2 minutes)**
- Evaluate solution risks
- Plan rollback strategies
- Consider prevention measures
""",
            
            PromptType.TREE_OF_THOUGHTS: """
### 🌳 TREE OF THOUGHTS EXPLORATION FRAMEWORK

**Depth Strategy**: Explore each path to maximum depth of 3 levels
**Breadth Strategy**: Generate 3 distinct approaches per level
**Evaluation Criteria**: Viability, Evidence, Complexity
**Selection Method**: Highest composite score wins
**Validation Approach**: Concrete tests for each path
""",
            
            PromptType.REACT_REASONING: """
### 🔄 REACT SYSTEMATIC INVESTIGATION FRAMEWORK

**Investigation Rules**:
- Each action must be specific and measurable
- Observations must be factual, not interpretive
- Reflections must update our understanding
- Maximum 10 cycles before concluding

**Action Priority**:
1. Gather immediate evidence
2. Test most likely hypothesis
3. Explore alternative causes
4. Validate solution approach
"""
        }
        
        return frameworks.get(prompt_type, frameworks[PromptType.ERROR_ANALYSIS])
    
    def _inject_domain_knowledge(self, context: PromptContext) -> str:
        """Inject domain-specific knowledge and best practices"""
        
        domain_knowledge = {
            "web_development": """
### 🌐 WEB DEVELOPMENT EXPERTISE
- **Common Patterns**: CORS issues, authentication problems, API integration failures
- **Debugging Tools**: Browser DevTools, network inspection, server logs
- **Best Practices**: RESTful design, proper error handling, security considerations
- **Frameworks**: FastAPI, Express.js, React, Vue.js debugging patterns
""",
            
            "systems_programming": """
### ⚙️ SYSTEMS PROGRAMMING EXPERTISE  
- **Common Patterns**: Memory leaks, race conditions, performance bottlenecks
- **Debugging Tools**: Profilers, debuggers, monitoring tools, system calls
- **Best Practices**: Resource management, concurrent programming, optimization
- **Languages**: C/C++, Rust, Go specific debugging approaches
""",
            
            "data_science": """
### 📊 DATA SCIENCE EXPERTISE
- **Common Patterns**: Data pipeline failures, model accuracy issues, memory problems
- **Debugging Tools**: Jupyter notebooks, profilers, data visualization
- **Best Practices**: Data validation, reproducible research, version control
- **Libraries**: Pandas, NumPy, scikit-learn, TensorFlow debugging
"""
        }
        
        return domain_knowledge.get(context.domain, """
### 🔧 GENERAL PROGRAMMING EXPERTISE
- **Common Patterns**: Logic errors, configuration issues, dependency problems
- **Debugging Tools**: IDE debuggers, logging, testing frameworks
- **Best Practices**: Clean code, proper testing, documentation
- **Approaches**: Systematic problem-solving, evidence-based debugging
""")
    
    def _build_constraints(self, context: PromptContext) -> str:
        """Build context-specific constraints"""
        
        constraints = []
        
        # Privacy constraints
        if context.privacy_level == "high":
            constraints.append("- **Privacy**: All solutions must work with anonymized data")
            constraints.append("- **Security**: No external API calls or data transmission")
        
        # Urgency constraints
        urgency_constraints = {
            "LOW": "- **Time**: Comprehensive analysis preferred, no rush",
            "MEDIUM": "- **Time**: Balance between thoroughness and speed",
            "HIGH": "- **Time**: Quick resolution needed, focus on immediate fixes",
            "CRITICAL": "- **Time**: Emergency situation, immediate safe action required"
        }
        constraints.append(urgency_constraints.get(context.urgency, ""))
        
        # Complexity constraints
        if context.complexity_level > 7:
            constraints.append("- **Complexity**: This is a complex issue requiring deep analysis")
        elif context.complexity_level < 4:
            constraints.append("- **Complexity**: Keep solutions simple and straightforward")
        
        # Expertise constraints
        expertise_constraints = {
            ExpertiseLevel.JUNIOR: "- **Communication**: Use clear explanations, avoid complex jargon",
            ExpertiseLevel.SENIOR: "- **Communication**: Technical depth appropriate for experienced developer",
            ExpertiseLevel.ARCHITECT: "- **Communication**: Focus on architectural implications and best practices",
            ExpertiseLevel.SPECIALIST: "- **Communication**: Deep technical detail with specialist terminology"
        }
        constraints.append(expertise_constraints[context.user_expertise])
        
        return "\n".join(constraints)
    
    def _build_output_format(self, prompt_type: PromptType, context: PromptContext) -> str:
        """Build structured output format specification"""
        
        base_format = """
### 📋 STRUCTURED OUTPUT REQUIREMENTS

**Format**: JSON with the following structure
**Confidence**: Include confidence scores (0.0-1.0) for all assessments
**Alternatives**: Provide alternative approaches when applicable
**Validation**: Include specific validation steps
**Prevention**: Add prevention strategies to avoid recurrence

**Required Fields**:
```json
{
  "analysis": "Root cause analysis",
  "confidence_score": 0.85,
  "solution_approach": "Primary solution strategy",
  "implementation_steps": ["step1", "step2", "step3"],
  "validation_plan": ["test1", "test2"],
  "risk_assessment": {
    "level": "low|medium|high",
    "factors": ["risk1", "risk2"],
    "mitigation": ["mitigation1", "mitigation2"]
  },
  "prevention_strategy": ["prevent1", "prevent2"],
  "alternatives": ["alt1", "alt2"],
  "estimated_time": "time estimate",
  "success_probability": 0.90
}
```
"""
        
        return base_format
    
    def _format_error_context(self, error_data: Dict[str, Any]) -> str:
        """Format error context for prompt inclusion"""
        
        formatted = f"""
### 🚨 ERROR DETAILS
**Type**: {error_data.get('error_type', 'Unknown')}
**Message**: {error_data.get('error_message', 'No message available')}
**File**: {error_data.get('file_path', 'Unknown')}:{error_data.get('line_number', 'Unknown')}
**Function**: {error_data.get('function_name', 'Unknown')}

### 📚 STACK TRACE
```
{error_data.get('stack_trace', 'No stack trace available')}
```

### 💻 CODE CONTEXT
```python
{chr(10).join(error_data.get('code_context', ['No code context available']))}
```
"""
        
        return formatted
    
    def _format_additional_context(self, additional_context: Dict[str, Any]) -> str:
        """Format additional context information"""
        
        if not additional_context:
            return ""
        
        formatted = "\n### 📊 ADDITIONAL CONTEXT\n"
        
        for key, value in additional_context.items():
            if isinstance(value, (list, dict)):
                formatted += f"**{key.replace('_', ' ').title()}**:\n```json\n{json.dumps(value, indent=2)}\n```\n\n"
            else:
                formatted += f"**{key.replace('_', ' ').title()}**: {value}\n"
        
        return formatted
    
    def optimize_prompt_for_model(self, prompt: str, model_name: str) -> str:
        """Optimize prompt for specific model characteristics"""
        
        model_optimizations = {
            "llama3.2": {
                "max_length": 8192,
                "prefers_structured": True,
                "markdown_friendly": True
            },
            "mixtral": {
                "max_length": 32768,
                "prefers_detailed": True,
                "reasoning_focused": True
            },
            "phi3": {
                "max_length": 4096,
                "prefers_concise": True,
                "direct_answers": True
            },
            "codellama": {
                "max_length": 16384,
                "code_focused": True,
                "technical_detail": True
            }
        }
        
        # Find matching optimization
        optimization = None
        for model_key, config in model_optimizations.items():
            if model_key in model_name.lower():
                optimization = config
                break
        
        if not optimization:
            return prompt  # No optimization needed
        
        # Apply optimizations
        optimized_prompt = prompt
        
        # Length optimization
        if len(prompt) > optimization.get("max_length", 8192):
            optimized_prompt = self._truncate_prompt_intelligently(prompt, optimization["max_length"])
        
        # Style optimizations
        if optimization.get("prefers_concise"):
            optimized_prompt = self._make_prompt_concise(optimized_prompt)
        
        if optimization.get("code_focused"):
            optimized_prompt = self._enhance_code_focus(optimized_prompt)
        
        return optimized_prompt
    
    def _truncate_prompt_intelligently(self, prompt: str, max_length: int) -> str:
        """Intelligently truncate prompt while preserving key sections"""
        
        if len(prompt) <= max_length:
            return prompt
        
        # Identify key sections to preserve
        key_sections = [
            r"# .*SYSTEM.*",  # System headers
            r"## 🔍 ERROR.*",  # Error context
            r"## 📤 .*OUTPUT.*",  # Output format
            r"```json.*?```"  # JSON examples
        ]
        
        preserved_content = []
        for pattern in key_sections:
            matches = re.findall(pattern, prompt, re.DOTALL | re.IGNORECASE)
            preserved_content.extend(matches)
        
        # Build truncated version
        essential_content = "\n\n".join(preserved_content)
        
        if len(essential_content) <= max_length:
            return essential_content
        else:
            return essential_content[:max_length] + "\n\n**[Truncated for model constraints]**"
    
    def _make_prompt_concise(self, prompt: str) -> str:
        """Make prompt more concise for lightweight models"""
        
        # Remove verbose explanations
        concise_prompt = re.sub(r'\*\*.*?\*\*:', '**', prompt)  # Simplify bold headers
        concise_prompt = re.sub(r'\n\n+', '\n\n', concise_prompt)  # Remove extra newlines
        
        return concise_prompt
    
    def _enhance_code_focus(self, prompt: str) -> str:
        """Enhance code-focused elements for code-specialized models"""
        
        # Add code analysis emphasis
        code_focused = prompt.replace(
            "Execute comprehensive expert analysis",
            "Focus on code analysis and provide specific programming solutions"
        )
        
        return code_focused

# Convenience functions
def create_debugging_prompt(
    error_data: Dict[str, Any],
    approach: str = "error_analysis",
    complexity: int = 5,
    urgency: str = "MEDIUM",
    tech_stack: List[str] = None,
    user_expertise: str = "senior"
) -> str:
    """Convenience function to create debugging prompts"""
    
    engineer = AdvancedPromptEngineer()
    
    prompt_type = PromptType(approach)
    
    context = PromptContext(
        error_type=error_data.get('error_type', 'Unknown'),
        complexity_level=complexity,
        domain="web_development",  # Default domain
        tech_stack=tech_stack or ["python", "fastapi"],
        urgency=urgency,
        privacy_level="high",
        user_expertise=ExpertiseLevel(user_expertise)
    )
    
    return engineer.create_expert_prompt(prompt_type, context, error_data)

def create_tree_of_thoughts_prompt(error_data: Dict[str, Any], **kwargs) -> str:
    """Create Tree of Thoughts debugging prompt"""
    return create_debugging_prompt(error_data, approach="tree_of_thoughts", **kwargs)

def create_react_prompt(error_data: Dict[str, Any], **kwargs) -> str:
    """Create ReAct debugging prompt"""
    return create_debugging_prompt(error_data, approach="react_reasoning", **kwargs)

# Test function
def test_prompt_generation():
    """Test the prompt generation system"""
    
    sample_error = {
        'error_type': 'HTTPConnectionError',
        'error_message': 'Connection timeout to localhost:8000',
        'file_path': '/app/src/main.py',
        'line_number': 42,
        'function_name': 'health_check',
        'stack_trace': 'Traceback...',
        'code_context': ['def health_check():', '    response = requests.get("http://localhost:8000")', '    return response.json()']
    }
    
    # Test different approaches
    approaches = ["error_analysis", "tree_of_thoughts", "react_reasoning"]
    
    for approach in approaches:
        print(f"\n{'='*50}")
        print(f"Testing {approach.upper()} approach")
        print(f"{'='*50}")
        
        prompt = create_debugging_prompt(
            sample_error,
            approach=approach,
            complexity=7,
            urgency="HIGH",
            tech_stack=["python", "fastapi", "requests"]
        )
        
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)

if __name__ == "__main__":
    test_prompt_generation()
