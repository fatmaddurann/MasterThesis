import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering - prevents static optimization
// This ensures Vercel treats this as a serverless function
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;
export const maxDuration = 300; // 5 minutes for large file uploads

export async function POST(request: NextRequest) {
  
  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
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
  
  try {
    const formData = await request.formData();
    // Frontend sends 'video' field, not 'file'
    const file = formData.get('video') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file uploaded' },
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'];
    const fileExt = file.name.split('.').pop()?.toLowerCase();
    const allowedExts = ['.mp4', '.mov', '.avi', '.mkv'];
    if (!fileExt || !allowedExts.includes(`.${fileExt}`)) {
      return NextResponse.json(
        { error: 'Invalid file type. Allowed types: MP4, MOV, AVI, MKV' },
        { status: 400 }
      );
    }

    // Validate file size (500MB limit to match backend)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: 'File too large. Maximum size is 500MB' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk8l.onrender.com';
    const endpoint = `${backendUrl}/api/video/upload`;

    // Forward the file to the backend (keep original FormData with 'video' field)
    const backendRes = await fetch(endpoint, {
      method: 'POST',
      body: formData, // Forward FormData as-is
      signal: AbortSignal.timeout(300000), // 5 minutes for large uploads
    });

    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || `Backend error: ${backendRes.status}` },
        { status: backendRes.status }
      );
    }

    const result = await backendRes.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
