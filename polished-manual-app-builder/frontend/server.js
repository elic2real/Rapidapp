#!/usr/bin/env node

import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { AppGenerator } from './app-generator.js';
import { AIOrchestrator } from './ai-orchestrator.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = process.env.PORT || 3030;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// Initialize services
const appGenerator = new AppGenerator();
const aiOrchestrator = new AIOrchestrator();

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'rapidapp-frontend',
    timestamp: new Date().toISOString(),
  });
});

app.post('/api/generate-app', async (req, res) => {
  try {
    const { description } = req.body;

    if (!description || !description.trim()) {
      return res.status(400).json({
        error: 'App description is required',
      });
    }

    console.log(`🚀 New app generation request: ${description.substring(0, 100)}...`);

    // Use AI to analyze the request and generate app specification
    const appSpec = await aiOrchestrator.analyzeAppRequest(description);

    // Generate unique app ID
    const appId = `app_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Start app generation process (async)
    appGenerator
      .generateApp(appId, appSpec)
      .then(() => {
        console.log(`✅ App generation completed for: ${appId}`);
      })
      .catch((error) => {
        console.error(`❌ App generation failed for ${appId}:`, error);
      });

    // Return immediate response with app details
    res.json({
      appId,
      appName: appSpec.name,
      description: appSpec.description,
      stack: appSpec.stack,
      features: appSpec.features,
      fileCount: appSpec.estimatedFiles,
      estimatedSize: appSpec.estimatedSize,
      status: 'generating',
    });
  } catch (error) {
    console.error('App generation error:', error);
    res.status(500).json({
      error: 'Failed to start app generation',
      details: error.message,
    });
  }
});

app.get('/api/app-status/:appId', async (req, res) => {
  try {
    const { appId } = req.params;
    const status = await appGenerator.getGenerationStatus(appId);
    res.json(status);
  } catch (error) {
    res.status(404).json({ error: 'App not found' });
  }
});

app.get('/api/download-app/:appId', async (req, res) => {
  try {
    const { appId } = req.params;
    const zipBuffer = await appGenerator.downloadApp(appId);

    res.set({
      'Content-Type': 'application/zip',
      'Content-Disposition': `attachment; filename="${appId}.zip"`,
      'Content-Length': zipBuffer.length,
    });

    res.send(zipBuffer);
  } catch (error) {
    console.error('Download error:', error);
    res.status(404).json({ error: 'App not found or not ready' });
  }
});

app.listen(port, () => {
  console.log(`🌐 Rapidapp Frontend Server running on http://localhost:${port}`);
  console.log(`🎯 Ready to generate apps via AI!`);
});

export default app;
