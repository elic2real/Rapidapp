export class TemplateEngine {
    generatePackageJson(appSpec, framework = 'nextjs', dbType = 'postgres') {
        const dependencies = {
            nextjs: {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "@types/node": "^20.0.0",
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "typescript": "^5.0.0",
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0",
                "eslint": "^8.0.0",
                "eslint-config-next": "^14.0.0"
            },
            vue: {
                "vue": "^3.3.0",
                "@vitejs/plugin-vue": "^4.0.0",
                "vite": "^4.0.0",
                "typescript": "^5.0.0",
                "@vue/tsconfig": "^0.4.0"
            }
        };

        // Add database dependencies
        if (dbType === 'postgres') {
            dependencies[framework]["@prisma/client"] = "^5.0.0";
            dependencies[framework]["prisma"] = "^5.0.0";
        } else if (dbType === 'mongodb') {
            dependencies[framework]["mongodb"] = "^5.0.0";
            dependencies[framework]["mongoose"] = "^7.0.0";
        } else if (dbType === 'redis') {
            dependencies[framework]["redis"] = "^4.0.0";
        }

        // Add authentication dependencies
        if (appSpec.authentication) {
            dependencies[framework]["next-auth"] = "^4.24.0";
            dependencies[framework]["bcryptjs"] = "^2.4.3";
            dependencies[framework]["@types/bcryptjs"] = "^2.4.0";
        }

        // Add real-time dependencies
        if (appSpec.realTime) {
            dependencies[framework]["socket.io"] = "^4.7.0";
            dependencies[framework]["socket.io-client"] = "^4.7.0";
        }

        const scripts = {
            nextjs: {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                "type-check": "tsc --noEmit"
            },
            vue: {
                "dev": "vite",
                "build": "vue-tsc && vite build",
                "preview": "vite preview"
            }
        };

        if (dbType === 'postgres') {
            scripts[framework]["db:generate"] = "prisma generate";
            scripts[framework]["db:push"] = "prisma db push";
            scripts[framework]["db:migrate"] = "prisma migrate dev";
        }

        return JSON.stringify({
            name: appSpec.name.toLowerCase().replace(/\s+/g, '-'),
            version: "1.0.0",
            description: appSpec.description,
            scripts: scripts[framework],
            dependencies: dependencies[framework],
            keywords: appSpec.features.map(f => f.toLowerCase().replace(/\s+/g, '-')),
            author: "Rapidapp AI Generator",
            license: "MIT"
        }, null, 2);
    }

    generateNextConfig(appSpec) {
        return `/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
  },
  ${appSpec.realTime ? `
  webpack: (config) => {
    config.externals.push({
      'utf-8-validate': 'commonjs utf-8-validate',
      'bufferutil': 'commonjs bufferutil',
    });
    return config;
  },` : ''}
}

module.exports = nextConfig`;
    }

    generateTailwindConfig() {
        return `/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}`;
    }

    generatePostcssConfig() {
        return `module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}`;
    }

    generateLayout(appSpec) {
        return `import './globals.css'
import { Inter } from 'next/font/google'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: '${appSpec.name}',
  description: '${appSpec.description}',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  )
}`;
    }

    generateHomePage(appSpec) {
        const features = appSpec.features.slice(0, 6);
        
        return `import { Button } from '@/components/Button'
import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Welcome to ${appSpec.name}
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          ${appSpec.description}
        </p>
        <div className="space-x-4">
          <Button asChild>
            <Link href="/dashboard">Get Started</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/about">Learn More</Link>
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          ${features.map(feature => `
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3">${feature}</h3>
            <p className="text-gray-600">
              Experience the power of ${feature.toLowerCase()} in our modern application.
            </p>
          </div>`).join('')}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-50 py-16 px-8 rounded-lg text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
        <p className="text-lg text-gray-600 mb-8">
          Join thousands of users who are already using ${appSpec.name}.
        </p>
        <Button size="lg" asChild>
          <Link href="/register">Sign Up Now</Link>
        </Button>
      </section>
    </div>
  )
}`;
    }

    generateGlobalCSS(appSpec) {
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
        
        return `export default function ${pageTitle}Page() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">${pageTitle}</h1>
        
        <div className="bg-white rounded-lg shadow-md p-8">
          <p className="text-lg text-gray-600 mb-6">
            Welcome to the ${pageTitle.toLowerCase()} page of ${appSpec.name}.
          </p>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-semibold mb-4">Features</h2>
              <ul className="space-y-2">
                ${appSpec.features.slice(0, 4).map(feature => `
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  ${feature}
                </li>`).join('')}
              </ul>
            </div>
            
            <div>
              <h2 className="text-2xl font-semibold mb-4">Information</h2>
              <p className="text-gray-600">
                This ${pageTitle.toLowerCase()} page is part of your ${appSpec.name} application.
                It's built with modern technologies and best practices.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}`;
    }

    generateDashboardPage(appSpec) {
        return `import { Card } from '@/components/Card'
import { Button } from '@/components/Button'

export default function DashboardPage() {
  const stats = [
    { label: 'Total Users', value: '1,234', change: '+12%' },
    { label: 'Active Sessions', value: '89', change: '+5%' },
    { label: 'Revenue', value: '$12,345', change: '+23%' },
    { label: 'Conversion Rate', value: '3.2%', change: '+8%' },
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your ${appSpec.name}.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-sm text-green-600">{stat.change}</p>
              </div>
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                📊
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-8">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            ${appSpec.features.slice(0, 3).map(feature => `
            <Button variant="outline" className="w-full justify-start">
              ⚡ ${feature}
            </Button>`).join('')}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                👤
              </div>
              <div>
                <p className="font-medium">New user registered</p>
                <p className="text-sm text-gray-600">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                💰
              </div>
              <div>
                <p className="font-medium">Payment received</p>
                <p className="text-sm text-gray-600">1 hour ago</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}`;
    }

    generateLoginPage(appSpec) {
        return `'use client'

import { useState } from 'react'
import { Input } from '@/components/Input'
import { Button } from '@/components/Button'
import Link from 'next/link'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // TODO: Implement authentication logic
    console.log('Login attempt:', { email, password })
    
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to ${appSpec.name}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link href="/register" className="font-medium text-primary-600 hover:text-primary-500">
              create a new account
            </Link>
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

import Link from 'next/link'
import { useState } from 'react'
import { Button } from './Button'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navigation = [
    { name: 'Home', href: '/' },
    ${appSpec.pages.map(page => `{ name: '${page}', href: '/${page.toLowerCase()}' }`).join(',\n    ')}
  ]

  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-primary-600">
              ${appSpec.name}
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  {item.name}
                </Link>
              ))}
            </div>
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6 space-x-3">
              ${appSpec.authentication ? `
              <Button variant="outline" asChild>
                <Link href="/login">Sign In</Link>
              </Button>
              <Button asChild>
                <Link href="/register">Sign Up</Link>
              </Button>` : `
              <Button asChild>
                <Link href="/contact">Contact</Link>
              </Button>`}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="bg-gray-200 inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-300"
            >
              <span className="sr-only">Open main menu</span>
              {!isMenuOpen ? (
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              ) : (
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="text-gray-600 hover:text-gray-900 block px-3 py-2 rounded-md text-base font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}`;
    }

    generateFooter(appSpec) {
        return `import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          <div className="col-span-2">
            <h3 className="text-lg font-semibold mb-4">${appSpec.name}</h3>
            <p className="text-gray-400 mb-4">
              ${appSpec.description}
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white">
                <span className="sr-only">Twitter</span>
                🐦
              </a>
              <a href="#" className="text-gray-400 hover:text-white">
                <span className="sr-only">GitHub</span>
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
              ${appSpec.pages.slice(0, 4).map(page => `
              <li>
                <Link href="/${page.toLowerCase()}" className="text-gray-400 hover:text-white">
                  ${page}
                </Link>
              </li>`).join('')}
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
        return `import React from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', asChild = false, ...props }, ref) => {
    const Comp = asChild ? 'span' : 'button'
    
    return (
      <Comp
        className={cn(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
          {
            'bg-primary-600 text-white hover:bg-primary-700': variant === 'primary',
            'bg-gray-200 text-gray-900 hover:bg-gray-300': variant === 'secondary',
            'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50': variant === 'outline',
            'text-gray-700 hover:bg-gray-100': variant === 'ghost',
            'h-8 px-3 text-sm': size === 'sm',
            'h-10 px-4': size === 'md',
            'h-12 px-6 text-lg': size === 'lg',
          },
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)

Button.displayName = 'Button'

export { Button }`;
    }

    generateInput() {
        return `import React from 'react'
import { cn } from '@/lib/utils'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)

Input.displayName = 'Input'

export { Input }`;
    }

    generateCard() {
        return `import React from 'react'
import { cn } from '@/lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'rounded-lg border border-gray-200 bg-white text-gray-950 shadow-sm',
        className
      )}
      {...props}
    />
  )
)

