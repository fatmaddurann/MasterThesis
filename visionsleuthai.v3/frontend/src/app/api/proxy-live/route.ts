import { NextRequest, NextResponse } from "next/server";

// Force dynamic rendering - prevents static optimization
// This ensures Vercel treats this as a serverless function
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;

// Correct Render backend URL (zk8l, not zk81)
const BACKEND_URL = "https://masterthesis-zk8l.onrender.com/api/live/frame";

// #region agent log
const log = (msg: string, data: any = {}, hId: string = "C") => {
  fetch('http://127.0.0.1:7244/ingest/746132e1-320b-4bc1-be3b-dd1c1c5c9fd4', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'proxy-live/route.ts',
      message: msg,
      data: data,
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: hId
    })
  }).catch(() => {});
};
// #endregion

export async function POST(request: NextRequest) {
  const t0 = Date.now();
  log("Proxy request started", { t0 }, "C");
  try {
    const contentType = request.headers.get("content-type") || "";
    let backendRequestInit: RequestInit = {
      method: "POST",
      headers: {},
    };

    if (contentType.includes("application/json")) {
      const body = await request.json();
      backendRequestInit.headers = { "Content-Type": "application/json" };
      backendRequestInit.body = JSON.stringify(body);
    } 
    // ... (existing logic)
    
    log("Forwarding to Render", { url: BACKEND_URL }, "C");
    const backendRes = await fetch(BACKEND_URL, backendRequestInit);
    const dt = Date.now() - t0;
    log("Render responded", { status: backendRes.status, dt_ms: dt }, "C");

    if (!backendRes.ok) {
      let errorData: any;
      try {
        errorData = await backendRes.json();
      } catch {
        errorData = { error: `Backend returned ${backendRes.status} ${backendRes.statusText}` };
      }

      console.error(`[Proxy] Backend error: ${backendRes.status}`, errorData);
      return NextResponse.json(
        {
          detections: [],
          error:
            errorData.error ||
            errorData.detail ||
            `Backend error: ${backendRes.status}`,
        },
        { status: backendRes.status }
      );
    }

    try {
      const result = await backendRes.json();
      return NextResponse.json(result, { status: backendRes.status });
    } catch {
      return NextResponse.json(
        { detections: [], error: "Failed to parse backend response" },
        { status: 500 }
      );
    }
  } catch (error: any) {
    console.error("[Proxy] Internal error:", error);
    const message = error?.message || "Internal server error";

    if (message.includes("timeout") || message.includes("aborted")) {
      return NextResponse.json(
        {
          detections: [],
          error: "Request timeout. Backend may be slow or unavailable.",
        },
        { status: 504 }
      );
    }

    return NextResponse.json(
      { detections: [], error: "Proxy error while calling backend" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { 
      message: "Live Proxy API is running. Use POST to send frames.",
      timestamp: new Date().toISOString(),
      route: "/api/proxy-live",
      target: BACKEND_URL
    },
    { status: 200 }
  );
}

// Explicitly export OPTIONS handler for CORS preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

