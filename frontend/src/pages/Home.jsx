import React from "react";
import { Link } from "react-router-dom";

const badges = [
  { label: "Image + Telemetry + Manual", icon: "⟐" },
  { label: "Gemini Vision Agent", icon: "✦" },
  { label: "Cloud Run Deployment", icon: "☁" },
  { label: "Real-time Diagnosis", icon: "⚡" },
];

const audiences = [
  {
    title: "Plant Engineers",
    desc: "Stop flipping through 200-page manuals during a line-down emergency. Point a camera at the part, and get the exact page and dial setting.",
  },
  {
    title: "Maintenance Teams",
    desc: "Correlate a visual defect with live sensor drift instead of guessing — OmniYield reads vibration and temperature alongside what your eyes see.",
  },
  {
    title: "Operations Leaders",
    desc: "Turn unplanned downtime into a measurable, trackable diagnostic log across every machine on the floor.",
  },
];

const timeline = [
  { step: "Capture", detail: "Photo of the defect + live telemetry snapshot", date: "Step 1" },
  { step: "Ingest", detail: "FastAPI receives image, JSON telemetry, manual excerpt", date: "Step 2" },
  { step: "Reason", detail: "Gemini Vision cross-references defect, sensors & manual", date: "Step 3" },
  { step: "Diagnose", detail: "Structured root cause + repair action returned", date: "Step 4" },
  { step: "Act", detail: "Technician executes the exact fix, logged for history", date: "Step 5" },
];

const roadmap = [
  {
    title: "Upload & Capture",
    desc: "Upload an image of the defective part alongside live machine telemetry readings — no special hardware required to try it.",
  },
  {
    title: "Multi-modal Reasoning",
    desc: "The backend agent fuses the image, sensor flags, and a manual excerpt into one Gemini Vision + text prompt.",
  },
  {
    title: "Structured Diagnosis",
    desc: "Get back a root cause, a specific repair action, and a confidence score — not a generic summary.",
  },
  {
    title: "Deploy Anywhere",
    desc: "Ship the backend to Cloud Run and the frontend to Firebase Hosting in minutes.",
  },
];

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Builders assemble.</p>
          <h1>
            Omni<span className="grad-text">Yield</span>
            <br />
            Diagnose in seconds.
            <br />
            Fix it right the first time.
          </h1>
          <p className="hero-sub">
            A multi-modal agentic digital twin for industrial maintenance — it looks at the
            broken part, checks the machine's live telemetry, and tells you the exact repair
            action from the manual.
          </p>
          <div className="hero-ctas">
            <Link to="/diagnose" className="pill-btn pill-btn-filled">
              Launch Diagnostic Console
            </Link>
            <Link to="/about" className="pill-btn">
              How it works
            </Link>
          </div>
        </div>
        <div className="hero-art">
          <div className="hero-art-glow" />
          <div className="hero-art-icon">⬡</div>
        </div>
      </section>

      <section className="badge-row">
        {badges.map((b) => (
          <div className="badge-pill" key={b.label}>
            <span>{b.icon}</span> {b.label}
          </div>
        ))}
      </section>

      <section className="overview">
        <div className="overview-media">
          <div className="overview-media-inner">
            <span className="overview-caption">From defect to diagnosis</span>
          </div>
        </div>
        <div className="overview-copy">
          <h2 className="section-label">
            <span className="grad-text">Overview</span>
          </h2>
          <p>
            Unplanned downtime and scrap waste cost manufacturers billions every year. Most
            diagnostic tools can only do one of two things: read a manual, or read a sensor.
            Neither alone tells you what's actually wrong.
          </p>
          <p>
            OmniYield is built as an agentic digital twin. It combines hardware telemetry
            (temperature, vibration, pressure) with Gemini Vision analysis of the physical
            defect and a text-based reasoning pass over the machine's own manual — producing a
            single, specific repair action instead of a vague summary.
          </p>
          <p>
            The premise is simple: upload a photo, enter the readings, paste the relevant
            manual section, and OmniYield tells you exactly what's broken and exactly how to
            fix it.
          </p>
        </div>
      </section>

      <section className="stats-bar">
        <div className="stats-pill">Problem Alignment <strong>Billion-dollar downtime</strong></div>
        <div className="stats-pill stats-pill-accent">Stack <strong>FastAPI · Gemini · Cloud Run</strong></div>
      </section>

      <section className="audience">
        <h2>This console is for</h2>
        <div className="audience-grid">
          {audiences.map((a) => (
            <div className="audience-card" key={a.title}>
              <h3>{a.title}</h3>
              <p>{a.desc}</p>
            </div>
          ))}
        </div>
        <p className="audience-footnote">
          Prototype stage — telemetry thresholds and manual excerpts are provided manually today;
          live hardware webhooks are the next milestone.
        </p>
      </section>

      <section className="timeline-section">
        <h2>How a diagnosis happens</h2>
        <div className="timeline">
          {timeline.map((t, i) => (
            <div className="timeline-item" key={t.step}>
              <div className="timeline-dot" />
              <div className="timeline-label">{t.step}</div>
              <div className="timeline-date">{t.detail}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="glow-banner">
        <div className="glow-banner-icon">◎</div>
        <p>
          OmniYield ships as a working prototype: a FastAPI diagnostic agent on{" "}
          <strong>Google Cloud Run</strong> and a React console on{" "}
          <strong>Firebase Hosting</strong> — try the live console now.
        </p>
      </section>

      <section className="roadmap">
        <div className="roadmap-copy">
          <h2>
            Your path
            <br />
            <span className="grad-text">to a fix</span>
          </h2>
        </div>
        <div className="roadmap-list">
          {roadmap.map((r, i) => (
            <div className="roadmap-item" key={r.title}>
              <div className="roadmap-dot" />
              <div>
                <h4>{r.title}</h4>
                <p>{r.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
