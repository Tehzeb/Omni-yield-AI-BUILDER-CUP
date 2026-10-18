import React from "react";

export default function TopBanner() {
  return (
    <div className="top-banner">
      <span>Live diagnostics available — <a href="/diagnose">open the OmniYield console</a></span>
      <span>Backed by Gemini Vision + Cloud Run — <a href="/about">see the architecture</a></span>
      <span>Built for the AI Builder Cup JAPAC Edition — <a href="/about">read the pitch</a></span>
    </div>
  );
}
