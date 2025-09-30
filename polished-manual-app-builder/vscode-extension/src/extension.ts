import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';

/**
 * AI Debug Assistant Extension for VS Code
 * Next-generation AI-powered debugging with autonomous problem-solving
 */

interface ErrorContext {
    errorType: string;
    errorMessage: string;
    filePath: string;
    lineNumber: number;
    functionName?: string;
    stackTrace?: string;
    codeContext: string[];
    timestamp: Date;
}

interface AIDebugConfig {
    enabled: boolean;
    ollamaEndpoint: string;
    defaultModel: string;
    autoAnalyze: boolean;
    debuggingMode: 'standard' | 'tree-of-thoughts' | 'react' | 'intelligent';
    expertiseLevel: 'junior' | 'senior' | 'architect' | 'specialist';
    privacyMode: boolean;
}

interface AIResponse {
    analysis: string;
    confidence_score: number;
    solution_approach: string;
    implementation_steps: string[];
    validation_plan: string[];
    risk_assessment: {
        level: string;
        factors: string[];
        mitigation: string[];
    };
    prevention_strategy: string[];
    alternatives: string[];
    estimated_time: string;
    success_probability: number;
}

class AIDebugAssistant {
    private context: vscode.ExtensionContext;
    private config: AIDebugConfig;
    private outputChannel: vscode.OutputChannel;
    private diagnosticCollection: vscode.DiagnosticCollection;
    private errorHistory: ErrorContext[] = [];
    private isAnalyzing = false;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('AI Debug Assistant');
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('ai-debug');
        this.loadConfiguration();
        this.setupEventListeners();
    }

    private loadConfiguration(): void {
        const config = vscode.workspace.getConfiguration('ai-debug');
        this.config = {
            enabled: config.get('enabled', true),
            ollamaEndpoint: config.get('ollama.endpoint', 'http://localhost:11434'),
            defaultModel: config.get('defaultModel', 'llama3.2'),
            autoAnalyze: config.get('autoAnalyze', true),
            debuggingMode: config.get('debuggingMode', 'intelligent'),
            expertiseLevel: config.get('expertiseLevel', 'senior'),
            privacyMode: config.get('privacyMode', true)
        };
    }

    private setupEventListeners(): void {
        // Configuration change listener
        vscode.workspace.onDidChangeConfiguration(event => {
            if (event.affectsConfiguration('ai-debug')) {
                this.loadConfiguration();
            }
        });

        // Document change listener for error detection
        vscode.workspace.onDidChangeTextDocument(event => {
            if (this.config.autoAnalyze && this.config.enabled) {
                this.analyzeDocumentErrors(event.document);
            }
        });

        // Diagnostic change listener
        vscode.languages.onDidChangeDiagnostics(event => {
            if (this.config.autoAnalyze && this.config.enabled) {
                this.handleDiagnosticChanges(event);
            }
        });
    }

    async analyzeDocumentErrors(document: vscode.TextDocument): Promise<void> {
        if (this.isAnalyzing) return;
        
        const diagnostics = vscode.languages.getDiagnostics(document.uri);
        const errors = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error);
        
        if (errors.length > 0 && this.shouldAnalyzeErrors()) {
            for (const error of errors) {
                await this.analyzeError(document, error);
            }
        }
    }

    private shouldAnalyzeErrors(): boolean {
        // Rate limiting: only analyze errors every 5 seconds
        const lastAnalysis = this.context.globalState.get('lastErrorAnalysis', 0);
        const now = Date.now();
        
        if (now - lastAnalysis < 5000) {
            return false;
        }
        
        this.context.globalState.update('lastErrorAnalysis', now);
        return true;
    }

    async analyzeError(document: vscode.TextDocument, diagnostic: vscode.Diagnostic): Promise<void> {
        try {
            this.isAnalyzing = true;
            
            const errorContext = this.buildErrorContext(document, diagnostic);
            this.errorHistory.push(errorContext);
            
            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'AI Debug Assistant',
                cancellable: true
            }, async (progress, token) => {
                progress.report({ message: 'Analyzing error...' });
                
                const analysis = await this.callAIDebugSystem(errorContext);
                
                if (analysis && !token.isCancellationRequested) {
                    progress.report({ message: 'Generating solutions...' });
                    await this.presentAnalysis(errorContext, analysis);
                }
            });
            
        } catch (error) {
            this.outputChannel.appendLine(`Error analyzing: ${error}`);
            vscode.window.showErrorMessage('AI Debug Assistant encountered an error');
        } finally {
            this.isAnalyzing = false;
        }
    }

    private buildErrorContext(document: vscode.TextDocument, diagnostic: vscode.Diagnostic): ErrorContext {
        const line = diagnostic.range.start.line;
        const codeContext = this.getCodeContext(document, line);
        
        return {
            errorType: this.classifyError(diagnostic.message),
            errorMessage: diagnostic.message,
            filePath: document.uri.fsPath,
            lineNumber: line + 1,
            functionName: this.findFunctionName(document, line),
            codeContext,
            timestamp: new Date()
        };
    }

    private getCodeContext(document: vscode.TextDocument, errorLine: number): string[] {
        const contextLines = 5;
        const startLine = Math.max(0, errorLine - contextLines);
        const endLine = Math.min(document.lineCount - 1, errorLine + contextLines);
        
        const context: string[] = [];
        for (let i = startLine; i <= endLine; i++) {
            const lineText = document.lineAt(i).text;
            const marker = i === errorLine ? ' >>> ' : '     ';
            context.push(`${i + 1}${marker}${lineText}`);
        }
        
        return context;
    }

    private classifyError(message: string): string {
        const patterns = {
            'SyntaxError': /syntax error|unexpected token|invalid syntax/i,
            'TypeError': /type error|cannot read property|is not a function/i,
            'ReferenceError': /not defined|is not declared/i,
            'ImportError': /cannot import|module not found/i,
            'NetworkError': /connection|timeout|network|fetch/i,
            'AuthenticationError': /unauthorized|authentication|permission/i,
            'ValidationError': /validation|invalid|required/i
        };

        for (const [errorType, pattern] of Object.entries(patterns)) {
            if (pattern.test(message)) {
                return errorType;
            }
        }

        return 'UnknownError';
    }

    private findFunctionName(document: vscode.TextDocument, errorLine: number): string | undefined {
        // Simple function detection - can be enhanced with AST parsing
        for (let i = errorLine; i >= 0; i--) {
            const line = document.lineAt(i).text;
            const funcMatch = line.match(/(?:def|function|async function|class)\s+(\w+)/);
            if (funcMatch) {
                return funcMatch[1];
            }
        }
        return undefined;
    }

    private async callAIDebugSystem(errorContext: ErrorContext): Promise<AIResponse | null> {
        try {
            if (!this.config.privacyMode) {
                // Use external AI service if privacy mode is off
                return await this.callExternalAI(errorContext);
            } else {
                // Use local Ollama instance
                return await this.callOllamaAI(errorContext);
            }
        } catch (error) {
            this.outputChannel.appendLine(`AI call failed: ${error}`);
            return null;
        }
    }

    private async callOllamaAI(errorContext: ErrorContext): Promise<AIResponse | null> {
        try {
            const prompt = this.buildPrompt(errorContext);
            
            const response = await axios.post(`${this.config.ollamaEndpoint}/api/generate`, {
                model: this.config.defaultModel,
                prompt,
                stream: false,
                options: {
                    temperature: 0.1,
                    top_p: 0.9
                }
            });

            return this.parseAIResponse(response.data.response);
        } catch (error) {
            this.outputChannel.appendLine(`Ollama call failed: ${error}`);
            throw error;
        }
    }

    private async callExternalAI(errorContext: ErrorContext): Promise<AIResponse | null> {
        // Placeholder for external AI integration
        // Could integrate with OpenAI, Anthropic, etc.
        throw new Error('External AI integration not implemented in privacy mode');
    }

    private buildPrompt(errorContext: ErrorContext): string {
        const techStack = this.detectTechStack(errorContext.filePath);
        
        return `# 🤖 AI DEBUG ASSISTANT

## 👨‍💻 EXPERT ROLE
You are a senior software engineer with expertise in ${techStack.join(', ')}.
User expertise level: ${this.config.expertiseLevel}
Debugging mode: ${this.config.debuggingMode}

## 🚨 ERROR DETAILS
**Type**: ${errorContext.errorType}
**Message**: ${errorContext.errorMessage}
**File**: ${errorContext.filePath}:${errorContext.lineNumber}
**Function**: ${errorContext.functionName || 'Unknown'}

## 💻 CODE CONTEXT
\`\`\`
${errorContext.codeContext.join('\n')}
\`\`\`

## 📋 REQUIRED OUTPUT
Provide a JSON response with:
- Root cause analysis
- Solution approach with implementation steps
- Risk assessment and prevention strategy
- Confidence score and alternatives

Format as valid JSON only.`;
    }

    private detectTechStack(filePath: string): string[] {
        const ext = path.extname(filePath).toLowerCase();
        const techStacks: { [key: string]: string[] } = {
            '.py': ['Python', 'FastAPI', 'Django', 'Flask'],
            '.js': ['JavaScript', 'Node.js', 'Express'],
            '.ts': ['TypeScript', 'Node.js', 'React'],
            '.rs': ['Rust', 'Axum', 'Tokio'],
            '.go': ['Go', 'Gin', 'Echo'],
            '.java': ['Java', 'Spring Boot'],
            '.cs': ['C#', '.NET Core']
        };

        return techStacks[ext] || ['General'];
    }

    private parseAIResponse(response: string): AIResponse | null {
        try {
            // Extract JSON from response (handle cases where AI includes explanation)
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('No JSON found in response');
            }

            const parsed = JSON.parse(jsonMatch[0]);
            
            // Validate required fields
            if (!parsed.analysis || !parsed.solution_approach) {
                throw new Error('Invalid response format');
            }

            return parsed as AIResponse;
        } catch (error) {
            this.outputChannel.appendLine(`Failed to parse AI response: ${error}`);
            this.outputChannel.appendLine(`Raw response: ${response}`);
            return null;
        }
    }

    private async presentAnalysis(errorContext: ErrorContext, analysis: AIResponse): Promise<void> {
        // Create webview panel for detailed analysis
        const panel = vscode.window.createWebviewPanel(
            'aiDebugAnalysis',
            'AI Debug Analysis',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this.generateAnalysisHTML(errorContext, analysis);

        // Add quick fix actions
        await this.addQuickFixes(errorContext, analysis);

        // Show notification with summary
        const action = await vscode.window.showInformationMessage(
            `AI Analysis Complete (${Math.round(analysis.confidence_score * 100)}% confidence)`,
            'View Details',
            'Apply Fix',
            'Learn More'
        );

        if (action === 'Apply Fix') {
            await this.applyQuickFix(errorContext, analysis);
        } else if (action === 'Learn More') {
            await this.openErrorGuide(errorContext.errorType);
        }
    }

    private generateAnalysisHTML(errorContext: ErrorContext, analysis: AIResponse): string {
        return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Debug Analysis</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--vscode-editor-foreground);
            background-color: var(--vscode-editor-background);
            padding: 20px;
        }
        .header { 
            border-bottom: 2px solid var(--vscode-panel-border); 
            padding-bottom: 15px; 
            margin-bottom: 20px; 
        }
        .section { 
            margin-bottom: 25px; 
            padding: 15px; 
            border: 1px solid var(--vscode-panel-border); 
            border-radius: 8px; 
        }
        .confidence { 
            background: linear-gradient(90deg, #4CAF50 ${analysis.confidence_score * 100}%, #f0f0f0 ${analysis.confidence_score * 100}%);
            border-radius: 10px;
            padding: 5px 10px;
            color: white;
            font-weight: bold;
        }
        .risk-${analysis.risk_assessment.level} {
            color: ${analysis.risk_assessment.level === 'high' ? '#ff4444' : 
                     analysis.risk_assessment.level === 'medium' ? '#ffaa00' : '#44aa44'};
        }
        ul { margin: 10px 0; }
        li { margin: 5px 0; }
        code { 
            background: var(--vscode-textBlockQuote-background); 
            padding: 2px 4px; 
            border-radius: 3px; 
        }
        .button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        .button:hover {
            background: var(--vscode-button-hoverBackground);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Debug Analysis</h1>
        <p><strong>Error:</strong> ${errorContext.errorType}</p>
        <p><strong>File:</strong> ${errorContext.filePath}:${errorContext.lineNumber}</p>
        <p><strong>Confidence:</strong> <span class="confidence">${Math.round(analysis.confidence_score * 100)}%</span></p>
    </div>

    <div class="section">
        <h2>🔍 Root Cause Analysis</h2>
        <p>${analysis.analysis}</p>
    </div>

    <div class="section">
        <h2>💡 Solution Approach</h2>
        <p>${analysis.solution_approach}</p>
        
        <h3>Implementation Steps:</h3>
        <ol>
            ${analysis.implementation_steps.map(step => `<li>${step}</li>`).join('')}
        </ol>
    </div>

    <div class="section">
        <h2>⚠️ Risk Assessment</h2>
        <p><strong>Risk Level:</strong> <span class="risk-${analysis.risk_assessment.level}">${analysis.risk_assessment.level.toUpperCase()}</span></p>
        
        <h3>Risk Factors:</h3>
        <ul>
            ${analysis.risk_assessment.factors.map(factor => `<li>${factor}</li>`).join('')}
        </ul>
        
        <h3>Mitigation Strategies:</h3>
        <ul>
            ${analysis.risk_assessment.mitigation.map(strategy => `<li>${strategy}</li>`).join('')}
        </ul>
    </div>

    <div class="section">
        <h2>✅ Validation Plan</h2>
        <ul>
            ${analysis.validation_plan.map(step => `<li>${step}</li>`).join('')}
        </ul>
    </div>

    <div class="section">
        <h2>🛡️ Prevention Strategy</h2>
        <ul>
            ${analysis.prevention_strategy.map(strategy => `<li>${strategy}</li>`).join('')}
        </ul>
    </div>

    <div class="section">
        <h2>🔄 Alternative Approaches</h2>
        <ul>
            ${analysis.alternatives.map(alt => `<li>${alt}</li>`).join('')}
        </ul>
    </div>

    <div class="section">
        <h2>⏱️ Implementation Details</h2>
        <p><strong>Estimated Time:</strong> ${analysis.estimated_time}</p>
        <p><strong>Success Probability:</strong> ${Math.round(analysis.success_probability * 100)}%</p>
    </div>

    <div class="section">
        <button class="button" onclick="applyFix()">🔧 Apply Quick Fix</button>
        <button class="button" onclick="openGuide()">📚 Open Error Guide</button>
        <button class="button" onclick="requestMoreHelp()">❓ Request More Help</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        function applyFix() {
            vscode.postMessage({ command: 'applyFix' });
        }
        
        function openGuide() {
            vscode.postMessage({ command: 'openGuide' });
        }
        
        function requestMoreHelp() {
            vscode.postMessage({ command: 'moreHelp' });
        }
    </script>
</body>
</html>`;
    }

    private async addQuickFixes(errorContext: ErrorContext, analysis: AIResponse): Promise<void> {
        // Create code actions for quick fixes
        const uri = vscode.Uri.file(errorContext.filePath);
        const range = new vscode.Range(
            errorContext.lineNumber - 1, 0,
            errorContext.lineNumber - 1, 0
        );

        // Register code action provider for this specific error
        const disposable = vscode.languages.registerCodeActionsProvider(
            { pattern: errorContext.filePath },
            {
                provideCodeActions: () => {
                    const actions: vscode.CodeAction[] = [];
                    
                    for (const step of analysis.implementation_steps) {
                        const action = new vscode.CodeAction(
                            `AI Fix: ${step}`,
                            vscode.CodeActionKind.QuickFix
                        );
                        action.command = {
                            command: 'ai-debug.applyStep',
                            title: step,
                            arguments: [errorContext, step]
                        };
                        actions.push(action);
                    }
                    
                    return actions;
                }
            }
        );

        // Auto-dispose after 5 minutes
        setTimeout(() => disposable.dispose(), 300000);
    }

    private async applyQuickFix(errorContext: ErrorContext, analysis: AIResponse): Promise<void> {
        const editor = await vscode.window.showTextDocument(vscode.Uri.file(errorContext.filePath));
        
        // Simple implementation - could be enhanced with more sophisticated code manipulation
        const position = new vscode.Position(errorContext.lineNumber - 1, 0);
        const comment = `// AI Fix: ${analysis.solution_approach}\n`;
        
        await editor.edit(editBuilder => {
            editBuilder.insert(position, comment);
        });

        vscode.window.showInformationMessage('Quick fix applied! Review and modify as needed.');
    }

    public async openErrorGuide(errorType: string): Promise<void> {
        const guideUri = vscode.Uri.file(
            path.join(this.context.extensionPath, '..', 'docs', 'ERROR_PREVENTION_GUIDE.md')
        );
        
        try {
            await vscode.window.showTextDocument(guideUri);
        } catch (error) {
            vscode.window.showErrorMessage('Error guide not found');
        }
    }

    private async handleDiagnosticChanges(event: vscode.DiagnosticChangeEvent): Promise<void> {
        // Handle diagnostic changes for real-time error analysis
        for (const uri of event.uris) {
            const diagnostics = vscode.languages.getDiagnostics(uri);
            const errors = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error);
            
            if (errors.length > 0 && this.shouldAnalyzeErrors()) {
                const document = await vscode.workspace.openTextDocument(uri);
                for (const error of errors) {
                    await this.analyzeError(document, error);
                }
            }
        }
    }

    public async showDashboard(): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'aiDebugDashboard',
            'AI Debug Dashboard',
            vscode.ViewColumn.One,
            { enableScripts: true }
        );

        panel.webview.html = this.generateDashboardHTML();
    }

    private generateDashboardHTML(): string {
        const errorStats = this.calculateErrorStats();
        
        return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Debug Dashboard</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .card {
            background: var(--vscode-panel-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 20px;
        }
        .metric {
            text-align: center;
            margin: 10px 0;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--vscode-charts-blue);
        }
        .metric-label {
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <h1>🤖 AI Debug Dashboard</h1>
    
    <div class="dashboard-grid">
        <div class="card">
            <h3>📊 Error Statistics</h3>
            <div class="metric">
                <div class="metric-value">${errorStats.totalErrors}</div>
                <div class="metric-label">Total Errors Analyzed</div>
            </div>
            <div class="metric">
                <div class="metric-value">${errorStats.averageConfidence}%</div>
                <div class="metric-label">Average AI Confidence</div>
            </div>
        </div>
        
        <div class="card">
            <h3>🎯 Most Common Errors</h3>
            ${errorStats.commonErrors.map(error => 
                `<div style="margin: 10px 0;">
                    <strong>${error.type}</strong>: ${error.count} occurrences
                </div>`
            ).join('')}
        </div>
        
        <div class="card">
            <h3>⚙️ Configuration</h3>
            <div><strong>Model:</strong> ${this.config.defaultModel}</div>
            <div><strong>Mode:</strong> ${this.config.debuggingMode}</div>
            <div><strong>Expertise:</strong> ${this.config.expertiseLevel}</div>
            <div><strong>Privacy Mode:</strong> ${this.config.privacyMode ? 'Enabled' : 'Disabled'}</div>
        </div>
    </div>
</body>
</html>`;
    }

    private calculateErrorStats() {
        const totalErrors = this.errorHistory.length;
        const errorCounts: { [key: string]: number } = {};
        
        for (const error of this.errorHistory) {
            errorCounts[error.errorType] = (errorCounts[error.errorType] || 0) + 1;
        }
        
        const commonErrors = Object.entries(errorCounts)
            .map(([type, count]) => ({ type, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);
        
        return {
            totalErrors,
            averageConfidence: 85, // Placeholder - would calculate from actual analyses
            commonErrors
        };
    }

    public dispose(): void {
        this.outputChannel.dispose();
        this.diagnosticCollection.dispose();
    }
}

// Extension activation
export function activate(context: vscode.ExtensionContext) {
    console.log('AI Debug Assistant is now active!');
    
    const assistant = new AIDebugAssistant(context);
    
    // Register commands
    const commands = [
        vscode.commands.registerCommand('ai-debug.startDebugging', () => {
            vscode.window.showInformationMessage('AI Debug Session Started!');
        }),
        
        vscode.commands.registerCommand('ai-debug.analyzeError', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }
            
            const diagnostics = vscode.languages.getDiagnostics(editor.document.uri);
            const errors = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error);
            
            if (errors.length === 0) {
                vscode.window.showInformationMessage('No errors found in current file');
                return;
            }
            
            for (const error of errors) {
                await assistant.analyzeError(editor.document, error);
            }
        }),
        
        vscode.commands.registerCommand('ai-debug.openErrorGuide', () => {
            assistant.openErrorGuide('general');
        }),
        
        vscode.commands.registerCommand('ai-debug.toggleAssistant', () => {
            const config = vscode.workspace.getConfiguration('ai-debug');
            const enabled = config.get('enabled', true);
            config.update('enabled', !enabled, vscode.ConfigurationTarget.Global);
            vscode.window.showInformationMessage(`AI Debug Assistant ${!enabled ? 'enabled' : 'disabled'}`);
        }),
        
        vscode.commands.registerCommand('ai-debug.requestHelp', () => {
            vscode.window.showInformationMessage('AI Help requested! Feature coming soon.');
        }),
        
        vscode.commands.registerCommand('ai-debug.showDashboard', () => {
            assistant.showDashboard();
        }),
        
        vscode.commands.registerCommand('ai-debug.treeOfThoughts', () => {
            vscode.window.showInformationMessage('Tree of Thoughts analysis starting...');
        }),
        
        vscode.commands.registerCommand('ai-debug.reactDebugging', () => {
            vscode.window.showInformationMessage('ReAct debugging mode activated!');
        })
    ];
    
    // Add all disposables to context
    commands.forEach(cmd => context.subscriptions.push(cmd));
    context.subscriptions.push(assistant);
    
    // Show welcome message
    vscode.window.showInformationMessage(
        'AI Debug Assistant is ready! Use Ctrl+Shift+A to analyze errors.',
        'Open Dashboard'
    ).then(selection => {
        if (selection === 'Open Dashboard') {
            assistant.showDashboard();
        }
    });
}

export function deactivate() {
    console.log('AI Debug Assistant deactivated');
}
