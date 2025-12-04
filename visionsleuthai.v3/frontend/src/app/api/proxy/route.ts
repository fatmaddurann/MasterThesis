import { NextRequest, NextResponse } from "next/server";

export const dynamic = 'force-dynamic'; // static olmasını engelle
export const runtime = 'nodejs';
export const revalidate = 0;

const BACKEND_URL = "https://masterthesis-zk8l.onrender.com/api/live/frame";

export async function POST(request: NextRequest) {
  console.log('[AppRouter-Proxy] Received request');
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
    } else {
      // Fallback for others
      const text = await request.text();
      backendRequestInit.headers = { "Content-Type": "application/json" };
      backendRequestInit.body = text;
    }

    backendRequestInit.signal = AbortSignal.timeout(30000);

    console.log(`[AppRouter-Proxy] Forwarding to: ${BACKEND_URL}`);
    const backendRes = await fetch(BACKEND_URL, backendRequestInit);

    if (!backendRes.ok) {
      let errorData: any;
      try {
        errorData = await backendRes.json();
      } catch {
        errorData = { error: `Backend status: ${backendRes.status}` };
      }
      console.error('[AppRouter-Proxy] Backend error:', errorData);
      return NextResponse.json(errorData, { status: backendRes.status });
    }

    const result = await backendRes.json();
    return NextResponse.json(result, { status: 200 });

  } catch (error: any) {
    console.error('[AppRouter-Proxy] Error:', error);
    return NextResponse.json(
      { error: error.message || "Proxy error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ 
    status: "ok", 
    router: "app-router", 
    path: "/api/proxy" 
  });
}

