import { NextResponse } from 'next/server';

export async function GET(request: Request, { params }: { params: { videoId: string } }) {
  // videoId ile backend'den gerçek analiz sonucunu al

 const backendUrl = process.env.NEXT_PUBLIC_API_URL;
 const backendRes = await fetch(`${backendUrl}/analyze-with-context`, {
  method: 'POST',
});
  
  if (!backendRes.ok) {
    return NextResponse.json({ error: 'Backend error' }, { status: 500 });
  }

  const result = await backendRes.json();
  return NextResponse.json(result);
}
