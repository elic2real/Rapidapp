#!/usr/bin/env node

import { Command } from 'commander';
import inquirer from 'inquirer';
// @ts-ignore - node-fetch ESM import compatibility
import fetch from 'node-fetch';

interface ErrorWithMessage {
  message: string;
}

const program = new Command();

program
  .name('rapidapp-cli')
  .description('CLI for Rapidapp - AI-driven app builder')
  .version('1.0.0');

program
  .command('new')
  .description('Create a new app using AI')
  .argument('<name>', 'App name')
  .option('--stack <stack>', 'Stack to use (nextjs-postgres, fastapi-mongodb, rust-axum-redis)', 'nextjs-postgres')
  .option('--features <features>', 'Comma-separated list of features to include')
  .option('--multi-tenant <type>', 'Multi-tenancy type (shared-schema, separate-db, hybrid)')
  .action(async (name: string, options: any) => {
    console.log(`🚀 Creating new app: ${name}`);
    
    // Interactive prompts for app details
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'description',
        message: 'Describe your app in detail:',
        validate: (input: string) => input.length >= 10 ? true : 'Please provide at least 10 characters'
      },
      {
        type: 'list',
        name: 'stack',
        message: 'Choose your tech stack:',
        choices: [
          { name: 'Next.js + PostgreSQL (Recommended)', value: 'nextjs-postgres' },
          { name: 'Next.js + MongoDB', value: 'nextjs-mongodb' },
          { name: 'FastAPI + PostgreSQL', value: 'fastapi-postgres' },
          { name: 'Vue.js + PostgreSQL', value: 'vue-postgres' },
          { name: 'Rust Axum + PostgreSQL', value: 'rust-axum-postgres' }
        ],
        default: options.stack
      },
      {
        type: 'checkbox',
        name: 'features',
        message: 'Select features to include:',
        choices: [
          { name: 'User Authentication', value: 'auth' },
          { name: 'Admin Dashboard', value: 'admin' },
          { name: 'Real-time Updates', value: 'realtime' },
          { name: 'File Upload', value: 'upload' },
          { name: 'Search & Filtering', value: 'search' },
          { name: 'Dark Mode', value: 'darkmode' },
          { name: 'Email Notifications', value: 'email' },
          { name: 'Payment Integration', value: 'payments' }
        ]
      }
    ]);

    try {
      console.log('\n🤖 Sending request to AI generator...');
      
      // Create detailed description including CLI options
      const fullDescription = `${answers.description}

Tech Stack: ${answers.stack}
Features: ${answers.features.join(', ')}
${options.features ? `Additional Features: ${options.features}` : ''}
${options.multiTenant ? `Multi-tenancy: ${options.multiTenant}` : ''}`;

      // Send request to frontend service
      const response = await fetch('http://localhost:3030/api/generate-app', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: fullDescription,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      console.log('\n✅ App generation started successfully!');
      console.log(`📱 App Name: ${result.appName}`);
      console.log(`🏗️ Stack: ${result.stack}`);
      console.log(`📦 Features: ${result.features.join(', ')}`);
      console.log(`📂 Estimated Files: ${result.fileCount}`);
      console.log(`💾 Estimated Size: ${result.estimatedSize}`);
      console.log(`� App ID: ${result.appId}`);
      
      console.log('\n🔄 Generation in progress...');
      console.log('💻 Open http://localhost:3030 to monitor progress and download when ready!');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('\n❌ Failed to generate app:', errorMessage);
      console.log('\n💡 Make sure the Rapidapp frontend service is running on http://localhost:3030');
      process.exit(1);
    }
  });

program
  .command('generate')
  .alias('g')
  .description('Generate code components for existing app')
  .argument('<type>', 'Type to generate (component, service, api, page)')
  .argument('<name>', 'Name of the component')
  .option('--app-id <id>', 'App ID to add component to')
  .action(async (type: string, name: string, options: any) => {
    console.log(`🔧 Generating ${type}: ${name}`);
    
    if (!options.appId) {
      console.error('❌ App ID is required. Use --app-id flag.');
      process.exit(1);
    }
    
    try {
      // Future implementation: Generate additional components for existing apps
      console.log('🚧 Component generation coming soon!');
      console.log(`Will generate ${type} named ${name} for app ${options.appId}`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Generation failed:', errorMessage);
      process.exit(1);
    }
  });

program
  .command('status')
  .description('Check the status of app generation')
  .argument('<app-id>', 'App ID to check')
  .action(async (appId: string) => {
    try {
      const response = await fetch(`http://localhost:3030/api/app-status/${appId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const status = await response.json();
      
      console.log(`\n📱 App Status: ${appId}`);
      console.log(`🔄 Status: ${status.status}`);
      console.log(`📊 Progress: ${status.progress || 0}%`);
      
      if (status.status === 'completed') {
        console.log('✅ App is ready for download!');
        console.log('💻 Visit http://localhost:3030 to download your app.');
      } else if (status.status === 'failed') {
        console.log('❌ App generation failed:', status.error);
      } else {
        console.log('⏳ App is still being generated...');
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Failed to check status:', errorMessage);
      process.exit(1);
    }
  });

program
  .command('download')
  .description('Download a generated app')
  .argument('<app-id>', 'App ID to download')
  .option('--output <path>', 'Output directory', './downloaded-apps')
  .action(async (appId: string, options: any) => {
    try {
      console.log(`📥 Downloading app: ${appId}`);
      
      const response = await fetch(`http://localhost:3030/api/download-app/${appId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // In a real implementation, this would save the file
      console.log('✅ Download started!');
      console.log('💻 For now, please use the web interface at http://localhost:3030');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Download failed:', errorMessage);
      process.exit(1);
    }
  });

program.parse();