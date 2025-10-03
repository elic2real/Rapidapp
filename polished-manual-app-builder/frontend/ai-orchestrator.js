import fetch from 'node-fetch';

export class AIOrchestrator {
  constructor() {
    this.orchestratorUrl = process.env.ORCHESTRATOR_URL || 'http://localhost:8001';
  }

  async analyzeAppRequest(description) {
    try {
      // Create a comprehensive prompt for app specification generation
      const prompt = this.createAppAnalysisPrompt(description);

      // Send request to AI orchestrator service
      const response = await fetch(`${this.orchestratorUrl}/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [
            {
              role: 'system',
              content:
                'You are an expert software architect and product manager. Your job is to analyze app requirements and create detailed technical specifications for modern web applications.',
            },
            {
              role: 'user',
              content: prompt,
            },
          ],
          model: 'llama3.2:3b',
          temperature: 0.7,
          max_tokens: 2048,
        }),
      });

      if (!response.ok) {
        throw new Error(`AI Orchestrator error: ${response.status}`);
      }

      const result = await response.json();
      const aiResponse = result.message.content;

      // Parse AI response into structured app specification
      return this.parseAppSpecification(aiResponse, description);
    } catch (error) {
      console.error('AI analysis failed:', error);
      // Fallback to rule-based analysis
      return this.fallbackAnalysis(description);
    }
  }

  createAppAnalysisPrompt(description) {
    return `
Analyze this app request and create a detailed technical specification:

"${description}"

Please provide a JSON response with the following structure:
{
  "name": "App Name",
  "description": "Brief description",
  "category": "web|mobile|desktop|api",
  "stack": "nextjs-postgres|react-nodejs|vue-mongodb|etc",
  "features": ["feature1", "feature2", "feature3"],
  "pages": ["page1", "page2"],
  "database_entities": ["entity1", "entity2"],
  "api_endpoints": ["GET /api/endpoint1", "POST /api/endpoint2"],
  "styling": "tailwind|css|styled-components",
  "authentication": true|false,
  "real_time": true|false,
  "file_upload": true|false,
  "search": true|false,
  "admin_panel": true|false,
  "complexity": "simple|medium|complex",
  "estimated_files": 25,
  "estimated_size": "2.5MB"
}

Be specific about technical details and modern best practices. Focus on:
1. Appropriate technology stack for the requirements
2. Essential features that match the description
3. Realistic file count and project size
4. Modern UI/UX patterns
5. Scalable architecture choices

Respond with valid JSON only.`;
  }

  parseAppSpecification(aiResponse, originalDescription) {
    try {
      // Try to extract JSON from AI response
      const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);

        // Validate and enhance the response
        return {
          name: parsed.name || this.generateAppName(originalDescription),
          description: parsed.description || originalDescription.substring(0, 100) + '...',
          category: parsed.category || 'web',
          stack: this.normalizeStack(parsed.stack),
          features: parsed.features || this.extractFeatures(originalDescription),
          pages: parsed.pages || ['Home', 'Dashboard'],
          databaseEntities: parsed.database_entities || [],
          apiEndpoints: parsed.api_endpoints || [],
          styling: parsed.styling || 'tailwind',
          authentication: parsed.authentication || false,
          realTime: parsed.real_time || false,
          fileUpload: parsed.file_upload || false,
          search: parsed.search || false,
          adminPanel: parsed.admin_panel || false,
          complexity: parsed.complexity || 'medium',
          estimatedFiles: parsed.estimated_files || 30,
          estimatedSize: parsed.estimated_size || '3.2MB',
        };
      }
    } catch (error) {
      console.warn('Failed to parse AI response, using fallback:', error);
    }

    return this.fallbackAnalysis(originalDescription);
  }

  fallbackAnalysis(description) {
    const lowerDesc = description.toLowerCase();

    // Analyze description for key features
    const features = this.extractFeatures(description);
    const hasAuth = /auth|login|register|user|account/.test(lowerDesc);
    const hasRealTime = /real.?time|live|chat|notification/.test(lowerDesc);
    const hasUpload = /upload|file|image|document/.test(lowerDesc);
    const hasSearch = /search|filter|find/.test(lowerDesc);
    const hasAdmin = /admin|manage|dashboard|control/.test(lowerDesc);

    // Determine stack based on requirements
    let stack = 'nextjs-postgres';
    if (/blog|cms|content/.test(lowerDesc)) stack = 'nextjs-postgres';
    else if (/ecommerce|shop|store/.test(lowerDesc)) stack = 'nextjs-postgres';
    else if (/chat|message|social/.test(lowerDesc)) stack = 'nextjs-redis';
    else if (/api|microservice|backend/.test(lowerDesc)) stack = 'fastapi-postgres';

    // Estimate complexity
    let complexity = 'medium';
    if (features.length <= 3) complexity = 'simple';
    else if (features.length >= 8) complexity = 'complex';

    return {
      name: this.generateAppName(description),
      description: description.substring(0, 150) + (description.length > 150 ? '...' : ''),
      category: 'web',
      stack,
      features,
      pages: this.generatePages(lowerDesc),
      databaseEntities: this.generateEntities(lowerDesc),
      apiEndpoints: this.generateEndpoints(lowerDesc),
      styling: 'tailwind',
      authentication: hasAuth,
      realTime: hasRealTime,
      fileUpload: hasUpload,
      search: hasSearch,
      adminPanel: hasAdmin,
      complexity,
      estimatedFiles: complexity === 'simple' ? 20 : complexity === 'medium' ? 35 : 55,
      estimatedSize:
        complexity === 'simple' ? '1.8MB' : complexity === 'medium' ? '3.2MB' : '5.1MB',
    };
  }

  generateAppName(description) {
    const words = description.split(' ').slice(0, 3);
    let name = words.map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join('');

    // Add "App" if not already present
    if (!name.toLowerCase().includes('app')) {
      name += 'App';
    }

    return name;
  }

  extractFeatures(description) {
    const lowerDesc = description.toLowerCase();
    const features = [];

    // Authentication features
    if (/auth|login|register|user|account|signup/.test(lowerDesc)) {
      features.push('User Authentication');
    }

    // UI/UX features
    if (/dark.?mode|theme/.test(lowerDesc)) {
      features.push('Dark Mode');
    }
    if (/responsive|mobile/.test(lowerDesc)) {
      features.push('Responsive Design');
    }
    if (/drag.?drop|reorder/.test(lowerDesc)) {
      features.push('Drag & Drop');
    }

    // Data features
    if (/database|data|store|save/.test(lowerDesc)) {
      features.push('Data Persistence');
    }
    if (/search|filter|find/.test(lowerDesc)) {
      features.push('Search & Filtering');
    }
    if (/export|download|pdf/.test(lowerDesc)) {
      features.push('Data Export');
    }

    // Real-time features
    if (/real.?time|live|sync|notification/.test(lowerDesc)) {
      features.push('Real-time Updates');
    }
    if (/chat|message|comment/.test(lowerDesc)) {
      features.push('Messaging System');
    }

    // File features
    if (/upload|file|image|document/.test(lowerDesc)) {
      features.push('File Upload');
    }

    // Admin features
    if (/admin|manage|dashboard|control/.test(lowerDesc)) {
      features.push('Admin Dashboard');
    }

    // Business features
    if (/payment|checkout|stripe|paypal/.test(lowerDesc)) {
      features.push('Payment Integration');
    }
    if (/email|notification|alert/.test(lowerDesc)) {
      features.push('Email Notifications');
    }
    if (/analytics|tracking|metrics/.test(lowerDesc)) {
      features.push('Analytics Dashboard');
    }

    // Default features if none detected
    if (features.length === 0) {
      features.push('Modern UI Design', 'Responsive Layout', 'Data Management');
    }

    return features;
  }

  generatePages(description) {
    const pages = ['Home'];

    if (/auth|login|user/.test(description)) {
      pages.push('Login', 'Register', 'Profile');
    }
    if (/dashboard|admin/.test(description)) {
      pages.push('Dashboard');
    }
    if (/about|contact/.test(description)) {
      pages.push('About', 'Contact');
    }
    if (/blog|post|article/.test(description)) {
      pages.push('Blog', 'Article');
    }
    if (/shop|product|store/.test(description)) {
      pages.push('Products', 'Cart', 'Checkout');
    }
    if (/settings|config/.test(description)) {
      pages.push('Settings');
    }

    return pages;
  }

  generateEntities(description) {
    const entities = [];

    if (/user|auth|account/.test(description)) entities.push('User');
    if (/post|blog|article/.test(description)) entities.push('Post');
    if (/product|item|goods/.test(description)) entities.push('Product');
    if (/order|purchase/.test(description)) entities.push('Order');
    if (/comment|review/.test(description)) entities.push('Comment');
    if (/category|tag/.test(description)) entities.push('Category');
    if (/todo|task/.test(description)) entities.push('Task');
    if (/message|chat/.test(description)) entities.push('Message');

    return entities;
  }

  generateEndpoints(description) {
    const endpoints = [];

    if (/user|auth/.test(description)) {
      endpoints.push('POST /api/auth/login', 'POST /api/auth/register', 'GET /api/user/profile');
    }
    if (/post|blog/.test(description)) {
      endpoints.push('GET /api/posts', 'POST /api/posts', 'GET /api/posts/:id');
    }
    if (/product/.test(description)) {
      endpoints.push('GET /api/products', 'GET /api/products/:id');
    }
    if (/order/.test(description)) {
      endpoints.push('POST /api/orders', 'GET /api/orders/:id');
    }

    return endpoints;
  }

  normalizeStack(stack) {
    if (!stack) return 'nextjs-postgres';

    const normalized = stack.toLowerCase();
    if (normalized.includes('next') || normalized.includes('react')) {
      if (normalized.includes('mongo')) return 'nextjs-mongodb';
      if (normalized.includes('redis')) return 'nextjs-redis';
      return 'nextjs-postgres';
    }
    if (normalized.includes('vue')) return 'vue-postgres';
    if (normalized.includes('fastapi') || normalized.includes('python')) return 'fastapi-postgres';
    if (normalized.includes('rust')) return 'rust-axum-postgres';

    return 'nextjs-postgres';
  }
}
