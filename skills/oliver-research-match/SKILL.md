---
name: oliver-durr-research-match
description: "Evaluate research calls, RFPs, and funding opportunities for fit with Oliver Dürr's research interests. Use this skill whenever you need to assess whether a specific call, grant announcement, journal special issue, or research opportunity aligns with his research directions in probabilistic AI, uncertainty quantification, Bayesian deep learning, causal inference, decision-making under uncertainty, and agentic AI with causal reasoning. This skill works for: reviewing individual calls, batch-screening multiple opportunities, analyzing call descriptions for keyword/thematic relevance, generating relevance scores with reasoning, and producing structured match reports. Always use this skill when evaluating research opportunities against Oliver's profile."
---

# Oliver Dürr Research Match Skill

This skill helps identify and evaluate research calls, RFPs, and funding opportunities that align with Oliver Dürr's research interests.

## Quick Reference: Research Profile

**Core Research Interests:**
- Probabilistic AI and uncertainty quantification (aleatoric and epistemic)
- Bayesian deep learning and scalable Bayesian approximations
- Integration of deep learning with statistical models
- Causal inference and causal deep learning
- Decision-making under uncertainty
- Agentic AI with causal and statistical reasoning

**Primary Application Domains:**
- Medical imaging and high-content screening
- Energy systems, renewable energy, and decarbonization
- Environmental and climate modeling
- Autonomous and sensor-based systems
- Healthcare decision support

**Key Methodologies:**
- Deep Transformation Models
- Variational inference and Bernstein Flows
- Single-Shot Dropout and subspace inference methods
- Causal DAG-based modeling
- Interpretable and probabilistic model combinations

**Strong Fit:**
- Probabilistic AI, uncertainty quantification
- Bayesian methods and deep learning
- Causal machine learning and agentic AI with causal reasoning
- Robustness and AI reliability
- Real-world applications with high decision costs

**Low Priority / No Fit:**
- Purely deterministic deep learning without uncertainty consideration
- Black-box optimization without interpretability
- System integration or software engineering projects
- AI projects lacking causal or uncertainty reasoning
- Purely descriptive tasks without decision relevance

---

## Workflow: Evaluating a Research Call

### 1. Analyze Call Content

Read the entire call/RFP carefully, noting:
- **Primary themes**: What is the call really about?
- **Methodological focus**: What methods are emphasized or requested?
- **Application domains**: Where will the research be applied?
- **Key challenges**: What problems are they trying to solve?
- **Decision-relevance**: Does success require reliable uncertainty quantification or causal reasoning?

### 2. Score Across Five Dimensions

Evaluate relevance on a **0–100 scale** across these dimensions. Use the guidance below for each:

#### A. **Methodological Alignment (0–100)**
Does the call match Oliver's core technical interests?

