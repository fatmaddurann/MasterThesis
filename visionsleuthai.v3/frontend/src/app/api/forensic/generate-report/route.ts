import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;

function agentLog(payload: any) {
  if (process.env.NODE_ENV === 'production' && !process.env.ALLOW_DEBUG_LOGS) return;
  // #region agent log
  fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).catch(()=>{});
  // #endregion
}

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

export async function POST(request: NextRequest) {
  // #region agent log
  const t0 = Date.now();
  agentLog({location:'api/forensic/generate-report/route.ts:POST',message:'Entry',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'forensic-404-F'});
  // #endregion
  
  try {
    const body = await request.json();
    // #region agent log
    agentLog({location:'api/forensic/generate-report/route.ts:POST',message:'Body parsed',data:{hasDetections:!!body.detections,detectionCount:body.detections?.length||0},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'forensic-404-F'});
    // #endregion

    if (!body.detections) {
      return NextResponse.json(
        { error: 'Missing detections field' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://masterthesis-zk8l.onrender.com';
    const endpoint = `${backendUrl}/api/forensic/generate-report`;
    // #region agent log
    agentLog({location:'api/forensic/generate-report/route.ts:POST',message:'Before backend fetch',data:{endpoint},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'forensic-404-F'});
    // #endregion

    const backendRes = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30000), // 30 seconds
    });
    // #region agent log
    const dt = Date.now() - t0;
    agentLog({location:'api/forensic/generate-report/route.ts:POST',message:'After backend fetch',data:{status:backendRes.status,ok:backendRes.ok,dt_ms:dt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'forensic-404-F'});
    // #endregion

    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({}));
      // #region agent log
      agentLog({location:'api/forensic/generate-report/route.ts:POST',message:'Backend error',data:{status:backendRes.status,errorData},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'forensic-404-F'});
      // #endregion
      return NextResponse.json(
        { error: errorData.detail || `Backend error: ${backendRes.status}` },
        { status: backendRes.status }
      );
    }

    const result = await backendRes.json();
    // #region agent log
    agentLog({location:'api/forensic/generate-report/route.ts:POST',message:'Success',data:{reportLength:result.report?.length||0},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'forensic-404-F'});
    // #endregion
    return NextResponse.json(result, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    // #region agent log
    const dt = Date.now() - t0;
    agentLog({location:'api/forensic/generate-report/route.ts:POST',message:'Catch',data:{name:error instanceof Error?error.name:'Unknown',message:error instanceof Error?error.message:String(error),dt_ms:dt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'forensic-404-F'});
    // #endregion
    console.error('Forensic report generation error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
