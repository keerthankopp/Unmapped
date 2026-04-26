# UNMAPPED 🌍
### Closing the distance between real skills and economic opportunity in the age of AI

> **Hack-Nation × World Bank Youth Summit — Global AI Hackathon 2026**  
> Challenge 05 · Powered by The World Bank · In collaboration with MIT Club of Northern California and MIT Club of Germany

---

## 🚀 Live Deployment

| | URL |
|---|---|
| **Frontend** | https://unmapped-kztccg3tp-keerthanmooc-3639s-projects.vercel.app |
| **Backend API** | https://unmapped-theta.vercel.app |
| **API Docs** | https://unmapped-theta.vercel.app/docs |
| **Repository** | https://github.com/keerthankopp/Unmapped |

Both frontend and backend are deployed on **Vercel**. The backend runs FastAPI as a serverless Python function. The frontend is a static React/Vite build. All API calls from the frontend point to the deployed backend — no local setup required to use the live app.

---

## 🚀 Live Deployment

| | URL |
|---|---|
| **Frontend** | https://unmapped-kztccg3tp-keerthanmooc-3639s-projects.vercel.app |
| **Backend API** | https://unmapped-theta.vercel.app |
| **API Docs** | https://unmapped-theta.vercel.app/docs |
| **Repository** | https://github.com/keerthankopp/Unmapped |

Both frontend and backend are deployed on **Vercel**. The backend runs FastAPI as a serverless Python function. The frontend is a static React/Vite build. All API calls from the frontend point to the deployed backend — no local setup required to use the app.

---

## What is UNMAPPED?

Meet Amara. She is 22, lives outside Accra, holds a secondary school certificate. She speaks three languages, has been repairing phones since she was 17, and taught herself to code from YouTube on a shared mobile connection.

By any reasonable measure, Amara has skills. But no employer in her city knows she exists. No training program has assessed what she already knows. No labor market system has a record of her.

**To the formal economy, Amara is unmapped.**

UNMAPPED is an open, configurable skills infrastructure layer that closes the distance between a young informal worker's real skills and real economic opportunity — using live World Bank data, AI-powered occupation classification, and LMIC-calibrated automation risk scoring.

---

## Challenge Requirements — How We Address Them

The challenge requires building **at least two of three modules** as a country-agnostic infrastructure layer grounded in real economic data.

**We built all three.**

| Requirement | Status | How |
|---|---|---|
| Module 01: Skills Signal Engine | ✅ Built | Conversational AI intake → ISCO-08 classified portable profile |
| Module 02: AI Readiness & Displacement Risk Lens | ✅ Built | Frey-Osborne baseline + LMIC calibration using WDI infrastructure data |
| Module 03: Opportunity Matching & Econometric Dashboard | ✅ Built | Live World Bank WDI signals, dual youth/policymaker interface |
| Bonus: Skills Growth & Learning Pathways | ✅ Built | WDI-grounded course recommendations, mobile-first |
| Country-agnostic (zero code changes to switch country) | ✅ | Single `country_config.json` controls all parameters |
| At least 2 real econometric signals visible to user | ✅ | WDI signals labeled with source and year on every opportunity card |
| Profile portable and explainable to non-expert | ✅ | Plain English profile card + PDF export |
| Calibrated to LMICs, not just global averages | ✅ | LMIC discount applied to automation risk using informality + broadband data |
| Real data, not synthetic proxies | ✅ | All signals from live World Bank WDI API |

---

## The Three Structural Failures We Solve

```
BROKEN SIGNALS          →  Skills Signal Engine
Education credentials       Conversational intake maps informal
don't translate to          experience to ISCO-08 + portable
labor market signals.       human-readable profile.

AI DISRUPTION           →  Readiness & Risk Lens
WITHOUT READINESS           Frey-Osborne automation scores
Youth have no tools to      LMIC-calibrated for infrastructure
understand automation       context. Honest. No sugarcoating.
risk or navigate it.

NO MATCHING             →  Opportunity Dashboard + Grow Tab
INFRASTRUCTURE              Live WDI econometric signals.
Informal networks           Honest matches. Wage floors shown.
exclude the most            Free learning pathways. Mobile-first.
vulnerable youth.
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  country_config.json                     │
│   Controls: labor data · education taxonomy · language   │
│   automation calibration · opportunity types · currency  │
└──────────────────────┬──────────────────────────────────┘
                       │ injected at startup, zero code changes
          ┌────────────┼────────────┐
          │            │            │
    [Module 01]  [Module 02]  [Module 03]
    Skills       Readiness    Opportunity
    Signal       & Risk       Matching &
    Engine       Lens         Dashboard
          │            │            │
          └────────────┼────────────┘
                       │
                  [Grow Tab]
              Learning Pathways
              & Market Readiness
```

