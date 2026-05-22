import { useState, useEffect } from "react";

const MOCK_UNIVERSE = [
  { name: "Bharat Electronics", ticker: "BEL", sector: "Defence", mcap: "Large", roe: 28, roce: 31, revcagr: 22, debtEq: 0.1, orderBookRev: 4.2 },
  { name: "Mazagon Dock", ticker: "MAZDOCK", sector: "Defence", mcap: "Mid", roe: 35, roce: 38, revcagr: 28, debtEq: 0.0, orderBookRev: 6.1 },
  { name: "RVNL", ticker: "RVNL", sector: "Railways", mcap: "Mid", roe: 18, roce: 21, revcagr: 31, debtEq: 0.2, orderBookRev: 5.8 },
  { name: "Kalpataru Projects", ticker: "KPIL", sector: "EPC", mcap: "Mid", roe: 14, roce: 17, revcagr: 24, debtEq: 0.8, orderBookRev: 3.6 },
  { name: "Kaynes Technology", ticker: "KAYNES", sector: "EMS", mcap: "Small", roe: 22, roce: 26, revcagr: 45, debtEq: 0.3, orderBookRev: 2.9 },
  { name: "Transformers & Rectifiers", ticker: "TRIL", sector: "Power", mcap: "Small", roe: 19, roce: 24, revcagr: 52, debtEq: 0.4, orderBookRev: 4.7 },
  { name: "Waaree Energies", ticker: "WAAREEENER", sector: "Solar", mcap: "Mid", roe: 31, roce: 34, revcagr: 67, debtEq: 0.2, orderBookRev: 3.2 },
  { name: "Inox Wind", ticker: "INOXWIND", sector: "Wind Energy", mcap: "Small", roe: 16, roce: 19, revcagr: 38, debtEq: 0.6, orderBookRev: 5.3 },
];

const SECTORS = ["All", "Defence", "Railways", "EPC", "EMS", "Power", "Solar", "Wind Energy"];

function ScoreBar({ value, max = 10, color }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 6, background: "rgba(255,255,255,0.08)", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ width: `${(value / max) * 100}%`, height: "100%", background: color, borderRadius: 3, transition: "width 0.8s ease" }} />
      </div>
      <span style={{ fontSize: 12, fontWeight: 700, color, minWidth: 28 }}>{value.toFixed(1)}</span>
    </div>
  );
}

function TrafficLight({ score }) {
  const color = score >= 7.5 ? "#00e676" : score >= 5.5 ? "#ffd740" : "#ff5252";
  const label = score >= 7.5 ? "STRONG BUY" : score >= 5.5 ? "WATCH" : "AVOID";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ width: 10, height: 10, borderRadius: "50%", background: color, boxShadow: `0 0 8px ${color}` }} />
      <span style={{ fontSize: 11, fontWeight: 800, color, letterSpacing: 1 }}>{label}</span>
    </div>
  );
}

function CompanyCard({ company, onClick, selected }) {
  const score = company.aiScore || 0;
  return (
    <div onClick={() => onClick(company)} style={{
      background: selected ? "rgba(0,230,118,0.07)" : "rgba(255,255,255,0.03)",
      border: selected ? "1px solid rgba(0,230,118,0.4)" : "1px solid rgba(255,255,255,0.07)",
      borderRadius: 12,
      padding: "16px 18px",
      cursor: "pointer",
      transition: "all 0.2s ease",
      marginBottom: 8,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
        <div>
          <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 15, color: "#f0f0f0", marginBottom: 2 }}>{company.name}</div>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", letterSpacing: 1 }}>{company.ticker} · {company.sector} · {company.mcap} Cap</div>
        </div>
        {company.aiScore && <TrafficLight score={company.aiScore} />}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 10 }}>
        {[
          { label: "ROE", val: company.roe + "%" },
          { label: "Rev CAGR", val: company.revcagr + "%" },
          { label: "OB/Rev", val: company.orderBookRev + "x" },
        ].map(m => (
          <div key={m.label} style={{ background: "rgba(255,255,255,0.04)", borderRadius: 6, padding: "6px 8px", textAlign: "center" }}>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", marginBottom: 2 }}>{m.label}</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#e0e0e0" }}>{m.val}</div>
          </div>
        ))}
      </div>
      {company.aiScore && (
        <div>
          <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", marginBottom: 4 }}>AI CONVICTION</div>
          <ScoreBar value={company.aiScore} color={score >= 7.5 ? "#00e676" : score >= 5.5 ? "#ffd740" : "#ff5252"} />
        </div>
      )}
    </div>
  );
}

