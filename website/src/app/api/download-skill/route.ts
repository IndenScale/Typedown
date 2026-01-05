import { NextResponse } from 'next/server';

export async function GET() {
  const SKILL_URL = 'https://raw.githubusercontent.com/IndenScale/typedown/main/skills/typedown/SKILL.md';
  
  try {
    const response = await fetch(SKILL_URL);
    if (!response.ok) throw new Error('Failed to fetch skill file');
    
    const content = await response.text();
    
    return new NextResponse(content, {
      headers: {
        'Content-Type': 'text/markdown',
        'Content-Disposition': 'attachment; filename="skill.md"',
      },
    });
  } catch (error) {
    console.error('Download error:', error);
    return new NextResponse('Failed to download file', { status: 500 });
  }
}
