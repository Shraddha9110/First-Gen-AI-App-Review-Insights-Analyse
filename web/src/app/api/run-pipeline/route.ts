import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    const { weeks = 8, max_reviews = 50, api_key } = await req.json();
    const geminiKey = api_key || process.env.GEMINI_API_KEY;

    if (!geminiKey) {
        return NextResponse.json({ error: "GEMINI_API_KEY is not set" }, { status: 500 });
    }

    // Read sample reviews from a static JSON embedded here (since filesystem access
    // is limited in Vercel serverless functions)
    const sampleReviews = [
        { rating: 5, text: "Great app! Portfolio tracking is excellent." },
        { rating: 1, text: "App crashes constantly after the latest update." },
        { rating: 4, text: "Good for SIP investments but KYC is slow." },
        { rating: 2, text: "Customer support is very slow to respond." },
        { rating: 5, text: "Best investment app in India. Love the interface." },
        { rating: 3, text: "App is okay but sometimes shows wrong portfolio values." },
        { rating: 1, text: "Login keeps failing, very frustrating experience." },
        { rating: 4, text: "Mutual fund tracking is superb, UI could be better." },
        { rating: 5, text: "Simple and clean interface, easy to track investments." },
        { rating: 2, text: "App freezes while loading mutual fund data." },
        { rating: 5, text: "Really smooth experience, love the daily gains tracking." },
        { rating: 1, text: "OTP not received, cannot login at all." },
        { rating: 4, text: "Good app, wish it had more detailed fund analysis." },
        { rating: 3, text: "Decent app but withdrawal takes too long." },
        { rating: 5, text: "Amazing app for beginners in mutual funds!" },
    ];

    const reviews = sampleReviews.slice(0, max_reviews);
    const formattedReviews = reviews
        .map((r) => `Rating: ${r.rating} | Review: ${r.text}`)
        .join("\n");

    const prompt = `
Analyze the following ${reviews.length} Play Store reviews for INDMoney (a financial investment app).
Generate a 'Weekly Pulse' report.

Constraints:
1. Max 5 themes.
2. Exactly 3 key user quotes.
3. Exactly 3 action ideas.
4. Total ≤ 250 words. No PII.

Reviews:
${formattedReviews}

Return ONLY valid JSON in this format:
{
  "themes": ["Theme 1", "Theme 2"],
  "quotes": ["Quote 1", "Quote 2", "Quote 3"],
  "actions": ["Action 1", "Action 2", "Action 3"],
  "summary": "Short 1-2 sentence overview"
}`;

    try {
        const geminiRes = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${geminiKey}`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: prompt }] }],
                    generationConfig: { responseMimeType: "application/json" },
                }),
            }
        );

        if (!geminiRes.ok) {
            const err = await geminiRes.json();
            return NextResponse.json(
                { error: `Gemini API error: ${JSON.stringify(err)}` },
                { status: 502 }
            );
        }

        const data = await geminiRes.json();
        const content = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        const result = JSON.parse(content);
        return NextResponse.json(result);
    } catch (e: any) {
        return NextResponse.json({ error: e.message }, { status: 500 });
    }
}