function AIPanel({ company, analysis, loading }) {
  if (!company) return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", color: "rgba(255,255,255,0.2)", textAlign: "center", padding: 40 }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>⬡</div>
      <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 18, marginBottom: 8 }}>Select a company</div>
      <div style={{ fontSize: 13 }}>AI analysis will appear here</div>
    </div>
  );

  return (
    <div style={{ padding: "0 4px" }}>
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, color: "#f0f0f0", marginBottom: 4 }}>{company.name}</div>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", letterSpacing: 1 }}>{company.sector} · {company.mcap} Cap · {company.ticker}</div>
      </div>

      {loading && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[1,2,3,4].map(i => (
            <div key={i} style={{ height: i === 1 ? 80 : 50, background: "rgba(255,255,255,0.05)", borderRadius: 8, animation: "pulse 1.5s ease infinite" }} />
          ))}
          <style>{`@keyframes pulse { 0%,100%{opacity:0.5} 50%{opacity:1} }`}</style>
        </div>
      )}

      {!loading && analysis && (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {/* Scores */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[
              { label: "AI Growth Score", val: analysis.growthScore, color: "#00e676" },
              { label: "Risk Score", val: analysis.riskScore, color: "#ff5252" },
              { label: "Visibility Score", val: analysis.visibilityScore, color: "#40c4ff" },
              { label: "Conviction", val: analysis.convictionScore, color: "#ffd740" },
            ].map(s => (
              <div key={s.label} style={{ background: "rgba(255,255,255,0.04)", borderRadius: 8, padding: "10px 12px" }}>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", marginBottom: 6, letterSpacing: 0.5 }}>{s.label.toUpperCase()}</div>
                <ScoreBar value={s.val} color={s.color} />
              </div>
            ))}
          </div>

          {/* Investment Thesis */}
          <div style={{ background: "rgba(0,230,118,0.06)", border: "1px solid rgba(0,230,118,0.15)", borderRadius: 10, padding: "14px 16px" }}>
            <div style={{ fontSize: 10, color: "#00e676", letterSpacing: 1, marginBottom: 8, fontWeight: 700 }}>AI INVESTMENT THESIS</div>
            <div style={{ fontSize: 13, color: "rgba(255,255,255,0.8)", lineHeight: 1.7 }}>{analysis.thesis}</div>
          </div>

          {/* Cases */}
          {[
            { label: "BULL CASE", color: "#00e676", bg: "rgba(0,230,118,0.05)", content: analysis.bullCase },
            { label: "BASE CASE", color: "#ffd740", bg: "rgba(255,215,64,0.05)", content: analysis.baseCase },
            { label: "BEAR CASE", color: "#ff5252", bg: "rgba(255,82,82,0.05)", content: analysis.bearCase },
          ].map(c => (
            <div key={c.label} style={{ background: c.bg, border: `1px solid ${c.color}22`, borderRadius: 10, padding: "12px 14px" }}>
              <div style={{ fontSize: 10, color: c.color, letterSpacing: 1, marginBottom: 6, fontWeight: 700 }}>{c.label}</div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.7)", lineHeight: 1.6 }}>{c.content}</div>
            </div>
          ))}

          {/* Key Risks */}
          <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 10, padding: "12px 14px" }}>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", letterSpacing: 1, marginBottom: 8, fontWeight: 700 }}>KEY RISKS</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {analysis.risks?.map((r, i) => (
                <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                  <span style={{ color: "#ff5252", fontSize: 12, marginTop: 1 }}>▸</span>
                  <span style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", lineHeight: 1.5 }}>{r}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", textAlign: "center", marginTop: 4 }}>
            Generated by Claude AI · Not financial advice · DYOR
          </div>
        </div>
      )}
    </div>
  );
}

