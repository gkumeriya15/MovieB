/**
 * MovieBox API Proxy Worker
 *
 * Proxies requests to the MovieBox FastAPI backend with caching
 */

const BACKEND_URL = 'https://your-render-api.onrender.com'; // Replace with your Render URL

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Only proxy API routes
    if (!url.pathname.startsWith('/api/')) {
      return new Response('Not Found', { status: 404 });
    }

    // Construct backend URL
    const backendUrl = BACKEND_URL + url.pathname + url.search;

    // Check cache first
    const cache = caches.default;
    let response = await cache.match(request);

    if (response) {
      // Add cache header to indicate hit
      response = new Response(response.body, response);
      response.headers.set('X-Cache-Status', 'HIT');
      return response;
    }

    try {
      // Fetch from backend
      response = await fetch(backendUrl, {
        method: request.method,
        headers: {
          ...request.headers,
          'User-Agent': 'MovieBox-API-Proxy/1.0',
          // Remove headers that might cause issues
          'Host': undefined,
          'CF-RAY': undefined,
          'CF-Visitor': undefined,
          'CF-IPCountry': undefined,
          'CF-Request-ID': undefined,
        },
        body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      });

      // Clone response for caching
      const responseClone = response.clone();

      // Cache successful GET responses for 1 hour
      if (request.method === 'GET' && response.status === 200) {
        responseClone.headers.set('Cache-Control', 's-maxage=3600');
        ctx.waitUntil(cache.put(request, responseClone));
      }

      // Add cache status header
      response.headers.set('X-Cache-Status', 'MISS');
      response.headers.set('Access-Control-Allow-Origin', '*');
      response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      response.headers.set('Access-Control-Allow-Headers', '*');

      return response;

    } catch (error) {
      console.error('Proxy error:', error);

      return new Response(JSON.stringify({
        success: false,
        error: 'Backend service unavailable',
        message: error.message
      }), {
        status: 503,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        }
      });
    }
  }
};