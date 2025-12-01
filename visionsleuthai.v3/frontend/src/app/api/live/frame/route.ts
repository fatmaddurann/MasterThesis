import { NextRequest, NextResponse } from 'next/server';

/**
 * Next.js API proxy route for /api/live/frame
 * 
 * ARCHITECTURE:
 * - Browser makes request to: /api/live/frame (same-origin, no CORS needed)
 * - Next.js server forwards to: ${NEXT_PUBLIC_API_URL}/api/live/frame (server-to-server)
 * - This eliminates CORS issues since browser only talks to same-origin Next.js server
 * 
 * ENVIRONMENT VARIABLE:
 * - NEXT_PUBLIC_API_URL should be set to: https://masterthesis-zk81.onrender.com
 * - Falls back to hardcoded URL if env var is not set (for development)
 */
export async function POST(request: NextRequest) {
  try {
    // Get backend URL from environment variable
    // In production (Vercel), this should be set in environment variables
    // In development, it can be set in .env.local
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk81.onrender.com';
    
    if (!backendUrl) {
      console.error('[API Route] Backend URL not configured');
      return NextResponse.json(
        { 
          detections: [], 
          error: 'Backend URL not configured. Please set NEXT_PUBLIC_API_URL environment variable.' 
        },
        { status: 500 }
      );
    }

    // Parse request body
    let body;
    try {
      body = await request.json();
    } catch (parseError) {
      console.error('[API Route] Failed to parse request body:', parseError);
      return NextResponse.json(
        { detections: [], error: 'Invalid request body' },
        { status: 400 }
      );
    }

    // Validate that image data is present
    if (!body || !body.image) {
      return NextResponse.json(
        { detections: [], error: 'Missing image data in request body' },
        { status: 400 }
      );
    }

    // Forward the request to the Render backend
    const backendUrlFull = `${backendUrl.replace(/\/+$/, '')}/api/live/frame`;
    
    console.log(`[API Route] Forwarding request to: ${backendUrlFull}`);
    
    const backendRes = await fetch(backendUrlFull, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      // Add timeout to prevent hanging requests
      signal: AbortSignal.timeout(30000), // 30 second timeout
    });

    // Handle non-OK responses
    if (!backendRes.ok) {
      let errorData;
      try {
        errorData = await backendRes.json();
      } catch {
        errorData = {
          error: `Backend returned ${backendRes.status} ${backendRes.statusText}`,
        };
      }
      
      console.error(`[API Route] Backend error: ${backendRes.status}`, errorData);
      
      return NextResponse.json(
        {
          detections: [],
          error: errorData.error || errorData.detail || `Backend error: ${backendRes.status}`,
        },
        { status: backendRes.status }
      );
    }

    // Parse and return successful response
    try {
      const result = await backendRes.json();
      return NextResponse.json(result);
    } catch (parseError) {
      console.error('[API Route] Failed to parse backend response:', parseError);
      return NextResponse.json(
        { detections: [], error: 'Failed to parse backend response' },
        { status: 500 }
      );
    }
  } catch (error) {
    // Handle network errors, timeouts, etc.
    console.error('[API Route] Request error:', error);
    
    const errorMessage = error instanceof Error 
      ? error.message 
      : 'Internal server error';
    
    // Check if it's a timeout error
    if (errorMessage.includes('timeout') || errorMessage.includes('aborted')) {
      return NextResponse.json(
        { 
          detections: [], 
          error: 'Request timeout. Backend may be slow or unavailable.' 
        },
        { status: 504 }
      );
    }
    
    return NextResponse.json(
      { 
        detections: [], 
        error: `Proxy error: ${errorMessage}` 
      },
      { status: 500 }
    );
  }
}

/**
 * Handle OPTIONS preflight requests
 * Not strictly necessary for same-origin requests, but included for completeness
 */
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '3600',
    },
  });
}

