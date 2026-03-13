import { NextRequest, NextResponse } from "next/server";
import nodemailer from "nodemailer";

export async function POST(req: NextRequest) {
    const { email, name = "Team", analysis } = await req.json();

    if (!email || !analysis) {
        return NextResponse.json(
            { error: "Missing recipient email or analysis data" },
            { status: 400 }
        );
    }

    const smtpHost = process.env.SMTP_HOST;
    const smtpPort = parseInt(process.env.SMTP_PORT || "587");
    const smtpUser = process.env.SMTP_USER;
    const smtpPass = process.env.SMTP_PASS;

    if (!smtpHost || !smtpUser || !smtpPass) {
        return NextResponse.json(
            { error: "SMTP credentials are not configured in environment variables" },
            { status: 500 }
        );
    }

    const themes = (analysis.themes || [])
        .map((t: string, i: number) => `${i + 1}. ${t}`)
        .join("\n");
    const quotes = (analysis.quotes || [])
        .map((q: string, i: number) => `${i + 1}. "${q}"`)
        .join("\n");
    const actions = (analysis.actions || [])
        .map((a: string, i: number) => `${i + 1}. ${a}`)
        .join("\n");

    const date = new Date().toLocaleDateString("en-IN", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });

    const body = `Hi ${name},

Here is the weekly pulse for INDMoney based on the latest review analysis.

EXECUTIVE SUMMARY
${analysis.summary}

TOP THEMES
${themes}

REAL USER QUOTES
${quotes}

ACTION IDEAS
${actions}

Best Regards,
INDMoney Product Insights Bot
Generated on: ${date}`;

    try {
        const transporter = nodemailer.createTransport({
            host: smtpHost,
            port: smtpPort,
            secure: false,
            auth: { user: smtpUser, pass: smtpPass },
        });

        await transporter.sendMail({
            from: smtpUser,
            to: email,
            subject: `Weekly Pulse: INDMoney App Review Insights - ${date}`,
            text: body,
        });

        return NextResponse.json({ status: "Email sent successfully" });
    } catch (e: any) {
        return NextResponse.json(
            { error: `Failed to send email: ${e.message}` },
            { status: 500 }
        );
    }
}
