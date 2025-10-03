export class TemplateEngine {
  generatePackageJson(appSpec, framework = 'nextjs', dbType = 'postgres') {
    const dependencies = {
      nextjs: {
        next: '^14.0.0',
        react: '^18.0.0',
        'react-dom': '^18.0.0',
        '@types/node': '^20.0.0',
        '@types/react': '^18.0.0',
        '@types/react-dom': '^18.0.0',
        typescript: '^5.0.0',
        tailwindcss: '^3.3.0',
        autoprefixer: '^10.4.0',
        postcss: '^8.4.0',
        eslint: '^8.0.0',
        'eslint-config-next': '^14.0.0',
      },
      vue: {
        vue: '^3.3.0',
        '@vitejs/plugin-vue': '^4.0.0',
        vite: '^4.0.0',
        typescript: '^5.0.0',
        '@vue/tsconfig': '^0.4.0',
      },
    };

    // Add database dependencies
    if (dbType === 'postgres') {
      dependencies[framework]['@prisma/client'] = '^5.0.0';
      dependencies[framework]['prisma'] = '^5.0.0';
    } else if (dbType === 'mongodb') {
      dependencies[framework]['mongodb'] = '^5.0.0';
      dependencies[framework]['mongoose'] = '^7.0.0';
    } else if (dbType === 'redis') {
      dependencies[framework]['redis'] = '^4.0.0';
    }

    // Add authentication dependencies
    if (appSpec.authentication) {
      dependencies[framework]['next-auth'] = '^4.24.0';
      dependencies[framework]['bcryptjs'] = '^2.4.3';
      dependencies[framework]['@types/bcryptjs'] = '^2.4.0';
    }

    // Add real-time dependencies
    if (appSpec.realTime) {
      dependencies[framework]['socket.io'] = '^4.7.0';
      dependencies[framework]['socket.io-client'] = '^4.7.0';
    }

    const scripts = {
      nextjs: {
        dev: 'next dev',
        build: 'next build',
        start: 'next start',
        lint: 'next lint',
        'type-check': 'tsc --noEmit',
      },
      vue: {
        dev: 'vite',
        build: 'vue-tsc && vite build',
        preview: 'vite preview',
      },
    };

    if (dbType === 'postgres') {
      scripts[framework]['db:generate'] = 'prisma generate';
      scripts[framework]['db:push'] = 'prisma db push';
      scripts[framework]['db:migrate'] = 'prisma migrate dev';
    }
    return JSON.stringify({
      name: appSpec.name.toLowerCase().replace(/\s+/g, '-'),
      version: '1.0.0',
      description: appSpec.description,
      scripts: scripts[framework],
      dependencies: dependencies[framework],
      keywords: appSpec.features.map((f) => f.toLowerCase().replace(/\s+/g, '-')),
      author: 'Rapidapp AI Generator',
      license: 'MIT',
    }, null, 2);
  }

  generateGlobalCSS() {
    return `@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    scroll-behavior: smooth;
  }
  
  body {
    @apply text-gray-900 antialiased;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-md font-medium transition-colors;
  }
  
  .btn-primary {
    @apply bg-primary-600 text-white hover:bg-primary-700;
  }
  
  .btn-secondary {
    @apply bg-gray-200 text-gray-900 hover:bg-gray-300;
  }
  
  .input {
    @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
}`;
  }

  generatePage(pageName, appSpec) {
    const pageTitle = pageName.charAt(0).toUpperCase() + pageName.slice(1);

    if (pageName.toLowerCase() === 'dashboard') {
      return this.generateDashboardPage(appSpec);
    }

    if (pageName.toLowerCase() === 'login') {
      return this.generateLoginPage(appSpec);
    }

    return `
<div class=\"container mx-auto px-4 py-8\">
  <div class=\"max-w-4xl mx-auto\">
    <h1 class=\"text-4xl font-bold mb-8\">${pageTitle}</h1>
    <div class=\"bg-white rounded-lg shadow-md p-8\">
      <p class=\"text-lg text-gray-600 mb-6\">
        Welcome to the ${pageTitle.toLowerCase()} page of ${appSpec.name}.
      </p>
      <div class=\"grid md:grid-cols-2 gap-8\">
        <div>
          <h2 class=\"text-2xl font-semibold mb-4\">Features</h2>
          <ul class=\"space-y-2\">
            ${(appSpec.features || []).slice(0, 4).map((feature) => `<li>${feature}</li>`).join('')}
          </ul>
        </div>
        <div>
          <p class=\"font-medium\">Payment received</p>
          <p class=\"text-sm text-gray-600\">1 hour ago</p>
        </div>
      </div>
    </div>
  </div>
</div>
`;
}`;
  }

  generateLoginPage(appSpec) {
    return `
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Sign in to ${appSpec.name}
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or <a href="/register" class="font-medium text-primary-600 hover:text-primary-500">create a new account</a>
      </p>
    </div>
    <form class="mt-8 space-y-6">
      <div class="rounded-md shadow-sm -space-y-px">
        <input class="input" type="email" placeholder="Email address" required />
        <input class="input" type="password" placeholder="Password" required />
      </div>
      <button class="btn btn-primary w-full" type="submit">Sign in</button>
    </form>
  </div>
</div>
`;
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-t-md"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="rounded-b-md"
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <Link href="/forgot-password" className="font-medium text-primary-600 hover:text-primary-500">
                Forgot your password?
              </Link>
            </div>
          </div>

          <div>
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}`;
  }

  generateComponent(componentName, appSpec) {
    switch (componentName) {
      case 'Header':
        return this.generateHeader(appSpec);
      case 'Footer':
        return this.generateFooter(appSpec);
      case 'Button':
        return this.generateButton();
      case 'Input':
        return this.generateInput();
      case 'Card':
        return this.generateCard();
      default:
        return this.generateGenericComponent(componentName, appSpec);
    }
  }

  generateHeader(appSpec) {
    return `'use client'

    return `
<header class="bg-white shadow-sm">
  <nav class="container mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <div class="flex items-center">
        <a href="/" class="text-xl font-bold text-primary-600">
          ${appSpec.name}
        </a>
      </div>
      <div class="hidden md:block ml-10 flex items-baseline space-x-4">
        <a href="/">Home</a>
        ${(appSpec.pages || []).map((page) => `<a href="/${page.toLowerCase()}">${page}</a>`).join('')}
      </div>
      <div class="hidden md:block ml-4 flex items-center md:ml-6 space-x-3">
        ${appSpec.authentication ? `<a href="/login">Sign In</a> <a href="/register">Sign Up</a>` : `<a href="/contact">Contact</a>`}
      </div>
    </div>
  </nav>
</header>
`;
  }

  generateFooter(appSpec) {
    return `
<footer class="bg-gray-900 text-white">
  <div class="container mx-auto px-4 py-12">
    <div class="grid md:grid-cols-4 gap-8">
      <div class="col-span-2">
        <h3 class="text-lg font-semibold mb-4">${appSpec.name}</h3>
        <p class="text-gray-400 mb-4">
          ${appSpec.description}
        </p>
        <div class="flex space-x-4">
          <a href="#" class="text-gray-400 hover:text-white">
            <span class="sr-only">Twitter</span>
            🐦
          </a>
          <a href="#" class="text-gray-400 hover:text-white">
            <span class="sr-only">GitHub</span>
                🐙
              </a>
              <a href="#" className="text-gray-400 hover:text-white">
                <span className="sr-only">LinkedIn</span>
                💼
              </a>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              ${appSpec.pages
                .slice(0, 4)
                .map(
                  (page) => `
              <li>
                <Link href="/${page.toLowerCase()}" className="text-gray-400 hover:text-white">
                  ${page}
                </Link>
              </li>`,
                )
                .join('')}
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-4">Support</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/help" className="text-gray-400 hover:text-white">
                  Help Center
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-400 hover:text-white">
                  Contact Us
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-gray-400 hover:text-white">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-gray-400 hover:text-white">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; {new Date().getFullYear()} ${appSpec.name}. All rights reserved.</p>
          <p className="mt-2 text-sm">Built with ❤️ using Rapidapp AI Generator</p>
        </div>
      </div>
    </footer>
  )
}`;
  }

  generateButton() {
    return `<button class="btn btn-primary">Button</button>`;
  }

  generateInput() {
    return `<input class="input" type="text" />`;
  }

  generateCard() {
    return `<div class="card">Card</div>`;
  }

  generateGenericComponent(componentName) {
    return `<div class="${componentName.toLowerCase()}">\n  <h2 class="text-2xl font-bold mb-4">${componentName}</h2>\n  <!-- Add your content here -->\n</div>`;
  }

  generatePrismaSchema(appSpec) {
    let schema = `// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

