# AI-Adaptive Onboarding Engine
## Technical Documentation

**ARTPARK CodeForge Hackathon Submission**
*Resume Skill Gap Analyser & Personalised Career Pathway Generator*

**March 2026**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Solution Overview](#2-problem-statement--solution-overview)
3. [System Architecture & Workflow](#3-system-architecture--workflow)
4. [Dataset & Criteria Design](#4-dataset--criteria-design)
5. [Resume Parsing Module](#5-resume-parsing-module)
6. [Skill Matching Engine — Fuzzy Logic](#6-skill-matching-engine--fuzzy-logic)
7. [Scoring Module](#7-scoring-module)
8. [LLM Integration — SWOT & Roadmap](#8-llm-integration--swot--roadmap)
9. [Frontend Application](#9-frontend-application)
10. [Tech Stack & Dependencies](#10-tech-stack--dependencies)
11. [Evaluation Criteria Alignment](#11-evaluation-criteria-alignment)
12. [Setup Instructions & File Structure](#12-setup-instructions--file-structure)

---

## 1. Executive Summary

The **AI-Adaptive Onboarding Engine** is a full-stack intelligent resume analysis system built for the ARTPARK CodeForge Hackathon. It addresses the critical problem of static, one-size-fits-all corporate onboarding by dynamically parsing a candidate's resume and generating a personalised skill gap analysis, competency score, SWOT analysis, and career roadmap — all tailored to the specific domain and role detected automatically from the resume.

### Key Highlights

| Metric | Value |
|---|---|
| Domains Covered | 24 |
| Unique Roles | 1,761 |
| Total Skill Entries | 22,893 |
| Average Skills per Role | 13.0 |
| Fallback Roles | 0 — every role explicitly defined |
| Data Sources | O*NET, BLS, Indeed, Glassdoor |
| LLM Model | google/gemma-3-4b-it:free via OpenRouter |
| Frontend | Streamlit (Python) |
| External Dependencies | Zero for matching — pure Python |

### Core Output

```
Score            : 0.73  (73%)
Experience Level : INTERMEDIATE
Certifications   : An ideal amount of diverse exposure
Matched Skills   : Core / Supporting / Advanced — separately listed
Missing Skills   : Core / Supporting / Advanced — with specific gaps
SWOT Analysis    : Strengths / Weaknesses / Opportunities / Threats
Career Roadmap   : Current Position → Stages → Goal
```

---

## 2. Problem Statement & Solution Overview

### The Problem

Corporate onboarding today is fundamentally broken. Static, one-size-fits-all curricula waste the time of experienced hires on content they already know, while simultaneously overwhelming beginners with advanced modules they are not ready for. The result is:

- Reduced efficiency and slower time-to-productivity
- Higher dropout rates during onboarding
- Missed identification of critical skill gaps
- No personalised learning pathway for new hires

### The Hackathon Challenge

> Build an AI-driven, adaptive learning engine that parses a new hire's current capabilities via resume and dynamically maps an optimised, personalised training pathway to reach role-specific competency.

### Our Solution

We built a **three-stage pipeline** that transforms any raw resume (PDF/DOCX/TXT) into a structured, scored, and actionable career analysis — fully automatically, with zero manual input from the user.

```
Stage 1 — PARSE
    Auto-detect domain and role from resume text
    Extract skills using regex + fuzzy NLP pipeline
    Calculate years of experience from date ranges
    Count certifications from resume sections

Stage 2 — SCORE
    Match extracted skills against 22,893-entry criteria database
    Classify into Core (×3), Supporting (×2), Advanced (×1)
    Calculate weighted competency score (0.0 to 1.0)
    Classify experience level and certification exposure

Stage 3 — ANALYSE
    Send all scored data to Google Gemma via OpenRouter
    Generate SWOT analysis grounded in actual skill data
    Generate personalised career roadmap with specific stages
```

### Why This Approach Works

- **No hallucinations in skill classification** — all criteria are explicitly defined from real sources
- **Fuzzy matching handles messy resumes** — typos, verb forms, gerunds, abbreviations all handled
- **Weighted scoring is transparent** — every point is traceable back to a specific skill
- **LLM used only for qualitative analysis** — never for factual skill matching, eliminating hallucination risk
- **Fully automatic** — user uploads resume, everything else is detected and computed

---

## 3. System Architecture & Workflow

### High-Level Architecture

```
USER uploads resume (PDF / DOCX / TXT)
            ↓
        app.py  (Streamlit frontend)
            ↓
resume_parser_FINAL.py
    ├── read_resume_file()          PDF/DOCX/TXT → plain text
    ├── detect_domain()             keyword scan → best matching domain
    ├── detect_role()               text extraction + fuzzy match → role
    ├── _extract_skills()           tokenise skill section
    ├── _extract_experience()       date ranges → total years
    ├── _extract_certifications()   cert keyword counting
    ├── _normalise() + _stem()      text preprocessing
    ├── _is_match()                 3-layer fuzzy matching
    └── parse_resume()              classify skills → Core/Supporting/Advanced
            ↓
scorer.py
    ├── calculate_score()           weighted formula → 0.0 to 1.0
    ├── calculate_experience_level() years → NOVICE/INTERMEDIATE/VETERAN
    └── calculate_cert_level()      count → ideal/not ideal
            ↓
output.py
    ├── build_prompt()              structure all data into LLM prompt
    ├── call_llm_api()              Google Gemma via OpenRouter
    └── parse_response()            extract SWOT + Roadmap from JSON
            ↓
app.py renders full results to user
```

### Data Flow

| Component | Input | Output |
|---|---|---|
| `resume_parser_FINAL.py` | File path | Parsed dict: `{core, supporting, advanced, missing, years, certs}` |
| `scorer.py` | Parsed dict | Score dict: `{score, experience, certs, matched_skills, missing_skills, breakdown}` |
| `output.py` | Score dict | Final dict: `{score, experience, certs, swot, roadmap}` |
| `app.py` | Final dict | Rendered Streamlit UI |

### Module Connections in app.py

```python
from resume_parser_FINAL import process_resume_file
from scorer              import score_resume
from output              import generate_output

# Three function calls — that is the entire backend
parsed = process_resume_file(file_path)   # auto-detects domain + role
scored = score_resume(parsed)
final  = generate_output(scored)
```

---

## 4. Dataset & Criteria Design

### Data Sources

| Source | Role in Project |
|---|---|
| **O*NET** (onetonline.org) | Primary source — occupational skills, knowledge, and abilities. Codes: 11-3031.00, 13-2011.00, 27-3031.00, 49-3011.00 and 20+ more |
| **BLS** (Bureau of Labor Statistics) | Secondary verification — employment outlook and skill requirements |
| **Indeed / Glassdoor** | Real-world job posting validation — confirmed skills match hiring requirements |
| **Kaggle Resume Dataset** | 2,484 resumes across 24 domains — used for role extraction and system validation |

### Criteria Structure

For each of the 24 domains:

```python
# Domain-level — same for ALL roles in domain
DOMAIN_CORE_SKILLS = [
    "Financial analysis",      # weight × 3
    "Budgeting",
    "Forecasting",
    "MS Excel",
    "Regulatory compliance",
]

# Role-specific — different for each of the 1,761 roles
DOMAIN_ROLE_SKILLS = {
    "FINANCE MANAGER": {
        "supporting": [        # weight × 2
            "Financial reporting oversight",
            "Budget & forecast management",
            "Team leadership",
            "Internal controls",
            "Audit & compliance management",
        ],
        "advanced": [          # weight × 1
            "Strategic financial planning",
            "ERP systems management",
            "Finance transformation",
        ],
    },
    # ... all 1,761 roles
}
```

### Scale

```
24  domains
1,761  unique roles — all explicitly defined, zero fallbacks
22,893  total skill entries
5  core skills per domain
5  supporting skills per role
3  advanced skills per role
```

### Three-Tier Classification Rationale

| Tier | Weight | Rationale |
|---|---|---|
| Core | ×3 | Foundational domain skills — non-negotiable, same for all roles |
| Supporting | ×2 | Role-specific required skills — directly needed for the job |
| Advanced | ×1 | Specialisation and growth path — differentiate exceptional candidates |

---

## 5. Resume Parsing Module

### File Reading

```python
def read_resume_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            text = ''.join(page.extract_text() for page in pdf.pages)

    elif ext == '.docx':
        from docx import Document
        doc  = Document(file_path)
        text = '\n'.join(para.text for para in doc.paragraphs)

    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

    return text.strip()
```

### Auto-Detection — Domain

```python
def detect_domain(resume_text):
    """
    Scans resume text for domain-specific keywords.
    Returns the domain with the most keyword matches.
    """
    DOMAIN_KEYWORDS = {
        "FINANCE":   ["finance", "financial", "budget", "cfo", "controller"],
        "HR":        ["human resources", "hr", "recruiter", "payroll"],
        "HEALTHCARE":["healthcare", "medical", "nurse", "clinical"],
        # ... all 24 domains
    }
    text_lower = resume_text.lower()
    scores = {d: sum(1 for kw in kws if kw in text_lower)
              for d, kws in DOMAIN_KEYWORDS.items()}
    return max(scores, key=scores.get)
```

### Auto-Detection — Role

```python
def detect_role(resume_text, domain):
    """
    Extracts role title from text before first section header.
    Fuzzy-matches against all known roles in the detected domain.
    """
    # Extract raw role from resume top
    role_split = re.split(r'\s+(Summary|Skills|Experience|...)', text)
    raw_role   = role_split[0].upper().strip()

    # Fuzzy match against known roles in domain
    best_role, best_score = raw_role, 0
    for known_role in DOMAIN_ROLE[domain].keys():
        score = max(levenshtein_ratio, partial_ratio, token_set_ratio)
        if score > best_score:
            best_role, best_score = known_role, score

    return best_role if best_score >= 60 else raw_role
```

### Skill Extraction

```
1. Find Skills / Skill Highlights / Core Competencies section
2. Split on delimiters: comma, newline, bullet •, pipe |, semicolon, dash
3. Clean each token: strip punctuation, collapse whitespace
4. Filter: keep tokens 3–60 chars, not purely numeric
5. Deduplicate while preserving order
```

### Experience Extraction

```
Pattern: "January 2018 to March 2022"
         "Feb 2019 - Present"
         "Mar 2015 – Current"

Process:
  1. Find all date ranges in full text
  2. Convert month names to numbers
  3. Calculate months between start and end
  4. Sum all ranges → total months → divide by 12
```

### Certification Extraction

```
Search for: Certifications / Accomplishments / Licenses section
Count lines containing: certif, licens, certified, diploma,
                         accredited, credential, registered,
                         chartered, awarded, qualified
```

---

## 6. Skill Matching Engine — Fuzzy Logic

### The Problem It Solves

The same skill appears in dozens of different forms in real resumes:

| Resume says | Criteria has | Problem |
|---|---|---|
| `"reported financials"` | `"Financial reporting"` | Verb form / gerund |
| `"finance reportng"` | `"Financial reporting"` | Typo |
| `"advanced Microsoft Excel"` | `"MS Excel"` | Abbreviation + word order |
| `"managing large teams"` | `"Team management"` | Gerund flip |
| `"budgetting experience"` | `"Budgeting"` | Misspelling |

### Full Preprocessing Pipeline

```python
def _normalise(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)   # remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()

    # Apply synonym map BEFORE stemming
    for phrase, replacement in SYNONYMS.items():
        text = text.replace(phrase, replacement)
    # "microsoft excel" → "ms excel"
    # "human resources" → "hr"
    # "search engine optimization" → "seo"

    # Stem each word
    words = [_stem(w) for w in text.split()]
    # "reporting" → "report"
    # "managing"  → "manag"
    # "certified" → "certif"

    return ' '.join(words)
```

### Three-Layer Fuzzy Matching

```python
def _is_match(resume_skill, criteria_skill, threshold=75):

    r = _normalise(resume_skill)
    c = _normalise(criteria_skill)

    # Layer 1 — character-level similarity (catches typos)
    score1 = _levenshtein_ratio(r, c)

    # Layer 2 — slide shorter over longer (catches phrase-in-sentence)
    score2 = _partial_ratio(r, c)

    # Layer 3 — word-order independent (catches reordered words)
    score3 = _token_set_ratio(r, c)

    best = max(score1, score2, score3)
    return best >= threshold   # 75 = configurable threshold
```

### Classification Priority

```
For each resume skill:
    1. Check against Core criteria   → if match → matched_core   (weight 3)
    2. Check against Supporting      → if match → matched_supporting (weight 2)
    3. Check against Advanced        → if match → matched_advanced   (weight 1)
    4. No match anywhere             → unmatched

A skill is placed in the HIGHEST matching category only.
```

### Zero External Libraries

The entire fuzzy matching engine is implemented in pure Python using dynamic programming — no `rapidfuzz`, no `nltk`, no `sklearn`. This means zero additional installations beyond the standard library.

---

## 7. Scoring Module

### Weighted Scoring Formula

```
earned   = (core_matched × 3) + (supporting_matched × 2) + (advanced_matched × 1)
max      = (core_total   × 3) + (supporting_total   × 2) + (advanced_total   × 1)
score    = earned / max

Result: float between 0.0 and 1.0
```

### Experience Level Classification

| Years of Experience | Output |
|---|---|
| Less than 5 years | `NOVICE 🌱` |
| 5 to 10 years | `INTERMEDIATE ⚡` |
| More than 10 years | `VETERAN 🏆` |

### Certification Level Classification

| Certification Count | Output |
|---|---|
| Less than 3 | `Not an ideal amount of diverse exposure` |
| 3 or more | `An ideal amount of diverse exposure` |

### Sample Calculation

```
Domain: FINANCE  |  Role: FINANCE MANAGER

Core Skills       : 3 / 5 matched  →  3 × 3 =  9 pts  (max 15)
Supporting Skills : 2 / 5 matched  →  2 × 2 =  4 pts  (max 10)
Advanced Skills   : 1 / 3 matched  →  1 × 1 =  1 pt   (max  3)

Total Earned  : 14 pts
Total Maximum : 28 pts
Score         : 14 / 28 = 0.50  (50%)

Experience    : 6.5 years  →  INTERMEDIATE
Certifications: 2 found    →  Not an ideal amount of diverse exposure
```

### Full Output Dict

```python
{
    'score':          0.50,
    'experience':     'INTERMEDIATE',
    'certs':          'Not an ideal amount of diverse exposure',
    'matched_skills': {
        'core':       ['Financial analysis', 'Budgeting', 'MS Excel'],
        'supporting': ['Financial reporting', 'Team leadership'],
        'advanced':   ['Strategic financial planning'],
    },
    'missing_skills': {
        'core':       ['Forecasting', 'Regulatory compliance'],
        'supporting': ['Internal controls', 'Audit management', 'ERP systems'],
        'advanced':   ['Finance transformation'],
    },
    'breakdown': {
        'core':        {'matched': 3, 'total': 5, 'points': 9,  'max': 15},
        'supporting':  {'matched': 2, 'total': 5, 'points': 4,  'max': 10},
        'advanced':    {'matched': 1, 'total': 3, 'points': 1,  'max':  3},
        'total_earned': 14,
        'total_max':    28,
    },
}
```

---

## 8. LLM Integration — SWOT & Roadmap

### Model & Provider

| Property | Value |
|---|---|
| Model | `google/gemma-3-4b-it:free` |
| Provider | OpenRouter (https://openrouter.ai) |
| Cost | Free tier — no billing required |
| API Format | OpenAI-compatible REST API |
| Implementation | Pure Python `urllib` — no `requests` library needed |

### What the LLM Receives

The prompt includes all scored data — giving the model full context:

```
OVERALL SCORE        : 50%
EXPERIENCE LEVEL     : INTERMEDIATE
YEARS OF EXPERIENCE  : 6.5 years
CERTIFICATION COUNT  : 2
CERTIFICATION LEVEL  : Not an ideal amount of diverse exposure

SCORE BREAKDOWN:
  Core Skills       : 3 / 5 matched (weight 3)
  Supporting Skills : 2 / 5 matched (weight 2)
  Advanced Skills   : 1 / 3 matched (weight 1)

MATCHED SKILLS:
  Core       : Financial analysis, Budgeting, MS Excel
  Supporting : Financial reporting, Team leadership
  Advanced   : Strategic financial planning

MISSING SKILLS:
  Core       : Forecasting, Regulatory compliance
  Supporting : Internal controls, Audit management, ERP systems
  Advanced   : Finance transformation
```

### JSON Response Format

```json
{
  "strengths":     "paragraph about strengths",
  "weaknesses":    "paragraph about weaknesses",
  "opportunities": "paragraph about opportunities",
  "threats":       "paragraph about threats",
  "roadmap": {
    "current_position": "where the candidate stands now",
    "stages": [
      "Stage 1: Learn Forecasting and Regulatory compliance",
      "Stage 2: Build Internal controls expertise",
      "Stage 3: Get certified — target CPA or CFA",
      "Stage 4: Master ERP systems (SAP/Oracle)",
      "Stage 5: Lead Finance transformation initiative"
    ],
    "goal": "what full efficiency looks like for this role"
  }
}
```

### Hallucination Prevention

- LLM is **never used for skill matching or scoring** — only for qualitative analysis
- All factual data (skills, scores, gaps) is pre-computed before LLM sees it
- LLM receives explicit matched and missing skills — cannot fabricate skill presence
- JSON response format is enforced — reduces free-form hallucination risk
- If JSON parsing fails — graceful fallback, app does not crash

---

## 9. Frontend Application

### Technology

Streamlit — a Python-native web framework. No HTML, CSS, or JavaScript required. Entire UI defined in `app.py`.

### User Journey

```
1. User opens browser → localhost:8501
2. User uploads resume (PDF / DOCX / TXT)
3. User clicks ANALYZE RESUME
4. App auto-detects domain and role — shown to user
5. Full results rendered on same page
```

### Results Sections

| Section | What it Shows |
|---|---|
| Auto-Detected Info | Domain and role detected from resume |
| Overall Results | Score %, Experience Level, Certification Level — metric cards |
| Score Breakdown | Progress bars per category with points earned vs max |
| Skills Analysis | Matched (green) vs Missing (red) — side by side for all 3 categories |
| SWOT Analysis | Four colour-coded boxes — green, yellow, blue, red |
| Career Roadmap | Current position → numbered stages → final goal |

### No Manual Input Required

```
❌ No domain dropdown
❌ No role text input
❌ No manual selection of any kind

✅ User only uploads file
✅ Everything else is automatic
```

---

## 10. Tech Stack & Dependencies

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Pure Python 3.x |
| PDF Reading | pdfplumber |
| DOCX Reading | python-docx |
| Fuzzy Matching | Pure Python — Levenshtein, Partial Ratio, Token Set Ratio |
| Stemming | Pure Python Porter Stemmer |
| Synonym Handling | Python dict — 22 common abbreviation mappings |
| LLM | google/gemma-3-4b-it:free via OpenRouter |
| API Calls | Python `urllib` (standard library) |
| Data Storage | Python dicts and lists — no database |
| Criteria Source | O*NET, BLS, Indeed, Glassdoor |

### Install Commands

```bash
pip install streamlit pdfplumber python-docx
```

That is all. No heavy ML frameworks, no torch, no transformers, no sklearn.

---

## 11. Evaluation Criteria Alignment

| Criterion | Weight | How We Address It |
|---|---|---|
| **Technical Sophistication** | 20% | 3-layer fuzzy matching engine, weighted scoring formula, 22,893 explicit skill entries across 1,761 roles — all sourced from O*NET and BLS |
| **Grounding & Reliability** | 15% | Zero LLM hallucinations in skill matching — all criteria pre-defined. LLM only receives pre-computed data and generates qualitative text |
| **Reasoning Trace** | 10% | Full breakdown shown to user: matched/missing per category, points earned vs max, weighted formula transparent |
| **Product Impact** | 10% | Identifies exact missing skills per tier — directly maps to which training modules are needed and in what priority order |
| **User Experience** | 15% | Streamlit UI with colour-coded sections, progress bars, metric cards, auto-detection — clean and requires zero technical knowledge from user |
| **Cross-Domain Scalability** | 10% | 24 domains, 1,761 roles — from Software Engineer to Chef, Aviation Technician to Yoga Instructor |
| **Communication & Documentation** | 20% | This 12-page technical document + inline code documentation throughout all modules |

### Datasets Cited

| Dataset | URL | Usage |
|---|---|---|
| O*NET Database | https://www.onetcenter.org/db_releases.html | Primary skill criteria source |
| Kaggle Resume Dataset | https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset | Resume text for role extraction |
| BLS Occupational Outlook | https://www.bls.gov/ooh/ | Skill requirement verification |

### Models Cited

| Model | Provider | Usage |
|---|---|---|
| google/gemma-3-4b-it:free | Google via OpenRouter | SWOT analysis + career roadmap generation |

---

## 12. Setup Instructions & File Structure

### Project Structure

```
prototype/
│
├── app.py                              ← Streamlit app (entry point)
├── resume_parser_FINAL.py              ← Part 1: Parse + Auto-Detect + Fuzzy Match
├── scorer.py                           ← Part 2: Score + Classify
├── output.py                           ← Part 3: Gemma API SWOT + Roadmap
│
├── criteria/                           ← 24 domain skill files
│     ├── __init__.py                   ← empty — marks folder as Python package
│     ├── ACCOUNTANT_skills_copyable.py
│     ├── ADVOCATE_skills_copyable.py
│     ├── AGRICULTURE_skills_copyable.py
│     ├── APPAREL_skills_copyable.py
│     ├── ARTS_skills_copyable.py
│     ├── AUTOMOBILE_skills_copyable.py
│     ├── AVIATION_skills_copyable.py
│     ├── BANKING_skills_copyable.py
│     ├── BPO_skills_copyable.py
│     ├── BUSINESS_DEVELOPMENT_skills_copyable.py
│     ├── CHEF_skills_copyable.py
│     ├── CONSTRUCTION_skills_copyable.py
│     ├── CONSULTANT_skills_copyable.py
│     ├── DESIGNER_skills_copyable.py
│     ├── DIGITAL_MEDIA_skills_copyable.py
│     ├── ENGINEERING_skills_copyable.py
│     ├── FINANCE_skills_copyable.py
│     ├── FITNESS_skills_copyable.py
│     ├── HEALTHCARE_skills_copyable.py
│     ├── HR_skills_copyable.py
│     ├── INFORMATION_TECHNOLOGY_skills_copyable.py
│     ├── PUBLIC_RELATIONS_skills_copyable.py
│     ├── SALES_skills_copyable.py
│     └── TEACHER_skills_copyable.py
│
└── uploads/                            ← Temp storage for uploaded resumes
```

### Installation

```bash
# Step 1 — Install dependencies
pip install streamlit pdfplumber python-docx

# Step 2 — Navigate to project folder
cd prototype

# Step 3 — Run the app
streamlit run app.py
```

### App opens automatically at

```
http://localhost:8501
```

### API Key Setup

In `output.py`, line 1 after the docstring:

```python
API_KEY = "your-openrouter-api-key-here"
```

Get a free key at: https://openrouter.ai → Sign up → Keys → Create new key

### Logic Overview for README

1. **Skill Gap Analysis**: Resume text is parsed using regex + pure Python fuzzy matching (Levenshtein distance, partial ratio, token set ratio). Skills are classified into Core, Supporting, and Advanced tiers against a pre-built criteria database sourced from O*NET and BLS.

2. **Adaptive Scoring**: Weighted formula — Core × 3, Supporting × 2, Advanced × 1. Score = earned points / max possible points. Experience and certification levels provide additional context.

3. **Adaptive Pathing Algorithm**: Missing skills per tier are identified and passed to a free LLM (Google Gemma via OpenRouter). The LLM generates a staged career roadmap — starting from the candidate's current position and mapping specific skill acquisition stages toward full role competency.

---

*Documentation prepared for ARTPARK CodeForge Hackathon — March 2026*
*Sources: O\*NET (onetonline.org), BLS (bls.gov), Indeed, Glassdoor, Kaggle Resume Dataset*
