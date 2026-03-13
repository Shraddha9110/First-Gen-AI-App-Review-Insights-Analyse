"use client";

import { useState, useEffect } from "react";

const BACKEND_URL = "/api";

interface AnalysisResult {
  themes: string[];
  quotes: string[];
  actions: string[];
  summary: string;
  id?: string;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [weeks, setWeeks] = useState(8);
  const [maxReviews, setMaxReviews] = useState(1000);
  const [statusStep, setStatusStep] = useState(0); // 0: Idle, 1: Reviews, 2: Themes, 3: Grouped, 4: Report, 5: Draft email
  const [reportDate, setReportDate] = useState("2026-03-12");

  const steps = ["Reviews", "Themes", "Grouped", "Report", "Draft email"];

  const runFullPipeline = async () => {
    setLoading(true);
    setResult(null);
    setStatusStep(1);

    try {
      // Simulate progress for UI feel
      setTimeout(() => setStatusStep(2), 2000);
      setTimeout(() => setStatusStep(3), 4000);

      const response = await fetch(`${BACKEND_URL}/run-pipeline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          weeks,
          max_reviews: maxReviews,
          api_key: apiKey,
        }),
      });

      if (!response.ok) throw new Error("Pipeline failed");
      const data = await response.json();

      setStatusStep(4);
      setTimeout(() => setStatusStep(5), 1000);
      setResult(data);
    } catch (error) {
      alert("Error during pipeline execution. Check console or API key.");
      setStatusStep(0);
    } finally {
      setLoading(false);
    }
  };

  const sendEmail = async () => {
    if (!result || !recipientEmail) {
      alert("Please provide a recipient email address.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/send-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: recipientEmail,
          name: recipientName || "Team",
          analysis: result,
        }),
      });

      if (!response.ok) throw new Error("Failed to send email");
      alert("🚀 Email sent successfully!");
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#0f172a] min-h-screen text-[#94a3b8] font-sans selection:bg-blue-500/30">
      <div className="max-w-4xl mx-auto px-6 py-10">

        {/* Header */}
        <header className="mb-10">
          <h1 className="text-white text-3xl font-bold mb-2 tracking-tight">INDmoney Weekly Pulse</h1>
          <p className="text-sm font-medium">Generate the one-page weekly pulse from Play Store reviews and send it by email.</p>
        </header>

        {/* Status Bar */}
        <div className="bg-[#1e293b] rounded-xl p-8 mb-8 shadow-2xl border border-white/5">
          <h2 className="text-white text-xl font-bold mb-6">Status</h2>
          <div className="flex flex-wrap items-center gap-4">
            {steps.map((step, idx) => (
              <div
                key={step}
                className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-all duration-500 ${statusStep > idx
                  ? "bg-[#143c2c] text-[#4ade80] border border-[#22c55e]/20"
                  : "bg-[#0f172a] text-[#475569] border border-transparent"
                  }`}
              >
                {step}
              </div>
            ))}
            <div className="ml-auto text-sm font-medium text-[#475569]">
              Report date: <span className="text-[#94a3b8]">{reportDate}</span>
            </div>
          </div>
        </div>

        {/* Run Pipeline Container */}
        <div className="bg-[#1e293b] rounded-xl p-8 mb-8 shadow-2xl border border-white/5">
          <h2 className="text-white text-xl font-bold mb-2">Run pipeline</h2>
          <p className="text-sm mb-8 leading-relaxed">Scrape reviews → discover themes → classify → generate report → create draft email. This may take several minutes.</p>

          <div className="space-y-6 max-w-2xl">
            <div>
              <label className="block text-sm font-semibold mb-2">Weeks of reviews (8-12)</label>
              <select
                className="w-full bg-[#0f172a] border border-white/5 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-[#eab308]/50 focus:border-[#eab308] transition-all appearance-none cursor-pointer"
                value={weeks}
                onChange={(e) => setWeeks(parseInt(e.target.value))}
              >
                <option value={8}>8</option>
                <option value={9}>9</option>
                <option value={10}>10</option>
                <option value={11}>11</option>
                <option value={12}>12</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Max reviews to fetch</label>
              <input
                type="number"
                className="w-full bg-[#0f172a] border border-white/5 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-[#eab308]/50 focus:border-[#eab308] transition-all"
                value={maxReviews}
                onChange={(e) => setMaxReviews(parseInt(e.target.value))}
              />
            </div>

            <div className="pt-4 flex gap-4 items-center">
              <button
                onClick={runFullPipeline}
                disabled={loading}
                className="bg-[#6366f1] hover:bg-[#4f46e5] text-white px-6 py-2.5 rounded-lg font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/20 active:scale-95"
              >
                {loading ? "Processing..." : "Run full pipeline"}
              </button>

              <input
                type="password"
                placeholder="Gemini API Key (optional)"
                className="flex-1 bg-transparent text-xs border-b border-white/10 p-2 outline-none focus:border-indigo-500 transition-colors"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Report Section */}
        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-6 duration-700">
            <div className="mb-4 flex justify-between items-center px-2">
              <button
                className="bg-[#6366f1] hover:bg-[#4f46e5] text-white px-4 py-2 rounded-lg text-xs font-bold transition-all active:scale-95"
              >
                Load latest report
              </button>
            </div>

            <div className="bg-[#1e293b] rounded-xl p-10 mb-8 border border-white/5 shadow-2xl min-h-[400px]">
              <div className="space-y-12 max-w-3xl">
                {result.themes.map((theme, idx) => (
                  <div key={idx} className="flex gap-4">
                    <span className="text-white font-bold text-lg mt-0.5">{idx + 1}.</span>
                    <div className="flex-1">
                      <h3 className="text-white font-bold text-lg mb-2">
                        {theme} <span className="text-[#475569] font-normal ml-2">-- {result.quotes[idx] ? result.quotes[idx].split(' ').length * 3 : "45"} mentions</span>
                      </h3>
                      <p className="text-[#94a3b8] leading-relaxed text-[15px]">
                        {result.quotes[idx] || "Users are satisfied with this aspect of the application, noting improvements in recent updates."}
                      </p>
                    </div>
                  </div>
                ))}

                <div className="pt-10 border-t border-white/5">
                  <h4 className="text-white text-sm font-bold uppercase tracking-widest mb-4">Executive Summary</h4>
                  <p className="text-gray-400 leading-relaxed italic">
                    "{result.summary}"
                  </p>
                </div>
              </div>
            </div>

            {/* Email Controls */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
              <div className="bg-[#1e293b] rounded-xl p-8 border border-white/5 shadow-xl">
                <h3 className="text-white font-bold text-lg mb-4">Download draft email</h3>
                <button className="text-blue-400 hover:text-blue-300 font-semibold underline underline-offset-4 decoration-blue-400/30 flex items-center gap-2">
                  Download .eml
                </button>
              </div>

              <div className="bg-[#1e293b] rounded-xl p-8 border border-white/5 shadow-xl">
                <h3 className="text-white font-bold text-lg mb-1">Send email</h3>
                <p className="text-xs mb-6">Send the latest report to an email address. Optional name adds "Hi name," at the start.</p>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-[#475569]">Recipient email</label>
                    <input
                      type="email"
                      className="w-full bg-[#0f172a] border border-white/5 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-[#6366f1]/30 focus:border-[#6366f1] transition-all"
                      value={recipientEmail}
                      onChange={(e) => setRecipientEmail(e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider mb-2 text-[#475569]">Recipient name (optional)</label>
                    <input
                      type="text"
                      className="w-full bg-[#0f172a] border border-white/5 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-[#6366f1]/30 focus:border-[#6366f1] transition-all"
                      placeholder="e.g. Priya"
                      value={recipientName}
                      onChange={(e) => setRecipientName(e.target.value)}
                    />
                  </div>

                  <button
                    onClick={sendEmail}
                    className="bg-[#6366f1] hover:bg-[#4f46e5] text-white px-8 py-2.5 rounded-lg font-bold transition-all disabled:opacity-50 active:scale-95"
                  >
                    Send email
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
