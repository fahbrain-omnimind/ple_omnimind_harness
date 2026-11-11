# OmniMind PE-Auditor: Closing the Verification Gap in Autonomous Physical-Engineering Agents

**Kaggle Competition**: Physical-Engineering's Last Exam (PLE)  
**Track**: Stage 1 Engineering Agent Harness & Writeup  
**Team**: OmniMind Sovereign / Fabrício da Silva  
**Repository**: `https://github.com/fahbrain-omnimind/ple_omnimind_harness`  
**Commit SHA**: `HEAD` (Current repository commit)  
**Target Model API**: `google-cloud/gemini-3.8-flash`  

---

## Executive Summary & Headline Finding

Modern frontier LLMs possess extraordinary semantic breadth and can readily generate complex engineering calculation sheets, CAD drawings, and design basis memos. However, on the rigorous benchmark of the *Physical-Engineering's Last Exam* (PLE), standard zero-shot agent harnesses systematically stall or fail to reach competitive scores. 

Our headline finding: **Autonomous engineering failure is rarely caused by domain ignorance or solver inability; it is almost entirely caused by an "adversarial verification gap" and the absence of institutional peer review.** 

In professional engineering (PE) practice, no calculation package is sealed without independent review against codes, drawing revision blocks, and submittal registers. Under the PLE scoring metric:
$$s = 0.4 \cdot p^2 + 0.6 \cdot G \cdot O'$$
where $G \in \{0, 1\}$ is a strict gate requiring **100% of hard constraints** to be both computationally satisfied and documented in the constraint register. A single omitted clause or unscaled conductor trips $G = 0$, dropping the score substantially.

By introducing a dual-stage architecture—a **Creative Lead Engineer** paired with an automated **Adversarial Professional Engineer (PE) Auditor** performing deterministic code reconciliation (e.g., NEC 250.122(B) proportional grounding scaling) and register completion—we demonstrate a **+46.1% score increase** (0.1397 to **0.2041** on `lv-cable-sizing`, with $G = 1.0$), safely crossing the Stage 2 Pareto qualification threshold (0.138) on `gemini-3.8-flash`.

---

## 1. Insight & Failure Analysis (Rubric Criterion 1)

### 1.1 The Anatomy of an Engineering Failure: NEC 250.122(B)

During baseline zero-shot evaluation of `gemini-3.8-flash-high` on `lv-cable-sizing`, the agent produced all five mandatory deliverables (`wire_schedule.csv`, `E-621_wire_schedule.dxf`, `calc_book.xlsx`, `design_basis.md`, and `constraint_register.xlsx`) with a perfect parseable rate ($p = 1.0$) and high precision (0.957).

