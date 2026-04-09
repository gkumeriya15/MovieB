/**
 * MovieBox API Proxy Worker
 *
 * Proxies requests to the MovieBox FastAPI backend with caching and CORS support
 * Environment variables:
 * - BACKEND_URL: Base URL of the FastAPI backend (e.g., https://movieb-rsoz.onrender.com)
 * - CACHE_TTL: Cache time-to-live in seconds (default: 3600)
 */

export default {
  async fetch(request, env, ctx) {
    const BACKEND_URL = env.BACKEND_URL || 'https://movieb-rsoz.onrender.com';
    const CACHE_ENABLED = env.CACHE_ENABLED !== 'false';
    const CACHE_TTL = parseInt(env.CACHE_TTL || '3600', 10);

    const url = new URL(request.url);

    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
          'Access-Control-Max-Age': '86400',
        }
      });
    }

    // Only proxy API routes
    if (!url.pathname.startsWith('/api/')) {
      return new Response('Not Found', { status: 404 });
    }

    // Construct backend URL, preserving query parameters
    const backendUrl = `${BACKEND_URL}${url.pathname}${url.search}`;

    // Check cache for GET requests
    const cache = caches.default;
    let response = null;

    if (CACHE_ENABLED && request.method === 'GET') {
      response = await cache.match(request);
      if (response) {
        // Add cache hit header
        response = new Response(response.body, response);
        response.headers.set('X-Cache-Status', 'HIT');
        response.headers.set('Access-Control-Allow-Origin', '*');
        return response;
      }
    }

    try {
      // Prepare headers for backend request
      const fetchHeaders = new Headers(request.headers);
      
      // Remove problematic headers
      const headersToRemove = [
        'Host',
        'CF-RAY',
        'CF-Visitor',
        'CF-IPCountry',
        'CF-Request-ID',
        'CF-Connecting-IP',
        'CF-Threat-Score',
        'CF-Bot-Management-Score'
      ];
      
      headersToRemove.forEach(header => {
        fetchHeaders.delete(header);
      });

      // Fetch from backend
      response = await fetch(backendUrl, {
        method: request.method,
        headers: fetchHeaders,
        body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      });

      // Only cache successful GET responses
      if (CACHE_ENABLED && request.method === 'GET' && response.status === 200) {
        const responseToCache = response.clone();
        responseToCache.headers.set('Cache-Control', `s-maxage=${CACHE_TTL}`);
        ctx.waitUntil(cache.put(request, responseToCache));
      }

      // Clone response to add headers
      response = new Response(response.body, response);
      response.headers.set('X-Cache-Status', 'MISS');
      response.headers.set('Access-Control-Allow-Origin', '*');
      response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
      response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
      
      return response;

    } catch (error) {
      console.error('Proxy error:', error);

      return new Response(JSON.stringify({
        success: false,
        error: 'Backend service unavailable',
        details: error.message,
        timestamp: new Date().toISOString()
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