`;

    // Add User model if authentication is required
    if (appSpec.authentication) {
      schema += `model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  password  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("users")
}

`;
    }

    // Add models for each database entity
    appSpec.databaseEntities.forEach((entity) => {
      const modelName = entity.charAt(0).toUpperCase() + entity.slice(1);
      schema += `model ${modelName} {
  id        String   @id @default(cuid())
  title     String
  content   String?
  published Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  ${
    appSpec.authentication
      ? `userId    String
  user      User     @relation(fields: [userId], references: [id])`
      : ''
  }

  @@map("${entity.toLowerCase()}s")
}

`;
    });

    return schema;
  }

  generateAPIRoute(entity) {
    const entityName = entity.toLowerCase();
    return `import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(request: NextRequest) {
  try {
    const ${entityName}s = await prisma.${entityName}.findMany({
      orderBy: { createdAt: 'desc' }
    })
    return NextResponse.json(${entityName}s)
  } catch (error) {
    console.error('Error fetching ${entityName}s:', error)
    return NextResponse.json(
      { error: 'Failed to fetch ${entityName}s' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { title, content } = body

    if (!title) {
      return NextResponse.json(
        { error: 'Title is required' },
        { status: 400 }
      )
    }

    const ${entityName} = await prisma.${entityName}.create({
      data: {
        title,
        content
      }
    })

    return NextResponse.json(${entityName}, { status: 201 })
  } catch (error) {
    console.error('Error creating ${entityName}:', error)
    return NextResponse.json(
      { error: 'Failed to create ${entityName}' },
      { status: 500 }
    )
  }
}`;
  }

  generateAuthAPI(appSpec) {
    return `import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const { email, password, action } = await request.json()

    if (action === 'login') {
      // Login logic
      const user = await prisma.user.findUnique({
        where: { email }
      })

      if (!user) {
        return NextResponse.json(
          { error: 'Invalid credentials' },
          { status: 401 }
        )
      }

      const isValidPassword = await bcrypt.compare(password, user.password)

      if (!isValidPassword) {
        return NextResponse.json(
          { error: 'Invalid credentials' },
          { status: 401 }
        )
      }

      // Remove password from response
      const { password: _, ...userWithoutPassword } = user

      return NextResponse.json({
        user: userWithoutPassword,
        message: 'Login successful'
      })
    }

    if (action === 'register') {
      // Check if user already exists
      const existingUser = await prisma.user.findUnique({
        where: { email }
      })

      if (existingUser) {
        return NextResponse.json(
          { error: 'User already exists' },
          { status: 400 }
        )
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 12)

      // Create user
      const user = await prisma.user.create({
        data: {
          email,
          password: hashedPassword,
        }
      })

      // Remove password from response
      const { password: _, ...userWithoutPassword } = user

      return NextResponse.json({
        user: userWithoutPassword,
        message: 'Registration successful'
      }, { status: 201 })
    }

    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    )
  } catch (error) {
    console.error('Auth error:', error)
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    )
  }
}`;
  }

  generateEnvFile(appSpec) {
    let env = `# Database
