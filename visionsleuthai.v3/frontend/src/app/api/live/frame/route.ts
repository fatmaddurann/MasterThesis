import { NextRequest, NextResponse } from 'next/server';

/**
 * Next.js API proxy route for /api/live/frame
 * This eliminates CORS issues by making the request server-side
 * 
 * Browser -> /api/live/frame (same-origin, no CORS)
 * Next.js Server -> https://masterthesis-zk81.onrender.com/api/live/frame (server-to-server, no CORS)
 */
export async function POST(request: NextRequest) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk81.onrender.com';
    
    if (!backendUrl) {
      return NextResponse.json(
        { error: 'Backend URL not configured' },
        { status: 500 }
      );
    }

    // Get the request body
    const body = await request.json();

    // Forward the request to the backend
    const backendRes = await fetch(`${backendUrl}/api/live/frame`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({
        error: `Backend error: ${backendRes.status} ${backendRes.statusText}`,
      }));
      return NextResponse.json(
        errorData,
        { status: backendRes.status }
      );
    }

    const result = await backendRes.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('Live frame processing error:', error);
    return NextResponse.json(
      { 
        detections: [], 
        error: error instanceof Error ? error.message : 'Internal server error' 
      },
      { status: 500 }
    );
  }
}

/**
 * Handle OPTIONS preflight requests
 * This is not strictly necessary when using Next.js proxy (same-origin),
 * but it's good practice to support it
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

