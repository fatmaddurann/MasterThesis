import { NextRequest, NextResponse } from 'next/server';

/**
 * Next.js API proxy route for /api/live/frame
 * 
 * ARCHITECTURE:
 * - Browser makes request to: /api/live/frame (same-origin, no CORS needed)
 * - Next.js server forwards to: https://masterthesis-zk81.onrender.com/api/live/frame (server-to-server)
 * - This eliminates CORS issues since browser only talks to same-origin Next.js server
 * 
 * SUPPORTS:
 * - JSON requests (Content-Type: application/json)
 * - Multipart/form-data requests
 */

const BACKEND_URL = 'https://masterthesis-zk81.onrender.com/api/live/frame';

export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type') || '';
    
    // Prepare backend request
    let backendRequestInit: RequestInit = {
      method: 'POST',
      headers: {},
    };

    // Handle JSON requests
    if (contentType.includes('application/json')) {
      try {
        const body = await request.json();
        backendRequestInit.headers = {
          'Content-Type': 'application/json',
        };
        backendRequestInit.body = JSON.stringify(body);
      } catch (parseError) {
        console.error('[API Route] Failed to parse JSON body:', parseError);
        return NextResponse.json(
          { detections: [], error: 'Invalid JSON request body' },
          { status: 400 }
        );
      }
    }
    // Handle multipart/form-data requests
    else if (contentType.includes('multipart/form-data')) {
      try {
        const formData = await request.formData();
        // When using FormData with fetch, don't set Content-Type header
        // Browser/fetch will automatically set it with boundary
        backendRequestInit.body = formData;
      } catch (parseError) {
        console.error('[API Route] Failed to parse form data:', parseError);
        return NextResponse.json(
          { detections: [], error: 'Invalid form data' },
          { status: 400 }
        );
      }
    }
    // Handle other content types (fallback to JSON)
    else {
      try {
        const body = await request.json();
        backendRequestInit.headers = {
          'Content-Type': 'application/json',
        };
        backendRequestInit.body = JSON.stringify(body);
      } catch {
        // If JSON parsing fails, try to get raw body
        const text = await request.text();
        backendRequestInit.headers = {
          'Content-Type': 'application/json',
        };
        backendRequestInit.body = text;
      }
    }

    // Add timeout to prevent hanging requests
    backendRequestInit.signal = AbortSignal.timeout(30000); // 30 second timeout

    console.log(`[API Route] Forwarding ${contentType} request to: ${BACKEND_URL}`);

    // Forward request to backend
    const backendRes = await fetch(BACKEND_URL, backendRequestInit);

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
      return NextResponse.json(result, { status: backendRes.status });
    } catch (parseError) {
      console.error('[API Route] Failed to parse backend response:', parseError);
      return NextResponse.json(
        { detections: [], error: 'Failed to parse backend response' },
        { status: 500 }
      );
    }
  } catch (error) {
    // Handle network errors, timeouts, etc.
    console.error('[API Route] Proxy error:', error);
    
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
        error: 'Proxy error while calling backend' 
      },
      { status: 500 }
    );
  }
}

// Handle GET requests - return 200 OK with info message
export async function GET() {
  return NextResponse.json(
    { message: 'Live frame API is running. Use POST to send frames.' },
    { status: 200 }
  );
}