- **80–100**: Explicitly mentions probabilistic AI, uncertainty quantification, Bayesian methods, causal inference, interpretability, or statistical modeling
- **60–79**: Implies strong need for these (e.g., "robust predictions," "quantify confidence," "decision-relevant AI")
- **40–59**: Tangential fit (e.g., "deep learning for complex data," but no explicit uncertainty/causal angle)
- **20–39**: Weak fit (e.g., mentions general AI, but doesn't align with probabilistic/causal focus)
- **0–19**: No fit or explicit mismatch (e.g., pure deterministic prediction, black-box optimization)

#### B. **Application Domain Alignment (0–100)**
Does the application domain match Oliver's expertise and interests?

- **80–100**: Medical (imaging, outcome prediction), energy (forecasting, renewable), or environmental applications
- **60–79**: Healthcare, autonomous systems, or safety-critical applications requiring uncertainty
- **40–59**: General scientific or high-impact domains where uncertainty matters
- **20–39**: Application domains where uncertainty is secondary
- **0–19**: Application area Oliver has not worked in and doesn't explicitly welcome

#### C. **Data & Problem Characteristics (0–100)**
Does the problem context match the conditions where Oliver's methods shine?

**High fit indicators:**
- Limited data regime, high costs of wrong decisions
- Distribution shifts or unknown classes
- High-dimensional data
- Need for calibration and uncertainty estimates
- Interpretability critical for decision-making

**Scoring:**
- **80–100**: Multiple high-fit indicators present
- **60–79**: Several relevant characteristics
- **40–59**: Some alignment, but not ideal testbed
- **20–39**: Misaligned (e.g., abundant labeled data, pure prediction accuracy focus)
- **0–19**: No match

#### D. **Decision-Making Relevance (0–100)**
Does success require decisions under uncertainty, or is pure prediction sufficient?

- **80–100**: Explicitly about decision support, optimization, planning, or intervention assessment
- **60–79**: Clear decision context implied (e.g., clinical decision support, energy planning)
- **40–59**: Prediction with some decision implications
- **20–39**: Prediction-focused with limited decision context
- **0–19**: Pure description, benchmarking, or prediction without decision stakes

#### E. **Strategic Fit (0–100)**
Overall fit with Oliver's research vision and funding priorities?

Consider:
- Does it open new application domains Oliver welcomes?
- Does it advance his research themes?
- Is it a distraction from core interests?
- Are there co-author or collaboration opportunities?

**Scoring:**
- **80–100**: Highly strategic, advances core vision
- **60–79**: Good fit, worth pursuing
- **40–59**: Acceptable fit if resources available
- **20–39**: Marginal, only pursue if very high funding
- **0–19**: Misaligned or low priority

---

### 3. Calculate Overall Score

**Simple average of all five dimensions:**

```
Overall Match Score = (A + B + C + D + E) / 5
```

### 4. Interpret the Score

- **80–100**: **STRONG MATCH** — Pursue actively. High probability of good fit and meaningful contribution.
- **60–79**: **GOOD MATCH** — Worth serious consideration. May require some adaptation or collaboration to achieve full alignment.
- **40–59**: **MODERATE MATCH** — Potential fit, but significant adaptation needed. Evaluate timeline, co-author availability, and strategic priority.
- **20–39**: **WEAK MATCH** — Limited alignment. Only pursue if significant funding and strong co-authors offset mismatch.
- **0–19**: **NO MATCH** — Does not align with research directions. Low priority unless strategic exceptions apply.

---

### 5. Generate Summary Report

Provide a structured report with:

1. **Call Title & Deadline**
2. **Overall Match Score: X/100** (with color coding or emoji: 🟢 strong, 🟡 good, 🟠 moderate, 🔴 weak)
3. **Dimension Breakdown:**
   - Methodological Alignment: X/100
   - Application Domain: X/100
   - Data & Problem Characteristics: X/100
   - Decision-Making Relevance: X/100
   - Strategic Fit: X/100

4. **Key Alignment Points** (bulleted, 3–5 items)
   - What specifically matches Oliver's interests?

5. **Gaps or Concerns** (bulleted, if any)
   - Where does the call diverge from his research?
   - What would need to be adapted?

6. **Recommended Action**
   - **Pursue actively**, **Consider if resources available**, **Monitor for future versions**, or **Pass**

7. **Suggested Approach** (if pursuing)
   - Key collaborators to involve?
   - Which research direction(s) to emphasize?
   - Potential co-authors or institutional partners?

---

## Batch Evaluation

If evaluating multiple calls:

1. **Create a summary table** with columns:
   - Call Name
   - Deadline
   - Overall Match Score
   - Recommendation (🟢 Pursue / 🟡 Consider / 🔴 Pass)

2. **Prioritize** by score and deadline

3. **Provide a narrative summary** of top matches with reasoning

4. **Flag emerging themes** — Are there consistent methodological or domain trends Oliver should track?

---

## Key Phrases to Watch For

**Strong signals (high score potential):**
- "uncertainty quantification," "Bayesian," "probabilistic"
- "reliable AI," "trustworthy," "interpretable"
- "decision support," "planning," "optimization," "agentic"
- "causal," "intervention," "treatment effect"
- "limited data," "distribution shift," "robustness"
- "medical imaging," "healthcare," "energy forecasting"
- "calibration," "confidence," "model validation"

**Weak signals (low score potential):**
- "purely deterministic," "black-box," "accuracy only"
- "system integration," "software engineering"
- "benchmark comparison," "state-of-the-art"
- "abundant labeled data," "perfect information"
- "prediction at scale," "inference speed"

---

## Example: Strong Match

**Call:** "Probabilistic Forecasting for Renewable Energy Grids: Quantifying Uncertainty in Volatile Systems"

**Scores:**
- Methodological: 95 (explicitly mentions probabilistic forecasting, uncertainty)
- Domain: 90 (renewable energy is core application area)
- Data characteristics: 85 (volatile, time-series data, distribution shifts common)
- Decision-making: 85 (planning and optimization require quantified uncertainty)
- Strategic: 90 (advances energy research direction, leverages existing expertise)

**Overall: 89/100 — STRONG MATCH 🟢**

---

## Example: Poor Match

**Call:** "Accelerating Deep Neural Networks for Image Classification with GPU Optimization"

**Scores:**
- Methodological: 15 (purely deterministic, no uncertainty)
- Domain: 40 (medical imaging is an application, but not the focus)
- Data characteristics: 25 (implies large labeled datasets, speed-focused)
- Decision-making: 10 (prediction accuracy only, no decision context)
- Strategic: 5 (system/engineering focus, not research direction)

**Overall: 19/100 — NO MATCH 🔴**

---

## Notes for Users

- **Be thorough in step 1**: Take time to understand the call deeply. Surface analysis leads to mismatches.
- **Use the scoring ranges carefully**: They're designed to differentiate meaningfully across Oliver's research portfolio.
- **Document reasoning**: Future evaluations benefit from consistent decision-making.
- **Update the profile**: As Oliver's research evolves, revisit these guidelines and adjust thresholds.
- **Consider timing**: A 60/100 match might be strong if resources are available; weak if deadlines are tight.

