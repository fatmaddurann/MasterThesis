import { NextRequest, NextResponse } from "next/server";

// Force dynamic rendering - prevents static optimization
// This ensures Vercel treats this as a serverless function
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;

// Correct Render backend URL (zk8l, not zk81)
const BACKEND_URL = "https://masterthesis-zk8l.onrender.com/api/live/frame";

export async function POST(request: NextRequest) {
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
    } else if (contentType.includes("multipart/form-data")) {
      const formData = await request.formData();
      backendRequestInit.body = formData;
    } else {
      try {
        const body = await request.json();
        backendRequestInit.headers = { "Content-Type": "application/json" };
        backendRequestInit.body = JSON.stringify(body);
      } catch {
        const text = await request.text();
        backendRequestInit.headers = { "Content-Type": "application/json" };
        backendRequestInit.body = text;
      }
    }

    backendRequestInit.signal = AbortSignal.timeout(30000);

    console.log(`[Proxy] Forwarding request to: ${BACKEND_URL}`);
    const backendRes = await fetch(BACKEND_URL, backendRequestInit);

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