### Infrastructure, Not Just an App

The system is designed as a **protocol, not a product**. Any government, NGO, training provider, or employer can plug in their local data and run it without touching the codebase. Country parameters are inputs, not assumptions.

---

## Tech Stack

### Backend
| Layer | Technology | Why |
|---|---|---|
| API framework | FastAPI (Python) | Async-native, lightweight, easy to extend |
| AI / LLM | Anthropic Claude API (claude-sonnet-4-20250514) | Skills extraction, occupation classification, opportunity matching |
| Labor data | World Bank WDI REST API | Only fully open, no-auth API that passed live testing |
| Occupation taxonomy | Claude-mediated ISCO-08 classification | ESCO (403 blocked) and O*NET (login required) both failed live testing — Claude's ISCO-08 knowledge is used directly with explicit taxonomy citations |
| Automation risk | Frey-Osborne 2013 baseline + LMIC calibration | Applied via occupation classification, adjusted for informality and broadband penetration |
| Async execution | asyncio.gather + run_in_executor | Concurrent WDI fetches; Claude calls run in thread pool to avoid blocking event loop |
| Validation | Pydantic | Country config schema validation |
| HTTP client | httpx | Async HTTP with timeout handling |

### Frontend
| Layer | Technology | Why |
|---|---|---|
| Framework | React 18 + Vite | Fast dev iteration, small bundle |
| Styling | Tailwind CSS | Mobile-first utility classes, no bloat |
| Charts | Hand-written SVG | No charting library = tiny bundle, works on slow connections |
| State | React hooks (useState, useEffect) | No Redux overhead |
| PDF export | Browser window.print() | Zero dependency, works offline |
| Streaming | fetch with streaming response | Claude intake streams token by token |

---

## Live Data Pipeline

**One API. Eighteen indicators. Everything real.**

Only the World Bank WDI API passed unauthenticated live testing. All other candidate APIs were tested and rejected:

| API | Test Result | Decision |
|---|---|---|
| World Bank WDI | ✅ Returns JSON, no auth | **Used — primary data source** |
| ILOSTAT SDMX-JSON | ❌ Page not found | Dropped |
| ESCO API | ❌ 403 Forbidden | Dropped |
| O*NET Web Services | ❌ Requires signin | Dropped |
| Wittgenstein Centre | ❌ UI only, no API | Dropped |

### WDI Indicators Used

```
SL.UEM.1524.ZS   Youth Unemployment Rate (%)
NY.GDP.PCAP.CD   GDP per Capita (USD)
SL.AGR.EMPL.ZS   Employment in Agriculture (% of total)
SL.IND.EMPL.ZS   Employment in Industry (% of total)
SL.SRV.EMPL.ZS   Employment in Services (% of total)
SE.SEC.ENRR      Secondary School Enrollment (% gross)
SP.POP.1524.TO   Youth Population 15-24
SL.TLF.ACTI.1524.FE.ZS   Youth Labor Force Participation Female (%)
SL.TLF.ACTI.1524.MA.ZS   Youth Labor Force Participation Male (%)
SL.EMP.WORK.ZS   Wage & Salaried Workers (% of employed)
SL.EMP.SELF.ZS   Self-Employed Workers (% of employed)
SL.EMP.VULN.ZS   Vulnerable Employment (% of total)
NY.GDP.MKTP.KD.ZG   GDP Growth (% annual)
SI.POV.DDAY      Poverty Rate at $2.15/day
IT.CEL.SETS.P2   Mobile Subscriptions per 100 people
IT.NET.USER.ZS   Internet Users (% of population)
SE.PRM.CMPT.ZS   Primary School Completion Rate (%)
SE.ADT.LITR.ZS   Adult Literacy Rate (%)
```

Every value displayed to the user carries its source label and year. No exceptions.

---

## LMIC Automation Risk Calibration

The standard Frey-Osborne (2013) automation probabilities are derived from US occupational data. They systematically overestimate automation risk in LMIC contexts because:

- Task composition within occupations differs significantly in informal economies
- Digital infrastructure required for automation is less available
- High informality means tasks are less standardized and harder to automate at scale

UNMAPPED applies an explicit LMIC calibration:

