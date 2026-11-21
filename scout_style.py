"""Scoped visual stylesheet for the Picky AI Scout UI.

Kept separate from legacy theme.py to avoid stacking conflicting layout rules.
"""
from __future__ import annotations

import streamlit as st


def inject_scout_css():
    st.markdown(
        """
<style>
:root {
  --picky-ink: #10151f;
  --picky-surface: #18242d;
  --picky-surface-rich: #142c28;
  --picky-soft-border: rgba(100,150,135,.22);
  --picky-primary: #38c98a;
  --picky-light: #e8fff3;
  --picky-muted: #a8bac4;
  --picky-radius: 16px;
}
.picky-hero {
  padding: clamp(16px, 2vw, 26px);
  border: 1px solid rgba(65,215,142,.55);
  border-radius: 20px;
  background:
    radial-gradient(ellipse at 88% 0%, rgba(49,205,137,.12),transparent 45%),
    linear-gradient(122deg,#173f34 0%,#14242d 70%,#131d2a 100%);
  box-shadow: 0 14px 45px rgba(4,12,10,.20),inset 0 1px rgba(125,255,190,.09);
  min-width:0;
  overflow:hidden;
}
.picky-hero-topline {
  display:flex; align-items:center; justify-content:space-between;
  gap:10px; flex-wrap:wrap; margin-bottom:14px;
}
.picky-hero-eyebrow {
  display:inline-flex; align-items:center; padding:7px 10px;
  border-radius:8px; background:#45d797; color:#082f1d;
  text-transform:uppercase; font-size:10px; font-weight:900; letter-spacing:.08em;
}
.picky-hero-status {
  color:#a4eac8; font-size:11px; text-transform:uppercase;
  font-weight:750; letter-spacing:.07em;
}
.picky-hero-body { display:flex; align-items:center; gap:clamp(14px,2.5vw,32px);min-width:0; }
.picky-hero-info { flex:1; min-width:0; }
.picky-hero-kicker {color:#71e0a8; font-size:10px;font-weight:850;letter-spacing:.10em;}
.picky-hero h3 {
  margin:7px 0 3px; font-size:clamp(24px,2.5vw,35px);
  font-weight:790; color:#f4fff8; letter-spacing:-.045em; line-height:1.18;
}
.picky-hero-meta {color:#b4d6c8;margin:0 0 9px;font-size:12px;line-height:1.5;}
.picky-hero-summary {
  color:#e3f3eb;max-width:780px;line-height:1.65;
  font-size:clamp(12px,1.05vw,14px);margin:0 0 13px;
}
.picky-hero-chips,.picky-player-metrics {display:flex;flex-wrap:wrap;gap:7px;align-items:center;}
.picky-chip {
  display:inline-flex; gap:5px; max-width:100%;align-items:center;
  padding:5px 8px;border-radius:999px;border:1px solid rgba(140,165,177,.21);
  color:#bdccd4;background:#22313a;font-size:10px;line-height:1.4;
  font-weight:700;white-space:normal;
}
.picky-chip--green {color:#9ff7c8;background:rgba(46,155,98,.19);border-color:rgba(65,195,118,.43);}
.picky-chip--amber {color:#f5cb8e;background:rgba(144,95,30,.17);border-color:rgba(230,156,62,.34);}
.picky-chip--blue {color:#bed8f6;background:rgba(68,108,146,.21);border-color:rgba(113,163,211,.32);}
.picky-photo {
  display:inline-grid;place-items:center;position:relative;flex-shrink:0;
  width:62px;height:62px;border-radius:15px;overflow:hidden;
  border:1px solid rgba(103,223,165,.35);
  background:linear-gradient(147deg,#2b8060,#194136);
  box-shadow:inset 0 1px rgba(255,255,255,.12),0 7px 16px rgba(5,25,16,.23);
  isolation:isolate;
}
.picky-photo--hero {width:clamp(88px,9vw,122px);height:clamp(88px,9vw,122px);border-radius:23px;}
.picky-photo--modal {width:95px;height:95px;border-radius:20px;}
.picky-photo-fallback {color:#b7ffdd;font-size:24px;line-height:1;font-weight:850;letter-spacing:-.04em;}
.picky-photo--hero .picky-photo-fallback {font-size:36px;}
.picky-photo--modal .picky-photo-fallback {font-size:32px;}
.picky-photo img {
  position:absolute;inset:0;width:100%;height:100%;
  object-fit:cover;object-position:center 22%;font-size:0;color:transparent;
  background:transparent;
}
.picky-photo--hero img,.picky-photo--modal img {object-fit:contain;object-position:center bottom;}
/* Only the Scout recommendation containers receive the new card treatment. */
[class*="st-key-ai_candidate_"] {
  border:1px solid rgba(75,145,121,.31)!important;
  background:linear-gradient(110deg,#132526 0%,#141e29 95%)!important;
  border-radius:15px!important; padding:14px 15px!important;
  margin-bottom:10px;
  transition:border-color .2s ease,background .2s ease,transform .2s ease;
}
[class*="st-key-ai_candidate_"]:hover {
  border-color:rgba(87,219,155,.65)!important;
  background:linear-gradient(112deg,#18392e,#192a31)!important;
  transform:translateY(-1px);
}
[class*="st-key-ai_candidate_"] [data-testid="stVerticalBlockBorderWrapper"]{
  border:0!important;background:transparent!important;padding:0!important;
}
[class*="st-key-ai_candidate_"] [data-testid="stVerticalBlock"] {gap:0!important;}
.picky-player-row {display:flex;align-items:center;gap:14px;min-width:0;padding:1px 0;}
.picky-player-rank {
  width:30px;flex-shrink:0;color:#76daaa;font-size:12px;font-weight:850;
}
.picky-player-content {flex:1;min-width:0;display:flex;flex-direction:column;gap:6px;}
.picky-player-title-line {display:flex;align-items:baseline;flex-wrap:wrap;gap:5px 11px;}
.picky-player-title-line strong {
  color:#f1fff7;font-size:clamp(14px,1.15vw,17px);font-weight:780;line-height:1.3;
}
.picky-player-team {color:#b4c6cf;font-size:11px;line-height:1.4;}
.picky-player-summary {
  font-size:12px!important;line-height:1.55!important;color:#d8e7e2!important;
  margin:0!important;display:-webkit-box;-webkit-box-orient:vertical;
  -webkit-line-clamp:2;line-clamp:2;overflow:hidden;
}
.picky-player-metrics {gap:5px;}
.picky-player-metrics .picky-chip {font-size:9px;padding:4px 7px;}
[class*="st-key-ai_candidate_"] button {
  width:100%!important;min-height:43px!important;border-radius:11px!important;
  background:#38c98a!important;border:1px solid #67efb0!important;
  color:#0c3021!important;font-weight:800!important;font-size:12px!important;
}
[class*="st-key-ai_candidate_"] button p,
[class*="st-key-ai_candidate_"] button [data-testid="stIconMaterial"] {
  color:#0c3021!important;font-weight:800!important;
}
[class*="st-key-ai_candidate_"] button:hover {
  background:#67edab!important;border-color:#92ffcb!important;
  box-shadow:0 5px 18px rgba(38,182,105,.20)!important;
}
[class*="st-key-ai_candidate_"] button:focus-visible {
  outline:3px solid #abfbd1!important;outline-offset:3px!important;
}
.picky-modal-hero {
  display:flex;align-items:center;gap:22px;min-width:0;
  border:1px solid rgba(68,199,133,.38);
  border-radius:17px;padding:18px;
  background:linear-gradient(116deg,#173d31,#192631);
  margin:0 0 16px;box-shadow:0 9px 29px rgba(10,24,19,.2);
}
.picky-modal-identity {min-width:0;flex:1;}
.picky-modal-eyebrow {color:#74e2a9;letter-spacing:.09em;font-weight:850;font-size:10px;}
.picky-modal-hero h3 {color:#f3fff8;font-size:clamp(22px,2.6vw,31px);
  margin:5px 0 2px;font-weight:800;letter-spacing:-.035em;}
.picky-modal-hero p {color:#b8d4c8;font-size:13px;margin:0 0 10px;}
.picky-insight {
  border:1px solid rgba(100,150,135,.25);
  background:linear-gradient(140deg,#1b2834,#172329);
  border-radius:14px;padding:16px 17px;height:100%;
  min-width:0;
}
.picky-insight--green {border-color:rgba(74,199,126,.42);
  background:linear-gradient(130deg,#16372d,#192a30);}
.picky-insight--amber {border-color:rgba(202,153,78,.32);}
.picky-insight-title {display:flex;align-items:center;gap:9px;color:#f2fcf5;
  font-size:13px;margin-bottom:9px;}
.picky-insight-title span {color:#59dca1;}
.picky-insight p {font-size:13px;line-height:1.65;color:#c5d8d0;margin:0;overflow-wrap:anywhere;}
.picky-source-heading {display:flex;align-items:center;gap:10px;}
.picky-source-icon {height:36px;width:36px;border-radius:10px;display:grid;place-items:center;
  background:#214639;color:#7ee3b3;font-weight:900;}
.picky-source-heading strong {display:block;color:#f2fcf5;font-size:13px;}
.picky-source-heading small {display:block;color:#9fb7b0;font-size:11px;margin-top:4px;}
div[data-testid="stDialog"] [role="dialog"]:has(.picky-modal-hero) {
  max-width:min(1060px,94vw)!important;width:min(1060px,94vw)!important;
  max-height:min(94dvh,1100px);overflow-y:auto;
  border:1px solid rgba(66,147,111,.34);
  border-radius:20px;background:#101721!important;
  box-shadow:0 24px 65px rgba(0,0,0,.56);
}
div[data-testid="stDialog"] [role="dialog"]:has(.picky-modal-hero) [data-baseweb="tab"] {
  color:#a6bec0;font-weight:650;
}
div[data-testid="stDialog"] [role="dialog"]:has(.picky-modal-hero) [aria-selected="true"] {
  color:#70e4a7!important;
}
/* Give manual research and collapse controls the same high contrast as the concept. */
.st-key-run_manual_ai_scout button {
  min-height:46px!important;border-radius:11px!important;
  background:linear-gradient(105deg,#3ccc8c,#2caa83)!important;
  color:#0d2a1e!important;font-size:14px!important;font-weight:800!important;
}
.st-key-run_manual_ai_scout button [data-testid="stIconMaterial"],
.st-key-run_manual_ai_scout button p { color:#0d2a1e!important; }
.st-key-run_manual_ai_scout button:hover {filter:brightness(1.12);}
@media (max-width:960px) {
  .picky-player-metrics .picky-chip:nth-child(2) {display:none;}
  .picky-hero {padding:17px;}
  .picky-player-row {gap:10px;}
  .picky-player-rank {width:23px;}
  .picky-photo {width:53px;height:53px;}
}
@media (max-width:760px) {
  [class*="st-key-ai_candidate_"] {padding:12px!important;}
  [class*="st-key-ai_candidate_"] [data-testid="stHorizontalBlock"]{
    flex-direction:column!important;flex-wrap:nowrap!important;gap:9px!important;
  }
  [class*="st-key-ai_candidate_"] [data-testid="stHorizontalBlock"] > [data-testid="column"]{
    width:100%!important;flex:1 1 auto!important;min-width:0!important;
  }
  [class*="st-key-ai_candidate_"] button {min-height:40px!important;}
  .picky-hero-body {align-items:flex-start;gap:13px;}
  .picky-photo--hero {width:75px;height:83px;border-radius:15px;}
  .picky-photo--hero .picky-photo-fallback {font-size:25px;}
  .picky-hero h3 {font-size:23px;}
  .picky-hero-summary {font-size:12px;}
  .picky-chip {font-size:9px;padding:4px 6px;}
  .picky-photo--modal {width:70px;height:77px;border-radius:13px;}
  .picky-modal-hero {gap:12px;padding:12px;}
  .picky-modal-hero h3 {font-size:21px;}
  div[data-testid="stDialog"] [role="dialog"]:has(.picky-modal-hero) {
    max-width:98vw!important;width:98vw!important;
  }
  [class*="st-key-ai_candidate_"]:hover {transform:none;}
}
@media (prefers-reduced-motion:reduce) {
  [class*="st-key-ai_candidate_"]{transition:none!important;}
  div[data-testid="stDialog"] [role="dialog"]:has(.picky-modal-hero) {animation:none!important;}
}
</style>
""",
        unsafe_allow_html=True,
    )