DATABASE_URL="postgresql://username:password@localhost:5432/${appSpec.name.toLowerCase().replace(/\s+/g, '_')}"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"

`;

    if (appSpec.authentication) {
      env += `# Authentication
JWT_SECRET="your-jwt-secret-here"

`;
    }

    if (appSpec.realTime) {
      env += `# Redis (for real-time features)
REDIS_URL="redis://localhost:6379"

`;
    }

    return env;
  }

  generateEnvExample(appSpec) {
    return this.generateEnvFile(appSpec).replace(/=".*"/g, '=""');
  }

  generateTSConfig() {
    return JSON.stringify(
      {
        compilerOptions: {
          target: 'es5',
          lib: ['dom', 'dom.iterable', 'es6'],
          allowJs: true,
          skipLibCheck: true,
          strict: true,
          noEmit: true,
          esModuleInterop: true,
          module: 'esnext',
          moduleResolution: 'bundler',
          resolveJsonModule: true,
          isolatedModules: true,
          jsx: 'preserve',
          incremental: true,
          plugins: [
            {
              name: 'next',
            },
          ],
          baseUrl: '.',
          paths: {
            '@/*': ['./src/*'],
          },
        },
        include: ['next-env.d.ts', '**/*.ts', '**/*.tsx', '.next/types/**/*.ts'],
        exclude: ['node_modules'],
      },
      null,
      2,
    );
  }

  generateESLintConfig() {
    return JSON.stringify(
      {
        extends: ['next/core-web-vitals'],
        rules: {
          'prefer-const': 'error',
          'no-unused-vars': 'warn',
        },
      },
      null,
      2,
    );
  }

  generateAuthAPI(appSpec) {
    // Use appSpec if needed for custom logic
    return `import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const { email, password, action } = await request.json()

    if (action === 'login') {
      // Login logic
      const user = await prisma.user.findUnique({
        where: { email }
      })

      if (!user) {
        return NextResponse.json(
          { error: 'Invalid credentials' },
          { status: 401 }
        )
      }

      const isValidPassword = await bcrypt.compare(password, user.password)

      if (!isValidPassword) {
        return NextResponse.json(
          { error: 'Invalid credentials' },
          { status: 401 }
        )
      }

      // Remove password from response
      const { password: _, ...userWithoutPassword } = user

      return NextResponse.json({
        user: userWithoutPassword,
        message: 'Login successful'
      })
    }

    if (action === 'register') {
      // Check if user already exists
      const existingUser = await prisma.user.findUnique({
        where: { email }
      })

      if (existingUser) {
        return NextResponse.json(
          { error: 'User already exists' },
          { status: 400 }
        )
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 12)

      // Create user
      const user = await prisma.user.create({
        data: {
          email,
          password: hashedPassword,
        }
      })

      // Remove password from response
      const { password: _, ...userWithoutPassword } = user

      return NextResponse.json({
        user: userWithoutPassword,
        message: 'Registration successful'
      }, { status: 201 })
    }

    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    )
  } catch (error) {
    console.error('Auth error:', error)
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    )
  }
}`;
  }

  generateREADME(appSpec) {
    return `# ${appSpec.name}

${appSpec.description}

## ✨ Features

${Array.isArray(appSpec.features) ? appSpec.features.map((feature) => `- ${feature}`).join('\n') : ''}

## 🚀 Getting Started

### Prerequisites


### Installation

1. Clone this repository
\`\`\`bash
git clone <repository-url>
cd ${appSpec.name.toLowerCase().replace(/\s+/g, '-')}
\`\`\`

... (rest of template) ...
`;
  }
}
