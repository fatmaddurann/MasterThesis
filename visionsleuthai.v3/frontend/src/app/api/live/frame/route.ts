import { NextRequest, NextResponse } from "next/server";

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

const BACKEND_URL = "https://masterthesis-zk81.onrender.com/api/live/frame";

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

    const backendRes = await fetch(BACKEND_URL, backendRequestInit);

    if (!backendRes.ok) {
      let errorData: any;
      try {
        errorData = await backendRes.json();
      } catch {
        errorData = { error: `Backend returned ${backendRes.status} ${backendRes.statusText}` };
      }

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
    { message: "Live frame API is running. Use POST to send frames." },
    { status: 200 }
  );
}
