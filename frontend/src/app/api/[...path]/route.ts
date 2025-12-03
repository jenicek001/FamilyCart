/**
 * API Proxy Route
 * 
 * This Next.js API route proxies all /api/* requests to the backend server.
 * It uses runtime environment variables, allowing the same Docker image
 * to work in different environments without rebuilding.
 * 
 * Why this approach:
 * - next.config.js rewrites() are evaluated at build time
 * - API routes run at request time and can read runtime environment variables
 * - This allows true environment-agnostic Docker images
 */

import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

async function proxyRequest(request: NextRequest, pathSegments: string[]) {
  try {
    // Get backend URL from runtime environment variable
    // This works in Docker because the environment variable is set at container startup
    const backendUrl = process.env.API_URL || 'http://localhost:8002';
    
    // Reconstruct the full path
    const path = pathSegments.join('/');
    const url = `${backendUrl}/api/${path}`;
    
    // Get search params from the original request
    const searchParams = request.nextUrl.searchParams.toString();
    const fullUrl = searchParams ? `${url}?${searchParams}` : url;
    
    console.log(`[API Proxy] ${request.method} ${fullUrl}`);
    
    // Forward headers (excluding host and connection headers)
    const headers = new Headers();
    request.headers.forEach((value, key) => {
      if (!['host', 'connection', 'content-length'].includes(key.toLowerCase())) {
        headers.set(key, value);
      }
    });
    
    // Get request body if present
    let body = null;
    if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
      body = await request.text();
    }
    
    // Make the proxied request
    const response = await fetch(fullUrl, {
      method: request.method,
      headers,
      body,
    });
    
    // Get response body
    const responseBody = await response.text();
    
    // Forward response headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      if (!['content-encoding', 'transfer-encoding'].includes(key.toLowerCase())) {
        responseHeaders.set(key, value);
      }
    });
    
    // Return proxied response
    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
    
  } catch (error) {
    console.error('[API Proxy] Error:', error);
    return NextResponse.json(
      { error: 'Failed to proxy request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// Mark as dynamic to ensure runtime execution
export const dynamic = 'force-dynamic';
