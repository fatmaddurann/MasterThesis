import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: { videoId: string } }
) {
  // #region agent log
  const t0 = Date.now();
  fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api/analysis/[videoId]/route.ts:GET',message:'Entry',data:{videoId:params.videoId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'video-404-C'})}).catch(()=>{});
  // #endregion
  try {
    const { videoId } = params;
    
    if (!videoId) {
      return NextResponse.json(
        { error: 'Video ID is required' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk8l.onrender.com';
    const endpoint = `${backendUrl}/api/video/analysis/${videoId}`;
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api/analysis/[videoId]/route.ts:GET',message:'Before backend fetch',data:{endpoint},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'video-404-C'})}).catch(()=>{});
    // #endregion
    const backendRes = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    // #region agent log
    const dt = Date.now() - t0;
    fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api/analysis/[videoId]/route.ts:GET',message:'After backend fetch',data:{status:backendRes.status,ok:backendRes.ok,dt_ms:dt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'video-404-C'})}).catch(()=>{});
    // #endregion
    
    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({}));
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api/analysis/[videoId]/route.ts:GET',message:'Backend error',data:{status:backendRes.status,errorData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'video-404-C'})}).catch(()=>{});
      // #endregion
      return NextResponse.json(
        { error: errorData.detail || `Backend error: ${backendRes.status}` },
        { status: backendRes.status }
      );
    }

    const result = await backendRes.json();
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api/analysis/[videoId]/route.ts:GET',message:'Success',data:{status:result.status,hasSummary:!!result.summary},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'video-404-C'})}).catch(()=>{});
    // #endregion
    return NextResponse.json(result);
  } catch (error) {
    // #region agent log
    const dt = Date.now() - t0;
    fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api/analysis/[videoId]/route.ts:GET',message:'Catch',data:{name:error instanceof Error?error.name:'Unknown',message:error instanceof Error?error.message:String(error),dt_ms:dt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'video-404-C'})}).catch(()=>{});
    // #endregion
    console.error('Analysis fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analysis results' },
      { status: 500 }
    );
  }
}
