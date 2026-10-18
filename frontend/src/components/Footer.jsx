import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-disclaimer">
        <h4>Disclaimer</h4>
        <p>
          OmniYield is an agentic industrial diagnostic prototype built for the AI Builder Cup,
          JAPAC Edition. It is an independent hackathon project and is not an officially
          certified industrial safety system. Always follow your facility's official
          lockout/tagout and manufacturer repair procedures.
        </p>
      </div>

      <div className="footer-columns">
        <div className="footer-col">
          <h5>Contact Us</h5>
          <p>
            💬 <Link to="/diagnose">Click here to join</Link>
          </p>
          <div className="footer-email">support+omniyield@hack2skill.com</div>
        </div>

        <div className="footer-brand">
          <span className="brand-mark">⬡</span>
          <span className="brand-name">OmniYield</span>
        </div>

        <div className="footer-col footer-links">
          <h5>Quick Links</h5>
          <Link to="/">Overview</Link>
          <Link to="/about">How It Works</Link>
          <Link to="/about#timeline">Architecture</Link>
          <Link to="/diagnose">Diagnostic Console</Link>
          <Link to="/about">Challenges &amp; Requirements</Link>
        </div>
      </div>

      <div className="footer-bottom">© OmniYield — AI Builder Cup JAPAC Edition. All rights reserved.</div>
    </footer>
  );
}
