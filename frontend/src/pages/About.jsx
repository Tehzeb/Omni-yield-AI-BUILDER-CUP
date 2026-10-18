import React from "react";
import { Link } from "react-router-dom";

const pillars = [
  {
    title: "Leverages a fast, known architecture",
    body:
      "No time to learn a new framework under deadline pressure. OmniYield relies on an architecture that ships fast: a microcontroller or manual input simulating live telemetry, a workflow orchestration layer catching that data, and that data piped alongside an image into Gemini's Vision and text APIs.",
  },
  {
    title: "A genuinely multi-modal agent",
    body:
      "Most AI diagnostic demos summarize a manual. OmniYield cross-references three independent signals — the physical defect in the photo, the live sensor readings, and the manual's own repair procedure — before producing one answer.",
  },
  {
    title: "Solves a tangible, expensive B2B problem",
    body:
      "Unplanned downtime and scrap waste are billion-dollar problems across manufacturing. Shifting from \"here is a summary of the manual\" to \"I looked at the broken part, checked the live temperature, and here is the exact dial to turn\" is a marketable leap in industrial efficiency.",
  },
];

const stack = [
  { label: "Backend", value: "FastAPI (Python) — async multipart endpoint, Gemini SDK orchestration" },
  { label: "AI model", value: "Gemini 3.8 Flash — multi-modal vision + text reasoning" },
  { label: "Deployment", value: "Docker on python:3.11-slim-buster → Google Cloud Run, port 8080" },
  { label: "Frontend", value: "React 18 — dark neon dashboard, glassmorphism result panel" },
  { label: "Hosting", value: "Firebase Hosting serving the compiled build/ output" },
  { label: "Persistence", value: "localStorage for theme preference across reloads" },
];

const pipeline = [
  {
    step: "01",
    title: "Telemetry rule pass",
    detail:
      "Incoming temperature, vibration and pressure readings are checked against defined thresholds (85°C, 4.5mm/s, 150psi) before the AI call, producing fast, deterministic flags.",
  },
  {
    step: "02",
    title: "Prompt assembly",
    detail:
      "The backend builds a single structured prompt combining the telemetry JSON, the telemetry flags, and the pasted manual excerpt — framed as instructions for a diagnostic agent.",
  },
  {
    step: "03",
    title: "Vision + text inference",
    detail:
      "The uploaded image and the assembled prompt are sent together to Gemini 3.8 Flash via the Interactions API, which reasons over the defect, the numbers, and the manual in one pass.",
  },
  {
    step: "04",
    title: "Structured response",
    detail:
      "The model is constrained to return strict JSON — root_cause, repair_action, confidence — which the API validates and returns to the console.",
  },
];

export default function About() {
  return (
    <div className="about-page">
      <section className="about-hero">
        <p className="eyebrow">How it works</p>
        <h1>
          An agentic digital twin for <span className="grad-text">industrial maintenance</span>
        </h1>
        <p className="hero-sub">
          OmniYield was built to demonstrate a significantly more advanced use of multi-modal AI
          than a chatbot wrapped around a PDF manual — it reasons across vision, sensors, and
          text together.
        </p>
      </section>

      <section className="pillars">
        {pillars.map((p) => (
          <div className="pillar-card" key={p.title}>
            <h3>{p.title}</h3>
            <p>{p.body}</p>
          </div>
        ))}
      </section>

      <section className="pipeline-section" id="timeline">
        <h2 className="section-label">
          <span className="grad-text">Request pipeline</span>
        </h2>
        <div className="pipeline-grid">
          {pipeline.map((p) => (
            <div className="pipeline-card" key={p.step}>
              <span className="pipeline-step">{p.step}</span>
              <h4>{p.title}</h4>
              <p>{p.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="stack-section">
        <h2 className="section-label">
          <span className="grad-text">Tech stack</span>
        </h2>
        <div className="stack-table">
          {stack.map((s) => (
            <div className="stack-row" key={s.label}>
              <span className="stack-label">{s.label}</span>
              <span className="stack-value">{s.value}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="glow-banner">
        <div className="glow-banner-icon">⬡</div>
        <p>
          The API contract is simple on purpose: <code>POST /analyze</code> with an{" "}
          <code>image</code> file, a <code>telemetry</code> JSON string, and optional{" "}
          <code>manual_text</code> — returns <code>root_cause</code>, <code>repair_action</code>,{" "}
          <code>confidence</code>, and <code>telemetry_flags</code>.
        </p>
      </section>

      <section className="about-cta">
        <h2>Ready to see it diagnose a part?</h2>
        <Link to="/diagnose" className="pill-btn pill-btn-filled">
          Open the Diagnostic Console
        </Link>
      </section>
    </div>
  );
}
