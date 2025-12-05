import type { NextApiRequest, NextApiResponse } from 'next';

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb',
    },
    externalResolver: true,
  },
};

const BACKEND_URL = "https://masterthesis-zk8l.onrender.com/api/live/frame";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Handle CORS manually for Pages Router
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    res.status(200).json({ 
      message: "Live Proxy API (Pages Router) is running. Use POST to send frames.",
      status: "active"
    });
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const backendRes = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
      signal: AbortSignal.timeout(60000),
    });

    if (!backendRes.ok) {
      let errorData: any;
      try {
        errorData = await backendRes.json();
      } catch {
        errorData = { error: `Backend status: ${backendRes.status}` };
      }
      
      // If backend returns 404, map it to 502 to distinguish from frontend 404
      const statusToReturn = backendRes.status === 404 ? 502 : backendRes.status;
      
      res.status(statusToReturn).json({
        detections: [],
        error: errorData.error || errorData.detail || `Backend error: ${backendRes.status}`,
        source: 'backend'
      });
      return;
    }

    const result = await backendRes.json();
    res.status(200).json(result);

  } catch (error: any) {
    const message = error?.message || "Internal server error";
    
    if (message.includes("timeout") || message.includes("aborted")) {
      res.status(504).json({
        detections: [],
        error: "Request timeout. Backend is warming up, please try again.",
      });
      return;
    }

    res.status(500).json({ 
      detections: [], 
      error: "Proxy error while calling backend" 
    });
  }
}
