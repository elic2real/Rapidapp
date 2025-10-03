// test-user-engine.js
// Simulates a test user interacting with the Rapidapp frontend API

import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';

const API_URL = 'http://localhost:3030/api';

async function simulateAppCreation() {
  const description =
    'A demo CRM app with authentication, dashboard, and notifications. Stack: nextjs-postgres';
  const timestamp = new Date().toISOString();
  console.log('Test User: Sending app creation request...');
  try {
    const res = await fetch(`${API_URL}/generate-app`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, timestamp }),
    });
    if (!res.ok) {
      throw new Error(`App creation failed: HTTP ${res.status}`);
    }
    const data = await res.json();
    if (!data.appId) {
      throw new Error('App creation response missing appId');
    }
    console.log('Test User: App creation response:', data);
    return data.appId;
  } catch (error) {
    console.error(
      'Self-Debug: App creation error:',
      error instanceof Error ? error.message : error,
    );
    return null;
  }
}

async function checkStatus(appId) {
  console.log('Test User: Checking app status...');
  try {
    const res = await fetch(`${API_URL}/app-status/${appId}`);
    if (!res.ok) {
      throw new Error(`Status check failed: HTTP ${res.status}`);
    }
    const status = await res.json();
    if (!status.status) {
      throw new Error('Status response missing status field');
    }
    console.log('Test User: Status response:', status);
    return status;
  } catch (error) {
    console.error(
      'Self-Debug: Status check error:',
      error instanceof Error ? error.message : error,
    );
    return { status: 'error', error: error instanceof Error ? error.message : error };
  }
}

async function downloadApp(appId) {
  console.log('Test User: Downloading app...');
  try {
    const res = await fetch(`${API_URL}/download-app/${appId}`);
    if (!res.ok) {
      throw new Error(`Download failed: HTTP ${res.status}`);
    }
    // Simulate saving the file
    const buffer = await res.arrayBuffer();
    const filePath = path.join(process.cwd(), `test-download-${appId}.zip`);
    fs.writeFileSync(filePath, Buffer.from(buffer));
    console.log(`Test User: Download successful. Saved to ${filePath}`);
    return filePath;
  } catch (error) {
    console.error('Self-Debug: Download error:', error instanceof Error ? error.message : error);
    return null;
  }
}

export async function runTestUserEngine() {
  console.log('--- Rapidapp Self-Debugging Test User Engine ---');
  const diagnostics = { errors: [], actions: [] };
  const appId = await simulateAppCreation();
  if (!appId) {
    diagnostics.errors.push('App creation failed.');
    console.log('Diagnostics:', diagnostics);
    return diagnostics;
  }
  diagnostics.actions.push('App created: ' + appId);
  let status;
  for (let i = 0; i < 10; i++) {
    status = await checkStatus(appId);
    if (status.status === 'error') {
      diagnostics.errors.push('Status check error: ' + status.error);
      break;
    }
    if (status.status === 'completed') break;
    await new Promise((r) => setTimeout(r, 2000));
  }
  if (status.status === 'completed') {
    diagnostics.actions.push('App generation completed.');
    const filePath = await downloadApp(appId);
    if (filePath) {
      diagnostics.actions.push('App downloaded: ' + filePath);
    } else {
      diagnostics.errors.push('App download failed.');
    }
  } else {
    diagnostics.errors.push('App generation did not complete in time.');
  }
  console.log('--- Self-Debugging Diagnostics ---');
  console.log(JSON.stringify(diagnostics, null, 2));
  return diagnostics;
}

// If run directly, execute the engine (ESM compatible)
if (
  import.meta.url === process.argv[1] ||
  import.meta.url === `file://${process.cwd()}/test-user-engine.js`
) {
  runTestUserEngine();
}