```
adjusted_risk = frey_osborne_base − lmic_discount

lmic_discount = lmic_discount_base
              + infrastructure_weight × (1 − broadband_penetration)
              + informality_weight × informal_economy_share
```

All calibration parameters are in `country_config.json` — no hardcoding. A phone repair worker in Accra gets a different (lower) automation risk score than the same SOC code in Boston, with the calibration shown transparently in the UI.

---

## Supported Countries

8 countries across 4 regions — switchable in real time with zero code changes:

| Country | Region | WB ISO3 | Informal Economy |
|---|---|---|---|
| 🇬🇭 Ghana | West Africa | GHA | 80% |
| 🇳🇬 Nigeria | West Africa | NGA | 92% |
| 🇰🇪 Kenya | East Africa | KEN | 83% |
| 🇪🇹 Ethiopia | East Africa | ETH | 91% |
| 🇮🇳 India | South Asia | IND | 90% |
| 🇧🇩 Bangladesh | South Asia | BGD | 85% |
| 🇵🇰 Pakistan | South Asia | PAK | 73% |
| 🇵🇭 Philippines | Southeast Asia | PHL | 78% |

Switching from Ghana to Bangladesh during the demo requires one dropdown selection. All data, calibration, education taxonomy, currency labels, and UI strings reload automatically.

---

## The Four Tabs

### 01 Skills — Conversational Intake
- Claude streams a warm conversational intake, one question at a time
- Extracts: occupation, years of experience, education level, skills, languages, digital access
- Maps to ISCO-08 occupation code using Claude's taxonomy knowledge
- Generates a human-readable profile card the user can download as PDF
- Profile includes: plain English summary, key skills with explanations, honest gaps, ISCO code + SOC equivalent

### 02 Readiness — Automation Risk Lens
- Frey-Osborne base automation probability by occupation
- LMIC calibration applied using country config (informality share + broadband penetration)
- SVG gauge showing adjusted risk percentage, color-coded green/amber/red
- Durable skills vs. at-risk tasks clearly separated
- Calibration note shown transparently: "Risk adjusted for Ghana: 80% informal economy reduces automation feasibility"
- Data source labeled: "Frey & Osborne (2013), LMIC-calibrated"

### 03 Opportunities — Matching Dashboard
**Youth view:** 4 matched opportunities with two visible econometric signals each:
- Signal 1: Sector employment share from WDI (e.g. "Services employs 38% of Ghana's workforce · World Bank WDI 2023")
- Signal 2: GDP growth trajectory (e.g. "Economy growing at 2.3% annually · World Bank WDI 2023")
- Honest barrier stated for every opportunity
- One actionable next step per opportunity

**Policymaker view:** 9-card aggregate dashboard showing all live WDI signals with source labels, sector employment bar chart, youth unemployment trend line — all from live API calls.

### 04 Grow — Learning & Market Readiness
- 3 personalized skill tracks based on occupation + risk profile + country WDI signals
- Each track: why now (country-specific), time to basic proficiency, time to job-ready, courses
- Prioritizes free resources accessible on a smartphone with limited data
- Quick Win card: single most impactful action this week
- 12-Month Goal: honest, reachable career trajectory
- Avoid card: what training to skip given their context and automation risk
- All recommendations grounded in WDI internet/mobile penetration data for the country

---

## Project Structure

