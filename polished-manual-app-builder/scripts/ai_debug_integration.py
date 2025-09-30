#!/usr/bin/env python3
"""
AI Debugging System Integration & Performance Testing
Comprehensive testing and optimization of the next-generation AI debugging system
"""

import asyncio
import json
import logging
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils import safe_subprocess_run, print_once
import concurrent.futures
from dataclasses import dataclass
import statistics

# Import our AI debugging components
sys.path.append(str(Path(__file__).parent))
from ai_debug_system import NextGenAIDebugger, ErrorContext
from advanced_prompt_engineering import AdvancedPromptEngineer, create_debugging_prompt

@dataclass
class TestCase:
    """Test case for AI debugging system"""
    name: str
    error_type: str
    error_data: Dict[str, Any]
    expected_confidence: float
    complexity_level: int
    tech_stack: List[str]

@dataclass
class PerformanceMetrics:
    """Performance metrics for debugging operations"""
    response_time: float
    confidence_score: float
    accuracy_score: float
    solution_quality: float
    memory_usage: float
    model_efficiency: float

class AIDebugIntegrationTester:
    """Comprehensive integration testing for AI debugging system"""
    
    def __init__(self, config_path: str = "scripts/ai_debug_config.json"):
        self.config_path = Path(config_path)
        self.debugger = NextGenAIDebugger(str(config_path))
        self.prompt_engineer = AdvancedPromptEngineer(str(config_path))
        
        # Test results storage
        self.test_results: List[Dict[str, Any]] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_debug_integration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_test_cases(self) -> List[TestCase]:
        """Generate comprehensive test cases"""
        return [
            TestCase(
                name="Python Import Error",
                error_type="ImportError",
                error_data={
                    'error_type': 'ImportError',
                    'error_message': 'No module named pandas',
                    'file_path': '/app/data_processor.py',
                    'line_number': 15,
                    'function_name': 'process_data',
                    'stack_trace': 'Traceback...',
                    'code_context': ['import pandas as pd', 'import numpy as np', 'def process_data():']
                },
                expected_confidence=0.9,
                complexity_level=3,
                tech_stack=["python", "pandas", "data-science"]
            ),
            
            TestCase(
                name="JavaScript Async Error",
                error_type="TypeError",
                error_data={
                    'error_type': 'TypeError',
                    'error_message': 'Cannot read property of undefined',
                    'file_path': '/app/src/api.js',
                    'line_number': 28,
                    'function_name': 'fetchUserData',
                    'stack_trace': 'TypeError: Cannot read property...',
                    'code_context': ['const user = await api.getUser(id);', 'return user.profile.name;']
                },
                expected_confidence=0.85,
                complexity_level=5,
                tech_stack=["javascript", "node.js", "async"]
            ),
            
            TestCase(
                name="Rust Ownership Error",
                error_type="BorrowCheckError",
                error_data={
                    'error_type': 'BorrowCheckError',
                    'error_message': 'cannot borrow as mutable',
                    'file_path': '/app/src/main.rs',
                    'line_number': 45,
                    'function_name': 'process_data',
                    'stack_trace': 'error[E0502]: cannot borrow...',
                    'code_context': ['let mut data = vec![1, 2, 3];', 'let reference = &data;', 'data.push(4);']
                },
                expected_confidence=0.8,
                complexity_level=8,
                tech_stack=["rust", "ownership", "borrowing"]
            ),
            
            TestCase(
                name="Network Connection Error",
                error_type="ConnectionError",
                error_data={
                    'error_type': 'ConnectionError',
                    'error_message': 'Connection timeout to database',
                    'file_path': '/app/database.py',
                    'line_number': 67,
                    'function_name': 'connect_db',
                    'stack_trace': 'ConnectionError: timeout...',
                    'code_context': ['conn = psycopg2.connect(', '    host="localhost",', '    timeout=5', ')']
                },
                expected_confidence=0.75,
                complexity_level=6,
                tech_stack=["python", "postgresql", "networking"]
            ),
            
            TestCase(
                name="Complex Authentication Error",
                error_type="AuthenticationError",
                error_data={
                    'error_type': 'AuthenticationError',
                    'error_message': 'JWT token validation failed',
                    'file_path': '/app/auth/middleware.py',
                    'line_number': 89,
                    'function_name': 'validate_token',
                    'stack_trace': 'AuthenticationError: invalid signature...',
                    'code_context': ['payload = jwt.decode(token, secret, algorithms=["HS256"])', 'return payload["user_id"]']
                },
                expected_confidence=0.7,
                complexity_level=9,
                tech_stack=["python", "jwt", "authentication", "security"]
            )
        ]
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests"""
        self.logger.info("Starting comprehensive AI debugging integration tests...")
        
        test_cases = self.get_test_cases()
        results = {
            'timestamp': time.time(),
            'total_tests': len(test_cases),
            'test_results': [],
            'performance_summary': {},
            'system_health': {},
            'recommendations': []
        }
        
        # Test each debugging approach
        approaches = ['standard', 'tree_of_thoughts', 'react', 'intelligent_routing']
        
        for approach in approaches:
            self.logger.info(f"Testing {approach} debugging approach...")
            approach_results = await self._test_approach(test_cases, approach)
            results['test_results'].append({
                'approach': approach,
                'results': approach_results
            })
        
        # Performance analysis
        results['performance_summary'] = self._analyze_performance()
        
        # System health check
        results['system_health'] = await self._system_health_check()
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        # Save results
        self._save_results(results)
        
        return results
    
    async def _test_approach(self, test_cases: List[TestCase], approach: str) -> List[Dict[str, Any]]:
        """Test specific debugging approach"""
        approach_results = []
        
        for test_case in test_cases:
            self.logger.info(f"Testing {test_case.name} with {approach} approach...")
            
            start_time = time.time()
            
            try:
                # Create ErrorContext with all required fields
                context = ErrorContext(
                    error_type=test_case.error_type,
                    error_message=test_case.error_data.get('message', 'Unknown error'),
                    stack_trace=test_case.error_data.get('stack_trace', ''),
                    file_path=test_case.error_data.get('file_path', ''),
                    line_number=test_case.error_data.get('line_number', 0),
                    function_name=test_case.error_data.get('function_name', ''),
                    code_context=test_case.error_data.get('code_context', []),
                    environment_info=test_case.error_data.get('environment_info', {}),
                    related_files=test_case.error_data.get('related_files', []),
                    dependency_info=test_case.error_data.get('dependency_info', {}),
                    system_metrics=test_case.error_data.get('system_metrics', {}),
                    timestamp=str(time.time())
                )
                
                # Use the correct method - analyze_error is the main entry point
                result = await self.debugger.analyze_error(test_case.error_data, approach=approach)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Evaluate result - convert DebugSolution to dict for evaluation
                result_dict = {
                    'analysis': result.analysis,
                    'solution': '\n'.join(result.solution_steps),
                    'confidence': result.confidence_score,
                    'prevention': '\n'.join(result.prevention_tips),
                    'diagnostic_commands': result.diagnostic_commands,
                    'estimated_time': result.estimated_time,
                    'risk_level': result.risk_level
                }
                evaluation = self._evaluate_result(test_case, result_dict, response_time)
                approach_results.append(evaluation)
                
                # Record performance metrics
                metrics = PerformanceMetrics(
                    response_time=response_time,
                    confidence_score=result.confidence_score,
                    accuracy_score=evaluation['accuracy_score'],
                    solution_quality=evaluation['solution_quality'],
                    memory_usage=evaluation.get('memory_usage', 0),
                    model_efficiency=evaluation.get('model_efficiency', 0)
                )
                self.performance_metrics.append(metrics)
                
            except Exception as e:
                self.logger.error(f"Error testing {test_case.name}: {e}")
                approach_results.append({
                    'test_case': test_case.name,
                    'success': False,
                    'error': str(e),
                    'response_time': time.time() - start_time
                })
        
        return approach_results
    
    def _evaluate_result(self, test_case: TestCase, result: Dict[str, Any], response_time: float) -> Dict[str, Any]:
        """Evaluate debugging result quality"""
        
        # Basic success criteria
        has_analysis = 'analysis' in result and result['analysis']
        has_solution = 'solution' in result and result['solution']
        has_confidence = 'confidence' in result
        
        # Confidence evaluation
        confidence_score = result.get('confidence', 0)
        confidence_meets_expectation = confidence_score >= test_case.expected_confidence - 0.1
        
        # Response time evaluation (should be under 30 seconds for most cases)
        time_acceptable = response_time < 30.0
        
        # Solution quality heuristics
        solution_text = result.get('solution', '')
        solution_quality = min(1.0, len(solution_text) / 500)  # Basic length heuristic
        
        # Calculate accuracy score
        accuracy_components = [
            has_analysis,
            has_solution,
            has_confidence,
            confidence_meets_expectation,
            time_acceptable
        ]
        accuracy_score = sum(accuracy_components) / len(accuracy_components)
        
        return {
            'test_case': test_case.name,
            'success': has_analysis and has_solution,
            'accuracy_score': accuracy_score,
            'solution_quality': solution_quality,
            'confidence_score': confidence_score,
            'expected_confidence': test_case.expected_confidence,
            'response_time': response_time,
            'time_acceptable': time_acceptable,
            'result_completeness': {
                'has_analysis': has_analysis,
                'has_solution': has_solution,
                'has_confidence': has_confidence,
                'has_prevention': 'prevention' in result
            }
        }
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze overall performance metrics"""
        if not self.performance_metrics:
            return {}
        
        response_times = [m.response_time for m in self.performance_metrics]
        confidence_scores = [m.confidence_score for m in self.performance_metrics]
        accuracy_scores = [m.accuracy_score for m in self.performance_metrics]
        solution_qualities = [m.solution_quality for m in self.performance_metrics]
        
        return {
            'response_time': {
                'mean': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            'confidence': {
                'mean': statistics.mean(confidence_scores),
                'median': statistics.median(confidence_scores),
                'min': min(confidence_scores),
                'max': max(confidence_scores)
            },
            'accuracy': {
                'mean': statistics.mean(accuracy_scores),
                'median': statistics.median(accuracy_scores),
                'pass_rate': sum(1 for s in accuracy_scores if s >= 0.8) / len(accuracy_scores)
            },
            'solution_quality': {
                'mean': statistics.mean(solution_qualities),
                'median': statistics.median(solution_qualities)
            },
            'total_tests': len(self.performance_metrics)
        }
    
    async def _system_health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health = {
            'ollama_status': 'unknown',
            'model_availability': {},
            'memory_usage': 0,
            'disk_space': 0,
            'network_connectivity': False
        }
        
        try:
            # Check Ollama status
            result = safe_subprocess_run(['curl', '-s', 'http://localhost:11434/api/tags'], 
                                       timeout=10)
            if result and result.returncode == 0:
                health['ollama_status'] = 'running'
                models_data = json.loads(result.stdout)
                health['model_availability'] = {
                    model['name']: model.get('size', 'unknown') 
                    for model in models_data.get('models', [])
                }
            else:
                health['ollama_status'] = 'stopped'
        except Exception as e:
            health['ollama_status'] = f'error: {e}'
        
        # Check system resources - conditional import
        try:
            import psutil
            health['memory_usage'] = psutil.virtual_memory().percent
            health['disk_space'] = psutil.disk_usage('/').percent
        except ImportError:
            health['memory_usage'] = 'psutil not available'
            health['disk_space'] = 'psutil not available'
        except Exception as e:
            print_once(f"System resource check failed: {e}", "WARNING")
            health['memory_usage'] = 'error'
            health['disk_space'] = 'error'
        
        # Check network connectivity
        try:
            result = safe_subprocess_run(['ping', '-c', '1', 'google.com'], 
                                       timeout=5)
            health['network_connectivity'] = result and result.returncode == 0
        except Exception:
            health['network_connectivity'] = False
        
        return health
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        performance = results.get('performance_summary', {})
        
        # Response time recommendations
        avg_response_time = performance.get('response_time', {}).get('mean', 0)
        if avg_response_time > 20:
            recommendations.append(
                "⚠️ High response times detected. Consider optimizing prompt length or using faster models."
            )
        
        # Accuracy recommendations
        accuracy_stats = performance.get('accuracy', {})
        avg_accuracy = accuracy_stats.get('mean', 0)
        pass_rate = accuracy_stats.get('pass_rate', 0)
        
        if avg_accuracy < 0.8:
            recommendations.append(
                "📈 Low accuracy scores. Consider improving prompt engineering or model selection."
            )
        
        if pass_rate < 0.9:
            recommendations.append(
                "🎯 Pass rate below 90%. Review failed test cases and enhance error handling."
            )
        
        # Confidence recommendations
        confidence_stats = performance.get('confidence', {})
        avg_confidence = confidence_stats.get('mean', 0)
        
        if avg_confidence < 0.7:
            recommendations.append(
                "🤔 Low confidence scores. Consider using more sophisticated models or ensemble approaches."
            )
        
        # System health recommendations
        health = results.get('system_health', {})
        
        if health.get('ollama_status') != 'running':
            recommendations.append(
                "🚨 Ollama not running. Start Ollama service for local AI debugging."
            )
        
        if isinstance(health.get('memory_usage'), (int, float)) and health['memory_usage'] > 80:
            recommendations.append(
                "💾 High memory usage detected. Consider optimizing memory allocation or using lighter models."
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append(
                "✅ System performing well! Consider exploring advanced debugging modes for complex issues."
            )
        
        return recommendations
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save test results to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"ai_debug_integration_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to {results_file}")
    
    async def benchmark_performance(self, iterations: int = 10) -> Dict[str, Any]:
        """Run performance benchmarks"""
        self.logger.info(f"Running performance benchmark with {iterations} iterations...")
        
        benchmark_case = TestCase(
            name="Benchmark Test",
            error_type="TypeError",
            error_data={
                'error_type': 'TypeError',
                'error_message': 'Object has no attribute',
                'file_path': '/test/benchmark.py',
                'line_number': 42,
                'function_name': 'test_function',
                'stack_trace': 'Traceback...',
                'code_context': ['obj.nonexistent_method()', 'return result']
            },
            expected_confidence=0.8,
            complexity_level=5,
            tech_stack=["python"]
        )
        
        benchmark_results = []
        
        for i in range(iterations):
            self.logger.info(f"Benchmark iteration {i+1}/{iterations}")
            
            start_time = time.time()
            
            # Create proper ErrorContext for debugging
            context = ErrorContext(
                error_type=benchmark_case.error_type,
                error_message=benchmark_case.error_data.get('message', 'Benchmark error'),
                stack_trace=benchmark_case.error_data.get('stack_trace', ''),
                file_path=benchmark_case.error_data.get('file_path', ''),
                line_number=benchmark_case.error_data.get('line_number', 0),
                function_name=benchmark_case.error_data.get('function_name', ''),
                code_context=benchmark_case.error_data.get('code_context', []),
                environment_info=benchmark_case.error_data.get('environment_info', {}),
                related_files=benchmark_case.error_data.get('related_files', []),
                dependency_info=benchmark_case.error_data.get('dependency_info', {}),
                system_metrics=benchmark_case.error_data.get('system_metrics', {}),
                timestamp=str(time.time())
            )
            
            result = await self.debugger.analyze_error(benchmark_case.error_data, approach='auto')
            
            end_time = time.time()
            response_time = end_time - start_time
            
            benchmark_results.append({
                'iteration': i + 1,
                'response_time': response_time,
                'confidence': result.confidence_score,
                'success': bool(result.analysis and result.solution_steps)
            })
        
        # Calculate benchmark statistics
        response_times = [r['response_time'] for r in benchmark_results]
        confidences = [r['confidence'] for r in benchmark_results]
        success_rate = sum(1 for r in benchmark_results if r['success']) / len(benchmark_results)
        
        benchmark_summary = {
            'iterations': iterations,
            'success_rate': success_rate,
            'response_time': {
                'mean': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'p95': sorted(response_times)[int(0.95 * len(response_times))],
                'p99': sorted(response_times)[int(0.99 * len(response_times))]
            },
            'confidence': {
                'mean': statistics.mean(confidences),
                'median': statistics.median(confidences),
                'min': min(confidences),
                'max': max(confidences)
            },
            'raw_results': benchmark_results
        }
        
        self.logger.info(f"Benchmark completed. Average response time: {benchmark_summary['response_time']['mean']:.2f}s")
        
        return benchmark_summary

def run_integration_tests():
    """Main function to run integration tests"""
    tester = AIDebugIntegrationTester()
    
    # Run comprehensive tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        print("🚀 Starting AI Debugging System Integration Tests...")
        print("=" * 60)
        
        # Comprehensive testing
        results = loop.run_until_complete(tester.run_comprehensive_tests())
        
        print("\n📊 Test Results Summary:")
        print(f"Total Tests: {results['total_tests']}")
        
        # Performance summary
        perf = results.get('performance_summary', {})
        if perf:
            print(f"Average Response Time: {perf.get('response_time', {}).get('mean', 0):.2f}s")
            print(f"Average Confidence: {perf.get('confidence', {}).get('mean', 0):.2f}")
            print(f"Pass Rate: {perf.get('accuracy', {}).get('pass_rate', 0):.1%}")
        
        # Recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  {rec}")
        
        # Performance benchmark
        print("\n🏃 Running Performance Benchmark...")
        benchmark = loop.run_until_complete(tester.benchmark_performance(5))
        print(f"Benchmark - Avg Response: {benchmark['response_time']['mean']:.2f}s, Success Rate: {benchmark['success_rate']:.1%}")
        
        print("\n✅ Integration testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Integration testing failed: {e}")
        raise
    finally:
        loop.close()

if __name__ == "__main__":
    run_integration_tests()