Card.displayName = 'Card'

export { Card }`;
    }

    generateGenericComponent(componentName, appSpec) {
        return `interface ${componentName}Props {
  className?: string
  children?: React.ReactNode
}

export default function ${componentName}({ className, children }: ${componentName}Props) {
  return (
    <div className={className}>
      <h2 className="text-2xl font-bold mb-4">${componentName}</h2>
      {children}
    </div>
  )
}`;
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
        appSpec.databaseEntities.forEach(entity => {
            const modelName = entity.charAt(0).toUpperCase() + entity.slice(1);
            schema += `model ${modelName} {
  id        String   @id @default(cuid())
  title     String
  content   String?
  published Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  ${appSpec.authentication ? `userId    String
  user      User     @relation(fields: [userId], references: [id])` : ''}

  @@map("${entity.toLowerCase()}s")
}

`;
        });

        return schema;
    }

    generateAPIRoute(entity, appSpec) {
        const entityName = entity.toLowerCase();
        const EntityName = entity.charAt(0).toUpperCase() + entity.slice(1);

        return `import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(request: NextRequest) {
  try {
    const ${entityName}s = await prisma.${entityName}.findMany({
      orderBy: { createdAt: 'desc' },
      ${appSpec.authentication ? 'include: { user: { select: { id: true, name: true, email: true } } }' : ''}
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
    const { title, content${appSpec.authentication ? ', userId' : ''} } = body

    if (!title) {
      return NextResponse.json(
        { error: 'Title is required' },
        { status: 400 }
      )
    }

    const ${entityName} = await prisma.${entityName}.create({
      data: {
        title,
        content,
        ${appSpec.authentication ? 'userId,' : ''}
      },
      ${appSpec.authentication ? 'include: { user: { select: { id: true, name: true, email: true } } }' : ''}
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
        return JSON.stringify({
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": true,
                "skipLibCheck": true,
                "strict": true,
                "noEmit": true,
                "esModuleInterop": true,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": true,
                "isolatedModules": true,
                "jsx": "preserve",
                "incremental": true,
                "plugins": [
                    {
                        "name": "next"
                    }
                ],
                "baseUrl": ".",
                "paths": {
                    "@/*": ["./src/*"]
                }
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }, null, 2);
    }

    generateESLintConfig() {
        return JSON.stringify({
            "extends": ["next/core-web-vitals"],
            "rules": {
                "prefer-const": "error",
                "no-unused-vars": "warn"
            }
        }, null, 2);
    }

    generateGitignore() {
        return `# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Next.js
/.next/
/out/

# Production
/build

# Environment variables
.env*.local

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Database
*.db
*.sqlite

# Prisma
/prisma/migrations/
`;
    }

    generateREADME(appSpec) {
        return `# ${appSpec.name}

${appSpec.description}

## ✨ Features

${appSpec.features.map(feature => `- ${feature}`).join('\n')}

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- PostgreSQL database

### Installation

1. Clone this repository
\`\`\`bash
git clone <repository-url>
cd ${appSpec.name.toLowerCase().replace(/\s+/g, '-')}
\`\`\`

2. Install dependencies
\`\`\`bash
npm install
\`\`\`

3. Set up environment variables
\`\`\`bash
cp .env.example .env.local
\`\`\`

4. Set up the database
\`\`\`bash
npx prisma generate
npx prisma db push
\`\`\`

5. Start the development server
\`\`\`bash
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 📁 Project Structure

\`\`\`
src/
├── app/                 # Next.js 13+ app directory
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── api/            # API routes
├── components/         # Reusable components
├── lib/               # Utility functions
└── types/             # TypeScript types
\`\`\`

## 🛠️ Built With

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL with Prisma
- **Language**: TypeScript
- **Authentication**: ${appSpec.authentication ? 'NextAuth.js' : 'Not included'}

## 📦 Scripts

- \`npm run dev\` - Start development server
- \`npm run build\` - Build for production
- \`npm run start\` - Start production server
- \`npm run lint\` - Run ESLint
- \`npm run type-check\` - Run TypeScript type checking

## 🚀 Deployment

This app can be deployed on platforms like:

- [Vercel](https://vercel.com)
- [Netlify](https://netlify.com)
- [Railway](https://railway.app)
- [Render](https://render.com)

## 📝 License

This project is licensed under the MIT License.

---

**Generated with ❤️ by Rapidapp AI Generator**
`;
    }

    // Additional methods for other frameworks...
    
    generateRequirements(appSpec) {
        return `fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
sqlalchemy==2.0.23
${appSpec.authentication ? 'python-jose[cryptography]==3.3.0\npasslib[bcrypt]==1.7.4' : ''}
${appSpec.databaseEntities.length > 0 ? 'psycopg2-binary==2.9.7' : ''}
python-multipart==0.0.6
python-dotenv==1.0.0`;
    }

    generateFastAPIMain(appSpec) {
        return `from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="${appSpec.name} API",
    description="${appSpec.description}",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to ${appSpec.name} API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers here
${appSpec.databaseEntities.map(entity => `# app.include_router(${entity.toLowerCase()}.router, prefix="/api/${entity.toLowerCase()}s", tags=["${entity.toLowerCase()}s"])`).join('\n')}
`;
    }

    generateFastAPIConfig(appSpec) {
        return `from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "${appSpec.name}"
    debug: bool = True
    database_url: str = "postgresql://user:password@localhost/dbname"
    secret_key: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"

settings = Settings()`;
    }
}