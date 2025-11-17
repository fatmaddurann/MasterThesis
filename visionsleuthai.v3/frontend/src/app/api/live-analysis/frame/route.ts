import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL;
  const formData = await request.formData();

  const backendRes = await fetch(`${backendUrl}/analyze-with-context`, {
    method: 'POST',
    body: formData,
  });

  if (!backendRes.ok) {
    return NextResponse.json({ error: 'Backend error' }, { status: 500 });
  }

  const result = await backendRes.json();
  return NextResponse.json(result);
}
