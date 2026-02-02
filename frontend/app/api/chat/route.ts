import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { message, sessionId } = await request.json();

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Simulate AI response for now
    // In a real implementation, you would connect to your AI service here
    const responses = [
      "I understand you're looking for help with RFP automation. Let me help you with that.",
      "That's a great question about RFP processing. I can assist you with scanning tenders and generating responses.",
      "I can help you analyze products and calculate pricing for your RFP responses. What specific RFP are you working on?",
      "For electrical tenders, I recommend starting with a comprehensive technical analysis. Would you like me to guide you through the process?",
      "I can scan tenders from tendersontime.com and help you analyze the requirements. What type of products are you interested in?"
    ];

    const randomResponse = responses[Math.floor(Math.random() * responses.length)];

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    return NextResponse.json({
      response: randomResponse,
      sessionId: sessionId || 'default_session',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
