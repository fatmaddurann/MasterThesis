import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file uploaded' },
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Invalid file type. Allowed types: MP4, MOV, AVI, MKV' },
        { status: 400 }
      );
    }

    // Validate file size (1GB limit)
    const maxSize = 1024 * 1024 * 1024; // 1GB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: 'File too large. Maximum size is 1GB' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!backendUrl) {
      return NextResponse.json(
        { error: 'Backend URL not configured' },
        { status: 500 }
      );
    }

    // Forward the file to the backend
    const backendRes = await fetch(`${backendUrl}/api/video/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Backend error' },
        { status: backendRes.status }
      );
    }

    const result = await backendRes.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