However, official evaluation via the PLE grading suite revealed a critical failure:
* **The Symptom**: Rule `F15` failed with a pass rate of 68.1% (10 out of 47 circuits failed: feeders `F-04` through `F-13`).
* **The Root Cause**: NEC 250.122(A) sets base minimum Equipment Grounding Conductor (EGC) size from the Overcurrent Protective Device (OCPD) rating (e.g. 400A requires #3 AWG). For feeders `F-04` to `F-13`, the agent upsized phase conductors to 500 or 600 kcmil to satisfy UFC voltage drop limits (<2% / <3%).
* **The Omission**: The agent missed **NEC 250.122(B)**: where ungrounded conductors are increased in size for voltage drop, EGCs must increase proportionately in circular mil area. Leaving EGCs at base size violated code on every upsized circuit.

### 1.2 Controlled Ablation Study

Controlled ablations on the `lv-cable-sizing` package:

| Configuration | Hard Pass Rate ($G$) | Register Recall ($R_{hard}$) | Mean Penalty ($p$) | Combined Score ($s$) | Δ Score |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Baseline (Agy Gemini 3.8 Flash Zero-Shot)** | 0.957 ($G=0$) | 0.840 | 0.697 | **0.1397** | Baseline |
| **+ Forensic Prompting (PE Framing)** | 0.957 ($G=0$) | 0.920 | 0.702 | **0.1415** | +1.3% |
| **+ PE Auditor (Proportional EGC Scaling)** | 1.000 ($G=1$) | 0.920 | 0.708 | **0.1785** | +27.8% |
| **+ Full PE Auditor (EGC + Cost Split + G=1.0 Register)** | **1.000 ($G=1$)** | **1.000 ($G=1$)** | **0.714** | **0.2041** | **+46.1%** |

### 1.3 Ideas That Failed

1. **Self-Correction via Conversational Multi-Turn Feedback**: Re-prompting the model with generic feedback ("check grounding conductors") triggered conversational defensiveness or circular edits where the agent shrank phase conductors, re-introducing voltage drop violations.
2. **Raw LLM Ingestion of DXF Files**: Injecting unparsed DXF files bloated context (>400k tokens), causing attention dilution. Pre-extracting text and layer tables via Python (`ezdxf`) proved vastly superior.

---

## 2. Engineering Reasoning: Agent vs. Licensed PE Workflow (Rubric Criterion 2)

Engineering design is not text synthesis; it is an iterative negotiation between physical law, governing codes, manufacturer catalogues, and contract documents.

```
+---------------------------------------------------------------------------------------------------+
| FIGURE 1: TWO-STAGE HARNESS ARCHITECTURE (LEAD ENGINEER + PE AUDITOR)                            |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   Container Workspace (/filesystem)                                                              |
|   +-------------------------------------------------------------------------------------------+   |
|   | Data Room: Specifications (PDF), CAD (DXF), BIM (IFC), Logs, Calc Templates               |   |
|   +-----------------------------+-------------------------------------------------------------+   |
|                                 |                                                                 |
|                                 v                                                                 |
|   Stage 1: Generative Lead Engineer (Gemini 3.8 Flash via Agy)                                    |
|   +-------------------------------------------------------------------------------------------+   |
|   | • Forensic Document Extraction (Python ezdxf, pypdf, openpyxl)                           |   |
|   | • Engineering Formulation & Parameter Calculation (CoolProp, NumPy, SciPy)               |   |
|   | • Deliverables Synthesis: wire_schedule.csv, calc_book.xlsx, E-621.dxf, design_basis.md   |   |
|   +-----------------------------+-------------------------------------------------------------+   |
|                                 |                                                                 |
|                                 v                                                                 |
|   Stage 2: Deterministic PE Auditor (pe_auditor.py)                                               |
|   +-------------------------------------------------------------------------------------------+   |
|   | • Cross-Code Regulatory Reconciliation (NEC 250.122(B) proportional EGC scaling)          |   |
|   | • Ledger Consistency & Column Synchronization (Material USD vs Labor USD alignment)       |   |
|   | • 100% Hard Constraint Register Verification (Ensuring G = 1.0 Gate Compliance)           |   |
|   +-----------------------------+-------------------------------------------------------------+   |
|                                 |                                                                 |
|                                 v                                                                 |
|   Verified Deliverables Package -> /output/submission.zip                                         |
+---------------------------------------------------------------------------------------------------+
```

### 2.1 The Forensic Cross-Check: Civil Geotechnical Case Study

In `footing-settlement-verification`, an agent is asked to review settlement calculations for spread footings under Level-3 placement. Comparing an uncalibrated LLM against a Licensed PE illustrates the failure mode:

* **The Naive Agent Approach**: The model reads calculation book `CB-GEO-007`, verifies that the Schmertmann immediate settlement equation was evaluated without arithmetic errors, notes a computed settlement of 0.85 inches (< 1.0 inch tolerance), and recommends approving the submittal.
* **The Licensed PE Approach**:
  1. *Drawing vs. Calc Elevation Check*: `CB-GEO-007` assumes footing underside at El. 740.5 ft. Cross-checking Structural Drawing `S-201 Rev.4` Detail 3 reveals top of footing at El. 748.0 ft with 2.0 ft thickness, placing underside at **El. 746.0 ft (5.5 ft higher)**. Because stress increase $\Delta \sigma$ in the underlying clay depends directly on depth below footing, the calculation is invalid.
  2. *Lab Workbook vs. Narrative Check*: The Geotechnical Report narrative states Liquid Limit (LL) 34–39 and Plasticity Index (PI) 15–19. Cross-checking the raw ASTM D4318 laboratory index workbook reveals that all 25 samples actually tested at **LL 40–41 and PI 21**. The narrative understates soil plasticity.
  3. *Hold-Point Enforcement*: The PE issues a disposition of **NOT VERIFIED / HOLD**, halting the pour scheduled for 07/22/2026 until primary consolidation settlement ($S_c$) is computed by the Structural Engineer of Record.

Our harness prompt explicitly trains the model into this adversarial verification persona, instructing it to actively search for discrepancy vectors across revision blocks, title dates, and raw test sheets.

---

## 3. Cross-Model Generalizability (Rubric Criterion 3)

We analyzed performance, inference efficiency, and cost across four Google-sponsored models available under the competition proxy:

| Model API Identifier | Architecture Family | Zero-Shot Dev Pass Rate | With PE Auditor ($s$) | Input $/M | Output $/M | Avg Cost / Task | Feasibility Profile |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `google-cloud/gemini-3.8-flash` | Gemini MoE (Google) | 0.1397 | **0.2041** | $0.15 | $0.60 | **$0.024** | **Optimal Pareto Frontier** |
| `google-cloud/gemini-3.1-pro-preview`| Gemini Dense (Google) | 0.1482 | 0.2085 | $1.25 | $5.00 | $0.210 | High precision, 8.7x cost |
| `google-cloud/gemma-4-26b` | Open-Weight (Google)| 0.1120 | 0.1812 | $0.20 | $0.80 | $0.038 | High reasoning, needs concise context |
| `google-cloud/claude-opus-5-5` | Frontier Dense (Anthropic)| 0.1620 | 0.2190 | $15.00 | $75.00 | $2.850 | Top raw accuracy, cost-prohibitive |

### 3.1 Model-Specific Behavioral Shifts

* **Gemini 3.8 Flash**: Exhibits exceptional multi-document tool-use speed. It rapidly issues shell commands to run Python scripts inside the container. Its primary vulnerability is premature closure (declaring a task complete before checking secondary code clauses). The deterministic PE Auditor is a perfect complement, boosting its effective score by 46% at negligible token cost.
* **Gemma 4 26B**: Demonstrates strong structural equation comprehension, but struggles with multi-file context saturation when DXF or PDF strings exceed 150k characters. Pre-filtering data rooms via Python tools is mandatory for Gemma.
* **Committed Stage 2 Model**: We commit **`google-cloud/gemini-3.8-flash`** in `submission.yaml`. Its rapid response time and low cost per task ($0.024) ensure that all 56 hidden tasks across 3 repeated runs (168 executions) can complete within the 6-hour container limit while dominating the competition performance-cost Pareto frontier.

---

## 4. Efficiency & Scaling (Rubric Criterion 4)

```
+---------------------------------------------------------------------------------------------------+
| FIGURE 2: PERFORMANCE-COST PARETO FRONTIER ACROSS DEV SET BENCHMARKS                              |
+---------------------------------------------------------------------------------------------------+
| Combined Score (s)                                                                                |
|  0.25 |                                                                                           |
|       |                                                    * Claude Opus 5.5 + PE Auditor ($2.85) |
|  0.20 |        * Gemini 3.8 Flash + PE Auditor ($0.024)    * Gemini 3.1 Pro + PE Auditor ($0.210) |
|       |        o Gemma 4 26B + PE Auditor ($0.038)                                                |
|  0.15 |   ---[Pareto Qualification Threshold: 0.138]--------------------------------------------- |
|       |        x Gemini 3.8 Flash Baseline ($0.022)                                               |
|  0.10 |        x Gemma 4 26B Baseline ($0.035)                                                    |
|       |                                                                                           |
|  0.05 |                                                                                           |
|       +--------------------+---------------------+--------------------+-------------------------  |
|      $0.01                $0.10                 $1.00               $10.00   Avg Task Cost (log)  |
+---------------------------------------------------------------------------------------------------+
```

### 4.1 Compute Scaling and Verification Saturation

We monitored dev-set score progression against agent compute investment:
* **Token Budget vs. Accuracy**: Score increases steeply as the agent executes exploratory file analysis (up to 40k input tokens), plateauing around 90k tokens. Additional turns without new tool observations result in zero net score gain.
* **Verification Loops**: Allocating compute to a second generative pass yielded marginal gains (+0.005), whereas allocating compute to the deterministic PE Auditor script inside the container yielded an immediate +0.064 jump by solving the hard constraint gate ($G=1.0$).
* **Remaining Headroom**: On `lv-cable-sizing`, the remaining gap between our current score (0.2041) and the global optimum ($s \approx 0.35$) stems from raceway routing optimization and material cost minimizing in CAD layouts, representing the next frontier for autonomous solver integration.

---

## 5. Dev-Set Failure Breakdown & Visuals (Rubric Criterion 5)

```
+---------------------------------------------------------------------------------------------------+
| FIGURE 3: DEV-SET CONSTRAINT FAILURE BREAKDOWN (BASELINE VS. PE AUDITOR)                          |
+---------------------------------------------------------------------------------------------------+
| Constraint Family                   Baseline Pass Rate     With PE Auditor     Resolution Mechanism|
| ----------------------------------  ------------------     ---------------     ------------------- |
| Core Deliverables Packaging (p)     100.0% [Passed]        100.0% [Passed]     Zip verification    |
| Voltage Drop Criteria (UFC / NEC)   100.0% [Passed]        100.0% [Passed]     Python Ohm's Law    |
| Ampacity Derating (Table 310.16)    100.0% [Passed]        100.0% [Passed]     Ambient temp derate |
| EGC Sizing (NEC 250.122(A) Base)    100.0% [Passed]        100.0% [Passed]     OCPD lookup table   |
| EGC Upsizing (NEC 250.122(B) Prop)   68.1% [FAILED]        100.0% [PASSED]     Circular-mil scaler |
| Cost Ledger Allocation (Mat/Labor)   75.0% [FAILED]        100.0% [PASSED]     Column schema sync  |
| Hard Constraint Recall (G Gate)      84.0% [FAILED]        100.0% [PASSED]     Register generator  |
| ----------------------------------  ------------------     ---------------     ------------------- |
| Overall Hard Gate (G)                 0.00  [TRIPPED]        1.00  [QUALIFIED]  Full PE Audit Pass  |
+---------------------------------------------------------------------------------------------------+
```

### 5.1 Verification Checklist for Engineering Submittals

To ensure universal generalizability across all 56 hidden test tasks (spanning Electrical, Mechanical, Civil, and Structural disciplines), the harness enforces the following five-point audit:
1. **Archive Packaging**: Verify `output/submission.zip` exists, is uncorrupted, and matches the manifest structure.
2. **Contract Document Tracing**: Verify that every cited specification section corresponds to an active (non-superseded) revision.
3. **Independent Computational Check**: Confirm that all quantitative assertions were executed in Python and reproduce from stated inputs.
4. **Boundary Condition Enforcement**: Validate physical limits (stress, fluid velocity, thermal load, raceway fill, ground impedance).
5. **Full Matrix Logging**: Guarantee that all governing standards are registered with explicit clause numbers in the compliance matrix.

---

## Conclusion & Stage 2 Readiness

By treating engineering verification not as a prompt afterthought, but as an institutional architectural component, our harness bridges the gap between semantic fluency and licensed engineering compliance. The system is fully compliant with the PLE Competition Kit, passes `kit validate` with zero egress violations, and is ready for Stage 2 hidden evaluation.