```
unmapped/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── intake/
│   │   │   │   ├── ConversationalIntake.jsx   # Streaming Claude chat UI
│   │   │   │   └── SkillsProfileCard.jsx      # Portable profile card + PDF export
│   │   │   ├── readiness/
│   │   │   │   ├── ReadinessCard.jsx           # SVG risk gauge + calibration note
│   │   │   │   └── AutomationRiskChart.jsx     # Task decomposition visualization
│   │   │   ├── opportunity/
│   │   │   │   ├── YouthDashboard.jsx          # 4 matches with econometric badges
│   │   │   │   └── PolicymakerDashboard.jsx    # 9-card aggregate WDI dashboard
│   │   │   ├── grow/
│   │   │   │   ├── GrowDashboard.jsx           # Learning pathways overview
│   │   │   │   ├── SkillTrackCard.jsx          # Per-track course recommendations
│   │   │   │   └── CourseCard.jsx              # Individual course with metadata
│   │   │   └── shared/
│   │   │       ├── CountrySelector.jsx         # 8-country dropdown with regions
│   │   │       └── EconSignalBadge.jsx         # Reusable signal badge with source
│   │   ├── config/                             # Country config JSON files
│   │   │   ├── ghana.json
│   │   │   ├── nigeria.json
│   │   │   ├── kenya.json
│   │   │   ├── ethiopia.json
│   │   │   ├── india.json
│   │   │   ├── bangladesh.json
│   │   │   ├── pakistan.json
│   │   │   └── philippines.json
│   │   ├── hooks/
│   │   │   ├── useSkillsProfile.js             # Intake state + streaming
│   │   │   ├── useAutomationRisk.js            # Risk assessment fetch
│   │   │   ├── useOpportunities.js             # Opportunity matching fetch
│   │   │   └── useGrowRecommendations.js       # Growth plan fetch
│   │   ├── App.jsx                             # Tab navigation + global state
│   │   └── main.jsx
│   └── package.json
│
├── backend/
│   ├── main.py                                 # FastAPI app + CORS
│   ├── routers/
│   │   ├── intake.py                           # /intake/chat, /intake/profile
│   │   ├── readiness.py                        # /readiness/assess
│   │   ├── opportunities.py                    # /opportunities/match, /policymaker
│   │   ├── grow.py                             # /grow/recommendations
│   │   └── config.py                           # /config/{country}
│   ├── services/
│   │   ├── claude_service.py                   # All Claude API calls
│   │   ├── occupation_service.py               # ISCO-08 classification via Claude
│   │   ├── wdi_service.py                      # World Bank WDI API (18 indicators)
│   │   └── automation_service.py               # Frey-Osborne + LMIC calibration
│   ├── config/
│   │   ├── country_config_schema.py            # Pydantic schema
│   │   └── [8 country JSON files]
│   └── requirements.txt
│
└── README.md
```

---

## Deployment

### Vercel (Live)

Both services are deployed on Vercel. No local setup needed to use the app — just open the frontend URL.

**Backend — FastAPI as serverless Python**

`/backend/vercel.json`:
```json
{
  "version": 2,
  "builds": [{ "src": "main.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "main.py" }]
}
```

Vercel environment variable (set in project settings, not committed to repo):
```
ANTHROPIC_API_KEY=your_key_here
```

**Frontend — React/Vite static build**

Vercel environment variable (set in project settings):
```
VITE_API_BASE=https://unmapped-theta.vercel.app
```

Vercel auto-detects Vite and runs `npm run build` on every push to `main`.

---

## Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key_here" > .env
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_BASE=http://localhost:8000" > .env
npm run dev
```

Open `http://localhost:5173`

---

## Design Principles

**Constraint-first design.** Every UI decision assumes a shared Android phone on a slow mobile connection. No charting libraries. Hand-written SVG charts. Minimal bundle size.

**Honest over optimistic.** Every opportunity card shows a barrier. Every automation risk score shows its calibration note. Every data point shows its source and year.

**Protocol, not product.** The config file is the architecture. Adding a new country takes 5 minutes and zero code changes.

**Real data or nothing.** If an API is blocked, we drop it and say so. No synthetic proxies. No invented wage figures.

---

## Limitations

In the spirit of the challenge brief: *"The best teams know exactly what they don't know."*

- **ILOSTAT wage data is unavailable** via their API (endpoint returns 404). Wage signals use WDI employment structure data as a proxy rather than direct wage floors.
- **Wittgenstein Centre projections** have no accessible API — their education trajectory data could not be integrated live. The readiness lens uses WDI school enrollment trends as a substitute.
- **Frey-Osborne scores** are US-derived and our LMIC calibration is a principled approximation, not ground truth. We show this caveat in the UI.
- **Occupation classification** is Claude-mediated against ISCO-08 — not a direct lookup against a live taxonomy database (both ESCO and O*NET blocked). We cite the taxonomy standard used on every profile.

---

## Data Sources

| Source | Used For | Access |
|---|---|---|
| World Bank WDI | All 18 econometric indicators | ✅ Live API, open |
| Frey & Osborne (2013) | Automation probability baseline | Applied via Claude classification |
| ISCO-08 (ILO) | Occupation taxonomy standard | Applied via Claude classification |
| ILO Task Framework | Task content indices (routine vs. non-routine) | Applied via Claude classification |

---

## Links

| Resource | URL |
|---|---|
| Live App | https://unmapped-kztccg3tp-keerthanmooc-3639s-projects.vercel.app |
| Backend API | https://unmapped-theta.vercel.app |
| API Docs (Swagger) | https://unmapped-theta.vercel.app/docs |
| GitHub Repository | https://github.com/keerthankopp/Unmapped |

---

*Built for the Hack-Nation × World Bank Youth Summit Global AI Hackathon 2026.*  
*"Protocol, not product."*