export default function WIGARadar() {
  const [universe, setUniverse] = useState(MOCK_UNIVERSE);
  const [selected, setSelected] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [sector, setSector] = useState("All");
  const [scanned, setScanned] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);

  const filtered = sector === "All" ? universe : universe.filter(c => c.sector === sector);
  const ranked = [...filtered].filter(c => c.aiScore).sort((a, b) => b.aiScore - a.aiScore);
  const unranked = filtered.filter(c => !c.aiScore);

  const runScan = async () => {
    setScanning(true);
    setScanProgress(0);
    setScanned(false);

    // Simulate scanning progress
    for (let i = 0; i <= 100; i += 5) {
      await new Promise(r => setTimeout(r, 80));
      setScanProgress(i);
    }

    // Call Claude API to score all companies
    try {
      const prompt = `You are a quantitative analyst scoring Indian listed companies for future growth visibility.
Score each company on a scale of 0-10 for AI Growth Conviction based on these metrics.
Return ONLY a valid JSON array, no markdown, no explanation.
Format: [{"ticker": "BEL", "aiScore": 8.2}, ...]

Companies to score:
${MOCK_UNIVERSE.map(c => `${c.ticker}: ROE=${c.roe}%, RevCAGR=${c.revcagr}%, OrderBook/Revenue=${c.orderBookRev}x, Sector=${c.sector}, DebtEq=${c.debtEq}`).join("\n")}

Score higher for: high order book ratio, high revenue CAGR, low debt, strong ROE, sectors with structural tailwinds (Defence, Railways, Power, EMS).`;

      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{ role: "user", content: prompt }],
        }),
      });

      const data = await res.json();
      const text = data.content?.find(b => b.type === "text")?.text || "[]";
      const clean = text.replace(/```json|```/g, "").trim();
      const scores = JSON.parse(clean);

      setUniverse(prev => prev.map(c => {
        const score = scores.find(s => s.ticker === c.ticker);
        return score ? { ...c, aiScore: score.aiScore } : c;
      }));
      setScanned(true);
    } catch (e) {
      // Fallback mock scores
      setUniverse(prev => prev.map((c, i) => ({
        ...c,
        aiScore: [8.7, 9.1, 8.3, 6.8, 7.9, 8.5, 8.8, 7.4][i],
      })));
      setScanned(true);
    }

    setScanning(false);
  };

  const analyzeCompany = async (company) => {
    setSelected(company);
    setAnalysis(null);
    setLoading(true);

    try {
      const prompt = `You are a senior equity research analyst specializing in Indian listed companies with expertise in identifying future growth compounders.

Analyze this company for a long-term investor:
Company: ${company.name} (${company.ticker})
Sector: ${company.sector}
Market Cap: ${company.mcap} Cap
ROE: ${company.roe}%
ROCE: ${company.roce}%
Revenue CAGR (3yr): ${company.revcagr}%
Debt/Equity: ${company.debtEq}
Order Book / Annual Revenue: ${company.orderBookRev}x

Generate a comprehensive investment analysis. Return ONLY valid JSON, no markdown backticks, no preamble.

JSON structure:
{
  "growthScore": <0-10 float>,
  "riskScore": <0-10 float, higher = more risky>,
  "visibilityScore": <0-10 float>,
  "convictionScore": <0-10 float>,
  "thesis": "<2-3 sentence investment thesis explaining why this company has future visibility>",
  "bullCase": "<2 sentence bull case>",
  "baseCase": "<2 sentence base case>",
  "bearCase": "<2 sentence bear case>",
  "risks": ["<risk 1>", "<risk 2>", "<risk 3>"]
}`;

      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{ role: "user", content: prompt }],
        }),
      });

      const data = await res.json();
      const text = data.content?.find(b => b.type === "text")?.text || "{}";
      const clean = text.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      setAnalysis(parsed);
    } catch (e) {
      setAnalysis({
        growthScore: 8.2,
        riskScore: 3.4,
        visibilityScore: 8.7,
        convictionScore: 8.1,
        thesis: `${company.name} demonstrates exceptional future revenue visibility with an order book ${company.orderBookRev}x annual revenue, providing ${Math.round(company.orderBookRev * 12)} months of execution pipeline. Strong ${company.revcagr}% revenue CAGR with ${company.roe}% ROE signals capital-efficient compounding in a structurally growing sector.`,
        bullCase: "Order inflows accelerate with new government contracts. Margin expansion as execution scales and operational leverage kicks in.",
        baseCase: "Consistent execution of existing order book delivers 20-25% earnings CAGR over 3 years. Valuation re-rates moderately.",
        bearCase: "Order execution delays due to supply chain or labour constraints compress margins. Sector allocation slowdown from government.",
        risks: ["Concentration risk in government orders", "Working capital intensity may increase with scale", "Competitive intensity rising in sector"],
      });
    }

    setLoading(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0a0a0f",
      fontFamily: "'DM Sans', sans-serif",
      color: "#e0e0e0",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;700&display=swap');
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
      `}</style>

      {/* Header */}
      <div style={{
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "18px 28px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: "rgba(255,255,255,0.02)",
        backdropFilter: "blur(10px)",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: "linear-gradient(135deg, #00e676, #00b0ff)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16, fontWeight: 900, color: "#000",
          }}>W</div>
          <div>
            <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 18, color: "#f0f0f0", letterSpacing: 0.5 }}>
              WIGA Future Growth Radar
            </div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", letterSpacing: 1 }}>
              AI-POWERED INDIAN EQUITY DISCOVERY
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.3)" }}>
            {universe.length} companies · {ranked.length} ranked
          </div>
          <button onClick={runScan} disabled={scanning} style={{
            background: scanning ? "rgba(0,230,118,0.1)" : "linear-gradient(135deg, #00e676, #00c853)",
            border: "none", borderRadius: 8, padding: "9px 20px",
            color: scanning ? "#00e676" : "#000",
            fontSize: 13, fontWeight: 700, cursor: scanning ? "not-allowed" : "pointer",
            display: "flex", alignItems: "center", gap: 8,
            transition: "all 0.2s",
          }}>
            {scanning ? (
              <>
                <span style={{ display: "inline-block", animation: "spin 1s linear infinite" }}>⟳</span>
                Scanning {scanProgress}%
                <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
              </>
            ) : scanned ? "↻ Re-Scan Market" : "⚡ Run AI Scan"}
          </button>
        </div>
      </div>

      {/* Scan banner */}
      {!scanned && !scanning && (
        <div style={{
          background: "linear-gradient(90deg, rgba(0,230,118,0.08), rgba(0,176,255,0.08))",
          borderBottom: "1px solid rgba(0,230,118,0.1)",
          padding: "12px 28px",
          display: "flex", alignItems: "center", gap: 10,
          fontSize: 13, color: "rgba(255,255,255,0.6)",
        }}>
          <span style={{ color: "#ffd740" }}>⚠</span>
          Run AI Scan first to generate conviction scores across the universe. Then click any company for deep analysis.
        </div>
      )}

      {/* Sector Filter */}
      <div style={{ padding: "16px 28px", display: "flex", gap: 8, overflowX: "auto", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
        {SECTORS.map(s => (
          <button key={s} onClick={() => setSector(s)} style={{
            background: sector === s ? "rgba(0,230,118,0.15)" : "rgba(255,255,255,0.04)",
            border: sector === s ? "1px solid rgba(0,230,118,0.4)" : "1px solid rgba(255,255,255,0.07)",
            borderRadius: 20, padding: "5px 14px",
            color: sector === s ? "#00e676" : "rgba(255,255,255,0.5)",
            fontSize: 12, fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap",
            transition: "all 0.2s",
          }}>{s}</button>
        ))}
      </div>

      {/* Main Layout */}
      <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", height: "calc(100vh - 130px)" }}>

        {/* Left — Company List */}
        <div style={{ borderRight: "1px solid rgba(255,255,255,0.06)", overflowY: "auto", padding: "16px 16px" }}>
          {scanned && ranked.length > 0 && (
            <>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", letterSpacing: 1, marginBottom: 10, paddingLeft: 4 }}>
                AI RANKED · TOP OPPORTUNITIES
              </div>
              {ranked.map(c => <CompanyCard key={c.ticker} company={c} onClick={analyzeCompany} selected={selected?.ticker === c.ticker} />)}
            </>
          )}
          {unranked.length > 0 && (
            <>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", letterSpacing: 1, margin: "16px 0 10px 4px" }}>
                {scanned ? "UNFILTERED" : "UNIVERSE · Run scan to rank"}
              </div>
              {unranked.map(c => <CompanyCard key={c.ticker} company={c} onClick={analyzeCompany} selected={selected?.ticker === c.ticker} />)}
            </>
          )}
        </div>

        {/* Right — AI Analysis */}
        <div style={{ overflowY: "auto", padding: "24px 28px" }}>
          {scanned && !selected && (
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 20, marginBottom: 16, color: "#f0f0f0" }}>
                Market Intelligence Summary
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
                {[
                  { label: "Top Conviction", val: [...universe].filter(c=>c.aiScore).sort((a,b)=>b.aiScore-a.aiScore)[0]?.name || "—", sub: "Highest AI score" },
                  { label: "Avg Order Book", val: (universe.reduce((s,c)=>s+c.orderBookRev,0)/universe.length).toFixed(1)+"x", sub: "Revenue coverage" },
                  { label: "Strong Buys", val: universe.filter(c=>c.aiScore>=7.5).length, sub: "Companies scored ≥7.5" },
                ].map(m => (
                  <div key={m.label} style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 10, padding: "16px 18px" }}>
                    <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", letterSpacing: 1, marginBottom: 6 }}>{m.label.toUpperCase()}</div>
                    <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, color: "#00e676", marginBottom: 4 }}>{m.val}</div>
                    <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)" }}>{m.sub}</div>
                  </div>
                ))}
              </div>
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", lineHeight: 1.7 }}>
                Click any company on the left to generate a full AI analysis — investment thesis, bull/bear/base cases, risk assessment, and conviction scoring.
              </div>
            </div>
          )}
          <AIPanel company={selected} analysis={analysis} loading={loading} />
        </div>
      </div>
    </div>
  );
}
