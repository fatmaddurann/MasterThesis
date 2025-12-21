import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering - prevents static optimization
// This ensures Vercel treats this as a serverless function
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;

function agentLog(payload: any) {
  if (process.env.NODE_ENV === 'production' && !process.env.ALLOW_DEBUG_LOGS) return;
  // #region agent log
  fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).catch(()=>{});
  // #endregion
}

export async function POST(request: NextRequest) {
  // #region agent log
  const t0 = Date.now();
  agentLog({location:'api/upload/route.ts:POST',message:'Entry',data:{url:request.url,method:request.method},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'upload-403-G'});
  // #endregion
  
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
    // #region agent log
    agentLog({location:'api/upload/route.ts:POST',message:'FormData parsed',data:{hasFile:!!file,fileName:file?.name,fileSize:file?.size},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'upload-404-D'});
    // #endregion

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
    // #region agent log
    agentLog({location:'api/upload/route.ts:POST',message:'Before backend fetch',data:{endpoint,fileSize:file.size},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'upload-404-D'});
    // #endregion

    // Forward the file to the backend (keep original FormData with 'video' field)
    const backendRes = await fetch(endpoint, {
      method: 'POST',
      body: formData, // Forward FormData as-is
      signal: AbortSignal.timeout(300000), // 5 minutes for large uploads
    });
    // #region agent log
    const dt = Date.now() - t0;
    agentLog({location:'api/upload/route.ts:POST',message:'After backend fetch',data:{status:backendRes.status,ok:backendRes.ok,dt_ms:dt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'upload-404-D'});
    // #endregion

    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({}));
      // #region agent log
      agentLog({location:'api/upload/route.ts:POST',message:'Backend error',data:{status:backendRes.status,errorData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'upload-404-D'});
      // #endregion
      return NextResponse.json(
        { error: errorData.detail || `Backend error: ${backendRes.status}` },
        { status: backendRes.status }
      );
    }

    const result = await backendRes.json();
    // #region agent log
    agentLog({location:'api/upload/route.ts:POST',message:'Success',data:{status:result.status,id:result.id},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'upload-404-D'});
    // #endregion
    return NextResponse.json(result);
  } catch (error) {
    // #region agent log
    const dt = Date.now() - t0;
    agentLog({location:'api/upload/route.ts:POST',message:'Catch',data:{name:error instanceof Error?error.name:'Unknown',message:error instanceof Error?error.message:String(error),dt_ms:dt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'upload-404-D'});
    // #endregion
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
