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

function agentLog(payload: any) {
  // Enable in production only if ?agentdebug=1 is in query (but we're server-side, so check env)
  if (process.env.NODE_ENV === 'production' && !process.env.ALLOW_DEBUG_LOGS) return;
  // #region agent log
  fetch('http://127.0.0.1:7243/ingest/fe281e07-c5bd-45a5-a2c9-cda1a466b1c2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).catch(()=>{});
  // #endregion
}

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

  const t0 = Date.now();
  agentLog({location:'live-proxy.ts:handler',message:'Proxy entry',data:{backendUrl:BACKEND_URL,bodySize:JSON.stringify(req.body)?.length||0},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'timeout-B'});

  try {
    agentLog({location:'live-proxy.ts:handler',message:'Before backend fetch',data:{backendUrl:BACKEND_URL},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'timeout-B'});
    const backendRes = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
      signal: AbortSignal.timeout(60000),
    });
    const dt = Date.now() - t0;
    agentLog({location:'live-proxy.ts:handler',message:'After backend fetch',data:{status:backendRes.status,ok:backendRes.ok,dt_ms:dt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'timeout-B'});

    if (!backendRes.ok) {
      let errorData: any;
      try {
        errorData = await backendRes.json();
      } catch {
        errorData = { error: `Backend status: ${backendRes.status}` };
      }
      
             // If backend returns 404, map it to 502 to distinguish from frontend 404
             const statusToReturn = backendRes.status === 404 ? 502 : backendRes.status;
             
             const errorBody = JSON.stringify(errorData).slice(0, 200); // Limit log size
             console.error(`[Proxy Error] Backend returned ${backendRes.status}. Body: ${errorBody}`);

             res.status(statusToReturn).json({
               detections: [],
               error: errorData.error || errorData.detail || `Backend error: ${backendRes.status}`,
               details: errorData,
               source: 'backend'
             });
      return;
    }

    const contentType = backendRes.headers.get('content-type');
    if (contentType && contentType.includes('text/html')) {
      console.error('Backend returned HTML instead of JSON (Cloudflare/Render Page)');
      res.status(503).json({
        detections: [],
        error: "Backend is warming up (Cloudflare/Render). Please wait 1-2 minutes and try again.",
        source: 'proxy_html_check'
      });
      return;
    }

    const result = await backendRes.json();
    res.status(200).json(result);

  } catch (error: any) {
    const message = error?.message || "Internal server error";
    const dt = Date.now() - t0;
    agentLog({location:'live-proxy.ts:handler',message:'Proxy catch',data:{name:error?.name,message,dt_ms:dt,isTimeout:message.includes('timeout')||message.includes('aborted')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'timeout-B'});
    
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
