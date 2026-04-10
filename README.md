<p align="center">
  <h1 align="center">📊 ISRI — Indian SME Readiness Index</h1>
  <p align="center">
    A full-stack assessment platform that quantifies IoT/digital-adoption barriers for Indian SMEs,<br/>
    computes a weighted <strong>Impact Value (ISRI)</strong> per barrier, and generates AI-powered<br/>
    analysis reports & strategic roadmaps.
  </p>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Formula System](#formula-system)
  - [Layer 1 — Barrier Scores](#layer-1--barrier-scores-15-barriers)
  - [Layer 2 — Cost Factor Impact](#layer-2--cost-factor-impact)
  - [Layer 3 — KPI Factor Impact](#layer-3--kpi-factor-impact)
  - [Final ISRI Calculation](#final-isri-impact-value-calculation)
  - [Severity Classification](#severity-classification)
- [All 15 Barriers — Detailed Formulas](#all-15-barriers--detailed-formulas)
- [Cost Factor Weight Matrix](#cost-factor-weight-matrix)
- [KPI Factor Weight Matrix](#kpi-factor-weight-matrix)
- [AI Report Generation](#ai-report-generation)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

The **ISRI (Indian SME Readiness Index)** platform helps organisations measure how ready they are for IoT and digital transformation. It works in **three layers**:

1. **Barrier Scores** — 15 barriers are scored from 0–10 using weighted sub-indicators collected from the company.
2. **Cost Factor Impact** — 20 cost factors are multiplied by a per-barrier weight matrix to quantify financial pressure per barrier.
3. **KPI Factor Impact** — 17 operational KPIs are multiplied by a per-barrier weight matrix to quantify performance pressure per barrier.

These three layers are normalised and combined into a single **Impact Value (ISRI)** per barrier. The top 3 highest-impact barriers are identified and fed into an AI (OpenRouter / Mistral) to generate:

- 📄 **Comprehensive Barrier Analysis** — detailed report for all 15 barriers
- 🗺️ **Strategic Roadmap** — phased action plan for the top 3 barriers

---

## Architecture

```
┌──────────────────┐
│     Frontend     │
│    (Next.js)     │
└────────┬─────────┘
         │  POST /generate_full_report
         ▼
┌──────────────────────────────────────────────────┐
│              FastAPI Backend (app.py)             │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────────┐   ┌──────────────────────┐  │
│  │ models/          │   │ config/settings.py   │  │
│  │  input_models.py │   │  weights, API keys   │  │
│  └────────┬────────┘   └──────────────────────┘  │
│           │                                      │
│  ┌────────▼────────────────────────────────────┐ │
│  │             services/                       │ │
│  │  barrier_service.py  → Layer 1 scores       │ │
│  │  cost_service.py     → Layer 2 scores       │ │
│  │  kpi_service.py      → Layer 3 scores       │ │
│  │  isri_service.py     → Final ISRI + Top N   │ │
│  │  ai_service.py       → Report generation    │ │
│  │  database_service.py → MongoDB persistence  │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  ┌─────────────────┐                             │
│  │ utils/           │                             │
│  │  pdf_utils.py    │  → Markdown → PDF          │
│  └─────────────────┘                             │
└──────────────────────────────────────────────────┘
         │
         ▼
   ZIP with 2 PDFs
   ├─ 01_Comprehensive_Barrier_Analysis.pdf
   └─ 02_Strategic_Roadmap_Top_3_Barriers.pdf
```

---

## Formula System

### Layer 1 — Barrier Scores (15 Barriers)

Each barrier has **2–3 sub-indicators**. Every indicator is scaled using a formula that produces a score contribution, and the contributions are summed. The total is **clamped to [0, 10]**.

**General pattern:**

```
Sub-score = f(input) × weight × 10
Barrier Total = clamp(Σ sub-scores, 0, 10)
```

Where `f(input)` is either:

- **(1 − input / threshold)** — higher input ⇒ lower risk (inverted)
- **(input / threshold)** — higher input ⇒ higher risk (direct)
- **categorical mapping** — e.g. frequency labels → numeric values

> All percentage inputs are on a **0–100** scale (divided by 100 in the formula).

---

### Layer 2 — Cost Factor Impact

**20 cost factors** are collected (each rated on a scale). A **20 × 15 weight matrix** maps the relevance of each cost factor to each barrier. The weighted sum of all cost factors produces a **cost impact score per barrier**.

```
CostImpact(barrier_i) = Σⱼ (cost_factor_j × weight_matrix[i][j])
```

Cost factors include: Labour, Depreciation, R&D, Maintenance, Supply Chain, Technology Infrastructure, Training, Regulatory Compliance, Insurance, Marketing, and more.

---

### Layer 3 — KPI Factor Impact

**17 KPIs** are collected. A **17 × 15 weight matrix** maps each KPI's relevance to each barrier.

```
KPIImpact(barrier_i) = Σⱼ (kpi_factor_j × weight_matrix[i][j])
```

KPIs include: Asset Efficiency, Process Quality, Product Quality, Safety, Time-to-Market, Customer Satisfaction, Employee Productivity, ROI, Financial Health, Talent Retention, and more.

---

### Final ISRI (Impact Value) Calculation

Each barrier's three layer scores are **normalised** (divided by the layer total across all 15 barriers), then combined with configurable weights:

```
barrier_norm  = barrier_score  / Σ(all barrier scores)
cost_norm     = cost_impact    / Σ(all cost impacts)
kpi_norm      = kpi_impact     / Σ(all KPI impacts)

ISRI(barrier_i) = (0.3 × barrier_norm) + (0.3 × cost_norm) + (0.4 × kpi_norm)
```

| Weight                 | Layer         | Default  |
| ---------------------- | ------------- | -------- |
| `WEIGHT_BARRIER_SCORE` | Barrier Score | **0.30** |
| `WEIGHT_COST_FACTOR`   | Cost Factor   | **0.30** |
| `WEIGHT_KPI_FACTOR`    | KPI Factor    | **0.40** |

The barriers are then **sorted by ISRI descending** and the **top 3** are selected for the strategic roadmap.

---

### Severity Classification

| Barrier Score | Level              |
| ------------- | ------------------ |
| 0.0 – 3.0     | 🟢 Low             |
| 3.1 – 7.0     | 🟡 Moderate        |
| 7.1 – 8.5     | 🟠 High            |
| 8.6 – 10.0    | 🔴 Critically High |

---

## All 15 Barriers — Detailed Formulas

> Notation: `w` = weight, `t` = threshold, `÷` means safe division (returns 0 if divisor is 0).

### Barrier 1 — Skills & Training Deficiency

| #   | Indicator                                | Formula                   | Weight |
| --- | ---------------------------------------- | ------------------------- | ------ |
| i   | Training programs offered/yr (≥5 = good) | `(1 − min(input, 5) ÷ 5)` | 0.2    |
| ii  | % employees trained in digital tech      | `(1 − input / 100)`       | 0.5    |
| iii | Training budget (% of payroll)           | `(1 − input ÷ 2.5)`       | 0.3    |

### Barrier 2 — Employee Resistance & Turnover

| #   | Indicator                                | Formula             | Weight |
| --- | ---------------------------------------- | ------------------- | ------ |
| i   | Turnover rate after IoT (20% = alarming) | `input ÷ 20`        | 0.4    |
| ii  | % employees resisting change             | `(1 − input / 100)` | 0.35   |
| iii | Feedback sessions/yr (12 = good)         | `(1 − input ÷ 12)`  | 0.25   |

### Barrier 3 — Digital Comfort & Adoption

| #   | Indicator                                       | Formula             | Weight |
| --- | ----------------------------------------------- | ------------------- | ------ |
| i   | Digital skills workshops attended (5 = healthy) | `(1 − input ÷ 5)`   | 0.2    |
| ii  | % comfortable with digital tools                | `(1 − input / 100)` | 0.4    |
| iii | Adoption rate of new digital tools (%)          | `(1 − input / 100)` | 0.4    |

### Barrier 4 — Training Effectiveness & Investment

| #   | Indicator                                        | Formula             | Weight |
| --- | ------------------------------------------------ | ------------------- | ------ |
| i   | Training expenditure (% of op. costs, 5% = good) | `(1 − input ÷ 5)`   | 0.4    |
| ii  | Avg training hours/employee/yr (40h = norm)      | `input ÷ 40`        | 0.3    |
| iii | ROI on training (% productivity improvement)     | `(1 − input / 100)` | 0.3    |

### Barrier 5 — Knowledge Management & Sharing

| #   | Indicator                                 | Formula             | Weight |
| --- | ----------------------------------------- | ------------------- | ------ |
| i   | Knowledge-sharing sessions/yr (24 = good) | `(1 − input ÷ 24)`  | 0.3    |
| ii  | % employees with KMS access               | `(1 − input / 100)` | 0.4    |
| iii | KMS update frequency                      | Categorical map\*   | 0.3    |

\*Frequency mapping: Daily=0, Weekly=0.25, Monthly=0.5, Quarterly=0.75, Bi-Annually=0.875, Annually=1.0

### Barrier 6 — Regulatory & Compliance Risks

| #   | Indicator                                | Formula       | Weight |
| --- | ---------------------------------------- | ------------- | ------ |
| i   | Non-compliance incidents/yr (5 = crisis) | `input ÷ 5`   | 0.4    |
| ii  | % projects delayed by regulations        | `input / 100` | 0.4    |
| iii | Time to compliance (days, 180 = crisis)  | `input ÷ 180` | 0.2    |

### Barrier 7 — Lack of Standards & Interoperability

| #   | Indicator                                 | Formula            | Weight |
| --- | ----------------------------------------- | ------------------ | ------ |
| i   | Industry standards adopted (10 = healthy) | `(1 − input ÷ 10)` | 0.35   |
| ii  | % IoT devices conforming to architectures | `(1 − input ÷ 50)` | 0.4    |
| iii | % projects delayed by lack of standards   | `input / 100`      | 0.25   |

### Barrier 8 — Infrastructure & Connectivity Issues

| #   | Indicator                           | Formula             | Weight |
| --- | ----------------------------------- | ------------------- | ------ |
| i   | % locations with stable internet    | `(1 − input / 100)` | 0.3    |
| ii  | Avg internet speed (50 Mbps = good) | `(1 − input ÷ 50)`  | 0.2    |
| iii | IT outages/month (8 = crisis)       | `input ÷ 8`         | 0.5    |

### Barrier 9 — Funding & Financial Constraints

| #   | Indicator                             | Formula             | Weight |
| --- | ------------------------------------- | ------------------- | ------ |
| i   | Loan approval rate (out of 5)         | `(1 − input ÷ 5)`   | 0.4    |
| ii  | % projects delayed by lack of funding | `input / 100`       | 0.4    |
| iii | External funding ratio (%)            | `(1 − input / 100)` | 0.2    |

### Barrier 10 — Limited Business Impact / ROI

| #   | Indicator                                     | Formula            | Weight |
| --- | --------------------------------------------- | ------------------ | ------ |
| i   | YoY revenue growth from IoT (20% = good)      | `(1 − input ÷ 20)` | 0.4    |
| ii  | Profit margin improvement (5% = strong)       | `(1 − input ÷ 5)`  | 0.4    |
| iii | New revenue streams from IoT (3 = successful) | `(1 − input ÷ 3)`  | 0.2    |

### Barrier 11 — Vendor Dependency & Lock-in

| #   | Indicator                                | Formula       | Weight |
| --- | ---------------------------------------- | ------------- | ------ |
| i   | % operations reliant on vendors          | `input / 100` | 0.4    |
| ii  | Vendor delays/yr (5 = crisis)            | `input ÷ 5`   | 0.4    |
| iii | Vendor contract cost (% of op. expenses) | `input / 100` | 0.2    |

### Barrier 12 — High Implementation & Maintenance Costs

| #   | Indicator                                   | Formula       | Weight |
| --- | ------------------------------------------- | ------------- | ------ |
| i   | % IT budget allocated to IoT                | `input / 100` | 0.4    |
| ii  | Annual O&M costs (% op. costs, 5% = crisis) | `input ÷ 5`   | 0.3    |
| iii | Integration costs (% of project cost)       | `input / 100` | 0.3    |

### Barrier 13 — Regulatory Compliance Management

| #   | Indicator                             | Formula             | Weight |
| --- | ------------------------------------- | ------------------- | ------ |
| i   | Regulatory violations/yr (4 = crisis) | `input ÷ 4`         | 0.5    |
| ii  | % audits passed without issues        | `(1 − input / 100)` | 0.3    |
| iii | Internal policy update frequency      | Categorical map\*   | 0.5    |

\*Frequency mapping: Monthly=0.25, Quarterly=0.5, Bi-Annually=0.75, Annually=1.0

### Barrier 14 — Standards & Framework Adoption

| #   | Indicator                                   | Formula             | Weight |
| --- | ------------------------------------------- | ------------------- | ------ |
| i   | % standards-compliant IoT devices           | `(1 − input / 100)` | 0.4    |
| ii  | Industry guidelines implemented (10 = good) | `(1 − input ÷ 10)`  | 0.6    |

> _Barrier 14 has only 2 indicators._

### Barrier 15 — Customer Data Privacy Concerns

| #   | Indicator                                | Formula             | Weight |
| --- | ---------------------------------------- | ------------------- | ------ |
| i   | % customers refusing to share data       | `input / 100`       | 0.4    |
| ii  | Data-sharing complaints/yr (25 = crisis) | `input ÷ 25`        | 0.35   |
| iii | % contracts with data-sharing agreements | `(1 − input / 100)` | 0.25   |

---

## Cost Factor Weight Matrix

The 20 cost factors and their weights (0–3 scale) per barrier:

| Cost Factor           | B1  | B2  | B3  | B4  | B5  | B6  | B7  | B8  | B9  | B10 | B11 | B12 | B13 | B14 | B15 |
| --------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Aftermarket/Warranty  | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 2   | 0   | 0   | 0   | 0   | 0   |
| Depreciation          | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1   | 0   | 0   | 0   | 0   | 0   |
| Labour                | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 3   | 2   | 2   | 2   | 2   | 2   |
| Maintenance & Repair  | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 2   | 0   | 0   | 0   | 0   | 0   |
| Raw Materials         | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 2   | 0   | 0   | 0   | 0   | 0   |
| Rental/Lease          | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 1   | 0   | 0   | 0   | 0   | 0   |
| R&D                   | 2   | 1   | 1   | 2   | 2   | 1   | 1   | 1   | 1   | 3   | 1   | 2   | 1   | 1   | 1   |
| SG&A                  | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 2   | 3   | 1   | 1   | 1   | 1   | 1   |
| Utilities             | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 0   | 2   | 0   | 0   | 0   | 0   | 0   |
| EBIT                  | 2   | 1   | 1   | 1   | 2   | 1   | 1   | 1   | 3   | 3   | 2   | 3   | 2   | 2   | 2   |
| Financing/Interest    | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 3   | 2   | 2   | 2   | 2   | 2   | 1   |
| Tax & Compliance      | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 2   | 1   | 3   | 3   | 3   | 1   |
| Supply Chain          | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 2   | 3   | 2   | 2   | 2   | 2   | 2   |
| Tech Infrastructure   | 3   | 2   | 3   | 3   | 3   | 2   | 2   | 2   | 1   | 3   | 1   | 1   | 1   | 1   | 3   |
| Training & Skill Dev. | 3   | 2   | 3   | 3   | 3   | 2   | 2   | 2   | 1   | 3   | 1   | 1   | 1   | 1   | 3   |
| Regulatory Compliance | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 3   | 1   | 3   | 3   | 3   | 1   |
| Insurance             | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   |
| Marketing & CustAcq   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 3   | 1   | 1   | 1   | 1   | 1   |
| Env. & Social Resp.   | 2   | 1   | 2   | 2   | 2   | 1   | 1   | 1   | 1   | 2   | 1   | 1   | 1   | 1   | 1   |
| Quality Control       | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 3   | 1   | 1   | 1   | 1   | 1   |

> Weights are on a **0–3** relevance scale (0 = no link, 3 = strong link).

---

## KPI Factor Weight Matrix

The 17 KPI factors and their weights (0–3 scale) per barrier:

| KPI Factor                 | B1  | B2  | B3  | B4  | B5  | B6  | B7  | B8  | B9  | B10 | B11 | B12 | B13 | B14 | B15 |
| -------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Asset/Equipment Efficiency | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 2   | 3   | 2   | 1   | 1   | 1   | 1   |
| Utilities Efficiency       | 1   | 1   | 1   | 1   | 1   | 0   | 0   | 0   | 1   | 2   | 1   | 0   | 0   | 0   | 0   |
| Inventory Efficiency       | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 2   | 3   | 2   | 1   | 1   | 1   | 1   |
| Process Quality            | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 1   | 3   | 1   | 1   | 2   | 2   | 2   |
| Product Quality            | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 1   | 3   | 1   | 1   | 2   | 2   | 2   |
| Safety & Security          | 1   | 1   | 1   | 1   | 1   | 2   | 2   | 1   | 0   | 2   | 1   | 0   | 2   | 2   | 2   |
| Planning Effectiveness     | 2   | 2   | 2   | 2   | 2   | 1   | 1   | 2   | 1   | 3   | 2   | 1   | 1   | 1   | 1   |
| Time to Market             | 1   | 1   | 2   | 2   | 2   | 1   | 1   | 2   | 2   | 3   | 2   | 2   | 1   | 1   | 1   |
| Production Flexibility     | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 3   | 2   | 1   | 2   | 2   | 2   |
| Customer Satisfaction      | 1   | 1   | 1   | 1   | 1   | 2   | 2   | 1   | 1   | 3   | 1   | 1   | 2   | 2   | 2   |
| Supply Chain Efficiency    | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 1   | 2   | 3   | 3   | 2   | 1   | 1   | 1   |
| Market Share Growth        | 2   | 2   | 1   | 1   | 1   | 2   | 2   | 1   | 2   | 3   | 1   | 1   | 2   | 2   | 1   |
| Employee Productivity      | 3   | 3   | 3   | 3   | 3   | 1   | 1   | 2   | 2   | 3   | 2   | 1   | 1   | 1   | 1   |
| ROI                        | 2   | 2   | 2   | 2   | 2   | 3   | 2   | 2   | 3   | 3   | 2   | 3   | 3   | 3   | 2   |
| Financial Health           | 2   | 2   | 2   | 2   | 2   | 3   | 2   | 2   | 3   | 3   | 2   | 3   | 3   | 3   | 2   |
| Talent Retention           | 3   | 3   | 3   | 3   | 2   | 1   | 1   | 1   | 1   | 2   | 1   | 1   | 1   | 1   | 1   |
| Customer Retention         | 2   | 2   | 2   | 2   | 2   | 2   | 2   | 1   | 1   | 3   | 2   | 1   | 2   | 2   | 3   |

> Weights are on a **0–3** relevance scale.

---

## AI Report Generation

After all scores are computed, the system generates two AI-powered reports using the **OpenRouter API** (default model: `mistralai/mistral-7b-instruct`):

### Report 1 — Comprehensive Barrier Analysis

- Covers **all 15 barriers**
- Split into 4 parallel generation chunks to stay within token limits
- Includes: Executive Summary, per-barrier analysis, indicator observations, severity context, KPIs to watch

### Report 2 — Strategic Roadmap (Top 3 Barriers)

- Focuses on the **3 highest-ISRI-value barriers**
- Includes for each barrier:
  - Problem statement
  - Strategic approach
  - 3-phase implementation plan (0–3, 4–9, 10–18+ months)
  - KPIs & targets
  - Risk mitigation
  - Budget considerations
- Cross-barrier success factors and governance

Both reports are converted to PDF and delivered as a ZIP download.

---

## Tech Stack

| Component          | Technology                           |
| ------------------ | ------------------------------------ |
| **Frontend**       | Next.js (React)                      |
| **Backend**        | FastAPI (Python)                     |
| **AI Engine**      | OpenRouter API (Mistral 7B Instruct) |
| **Database**       | MongoDB                              |
| **PDF Generation** | Markdown → PDF pipeline              |
| **Validation**     | Pydantic                             |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (optional, for persistence)
- An [OpenRouter](https://openrouter.ai/) API key

### Backend Setup

```bash
cd backend

# Create environment file
cp .env.example .env
# Edit .env → set OPENROUTER_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py

# Start the server
python app.py
```

The API will be available at **http://localhost:8000**.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at **http://localhost:3000**.

---

## API Reference

| Method | Endpoint                               | Description                          |
| ------ | -------------------------------------- | ------------------------------------ |
| `GET`  | `/`                                    | Health check                         |
| `GET`  | `/health`                              | Detailed health check                |
| `POST` | `/generate_full_report`                | Full ISRI analysis → ZIP with 2 PDFs |
| `POST` | `/generate_report_async`               | Start async report generation        |
| `GET`  | `/status/{session_id}`                 | Poll async generation progress       |
| `GET`  | `/download/comprehensive/{session_id}` | Download barrier analysis PDF        |
| `GET`  | `/download/roadmap/{session_id}`       | Download strategic roadmap PDF       |
| `POST` | `/strategic_plan_from_pdfs`            | Generate plan from pre-existing PDFs |
| `GET`  | `/api/barrier-definitions`             | List all 15 barrier definitions      |

---

## Project Structure

```
impact-value/
├── README.md                       ← You are here
├── FORMULAS.md                     # Raw formula reference sheet
├── MIGRATION_GUIDE.md              # Migration from legacy code
├── calc-barrier-score.py           # Legacy standalone script
│
├── backend/
│   ├── app.py                      # FastAPI application entry
│   ├── requirements.txt
│   ├── verify_setup.py
│   ├── config/
│   │   └── settings.py             # Weights, API keys, AI params
│   ├── models/
│   │   └── input_models.py         # Pydantic input schemas
│   ├── services/
│   │   ├── barrier_service.py      # Layer 1: Barrier score formulas
│   │   ├── cost_service.py         # Layer 2: Cost factor impact
│   │   ├── kpi_service.py          # Layer 3: KPI factor impact
│   │   ├── isri_service.py         # Final ISRI + Top-N selection
│   │   ├── ai_service.py           # OpenRouter report generation
│   │   └── database_service.py     # MongoDB persistence
│   └── utils/
│       └── pdf_utils.py            # Markdown → PDF conversion
│
└── frontend/                       # Next.js application
    ├── app/                        # Next.js app router
    ├── components/                 # React components
    ├── hooks/                      # Custom hooks
    └── lib/                        # Utilities
```

---

## License

This project is proprietary. All rights reserved.
