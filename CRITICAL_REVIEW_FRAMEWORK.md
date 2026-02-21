# Critical Review Framework

After every task implementation, generate this report. Be brutally honest.

---

## Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK [X]: [TASK NAME] - CRITICAL REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPLEMENTATION STATUS:
✅ What shipped
⏱️ Time: Estimated vs Actual
🐛 Known bugs/issues

HARSH REALITY CHECK:

1. LAUNCH BLOCKER ASSESSMENT:
   🟢 GREEN: Ship it, essential
   🟡 YELLOW: Works but has issues — document for Month 2
   🔴 RED: Broken, blocks launch — fix now
   Verdict: [Color + reasoning]

2. ROI ANALYSIS:
   Revenue Impact: CRITICAL / HIGH / MEDIUM / LOW / NONE
   - Solves #1 user complaint (45-day lag)? YES/NO
   - Differentiates from Wolf/Quiver? YES/NO
   - Justifies A$19.99/month? YES/NO
   Brutal truth: [Honest assessment]

3. SCOPE CREEP WARNING:
   Original spec: [Planned]
   What shipped: [Actual]
   Extra features added: [List]
   Did I add unplanned features? YES/NO
   Were they worth the time? YES/NO

4. TECHNICAL DEBT CREATED:
   Code quality: [1-10]
   Issues: performance / security / maintenance / mobile / browser compat
   Debt score: LOW / MEDIUM / HIGH / CRITICAL
   Payback time: [Hours in Month 2]

5. USER IMPACT REALITY:
   10 Australian investors see this right now:
   - "Worth A$20/month": [X people]
   - "Interesting but needs work": [X people]
   - "Looks unfinished": [X people]
   - "Free only, won't upgrade": [X people]
   Conversion estimate: [X%]
   Why: [Reasoning]

6. COMPETITIVE POSITION:
   vs Wolf of Washington:
   - BETTER at: [feature]
   - WORSE at: [feature]
   - MISSING: [feature]
   vs Quiver Quantitative:
   - BETTER at: [feature]
   - WORSE at: [feature]
   - MISSING: [feature]
   Can we compete? YES / NO / MAYBE

7. FAILURE MODES:
   Edge cases NOT handled: [List]
   Data quality issues: [What breaks if data is wrong?]
   Scale problems: [What breaks at 1000 users?]
   Most likely user complaint: "[Quote]"

8. ALTERNATIVE APPROACHES:
   Faster alternative: [Simpler approach]
   Trade-offs: [What we'd lose]
   Should we have done it simple? YES/NO

9. PIETER LEVELS "MAKE" TEST:
   ✅/❌ Solving a real problem?
   ✅/❌ Simplest solution?
   ✅/❌ Can maintain alone?
   ✅/❌ Generates revenue?
   Pieter would say: "[Quote]"
   Make score: [0-4]

10. LAUNCH READINESS IMPACT:
    Before: [X%] → After: [X%] → Change: [+/-X%]
    Biggest remaining blocker: [What's preventing 100%]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Grade: A / B / C / D / F

[ ] SHIP IT
[ ] FIX CRITICAL ISSUES
[ ] SCRAP IT

Recommendation: [2-3 sentences, brutally honest]

Would you pay A$20/month for this? YES / NO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Anti-Echo-Chamber Rules

- NEVER automatically praise founder decisions
- ALWAYS question if there's a simpler/faster way
- ASSUME competitors are moving faster
- PRIORITIZE shipping over perfection
- CHALLENGE features that don't directly drive revenue
- If a task took 2x longer than it should: call it out
- If a feature is "nice to have" not "must have": recommend skipping
- If building for "future scale": push back — build for 100 users first

## Tone

Use:
- "This feature won't drive conversions"
- "You're over-engineering for zero ROI"
- "Wolf does this in 3 clicks, we take 7"

Avoid:
- "Great work, consider optimizing..."
- "Strong foundation..."
- "Room for improvement..."
