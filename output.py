"""
OUTPUT.PY — PART 3
==================
INPUT  : result dict from scorer.py

PROCESS:
    Sends all scorer output to LLaMA API (FREE)
    Model  : meta-llama/llama-3.3-70b-instruct:free
    Via    : OpenRouter (https://openrouter.ai)

    LLaMA analyses:
        → matched skills            (strengths)
        → missing skills            (weaknesses)
        → experience level          (NOVICE/INTERMEDIATE/VETERAN)
        → certification level       (ideal/not ideal)
        → score
        → years of experience
        → certification count

OUTPUT : {
    score          : float — weighted score 0.0 to 1.0
    experience     : str   — NOVICE / INTERMEDIATE / VETERAN
    certs          : str   — ideal or not ideal exposure
    matched_skills : dict  — matched skills in all 3 categories
    missing_skills : dict  — missing skills in all 3 categories
    swot           : {
        strengths      : str
        weaknesses     : str
        opportunities  : str
        threats        : str
    }
    roadmap        : {
        current_position : str  — where candidate stands right now
        stages           : list — list of stages to reach full efficiency
        goal             : str  — final goal description
    }
}

HOW TO GET FREE API KEY:
    1. Go to https://openrouter.ai
    2. Sign up for free
    3. Go to Keys section
    4. Create a new key
    5. Paste it below where it says API_KEY = "your-key-here"
"""

import json
import urllib.request
import urllib.error


# ─────────────────────────────────────────────────────────────────────────────
# ★ INSERT YOUR OPENROUTER API KEY HERE
# ─────────────────────────────────────────────────────────────────────────────

API_KEY = "enter your api key"


# ─────────────────────────────────────────────────────────────────────────────
# API SETTINGS — DO NOT CHANGE
# ─────────────────────────────────────────────────────────────────────────────

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL   = "google/gemma-3-4b-it:free"


# ─────────────────────────────────────────────────────────────────────────────
# BUILD PROMPT FROM SCORER OUTPUT
# ─────────────────────────────────────────────────────────────────────────────

def build_prompt(scored):
    """
    Builds the prompt sent to LLaMA API.
    Uses all outputs from scorer.py.

    Parameters
    ----------
    scored : dict — output from scorer.score_resume()

    Returns
    -------
    str — full prompt for LLaMA
    """

    # ── Pull all data from scorer output ──────────────────────────────────
    score      = round(scored['score'] * 100, 1)
    experience = scored['experience']
    certs      = scored['certs']

    core_matched       = scored['matched_skills']['core']
    supporting_matched = scored['matched_skills']['supporting']
    advanced_matched   = scored['matched_skills']['advanced']

    core_missing       = scored['missing_skills']['core']
    supporting_missing = scored['missing_skills']['supporting']
    advanced_missing   = scored['missing_skills']['advanced']

    breakdown          = scored['breakdown']

    years              = scored.get('years_experience', 0)
    cert_count         = scored.get('cert_count', 0)

    # ── Build prompt ──────────────────────────────────────────────────────
    prompt = f"""You are a professional career analyst and resume evaluator.

Analyse the following resume evaluation data and generate a SWOT analysis and a career roadmap.

RESUME EVALUATION DATA:

OVERALL SCORE        : {score}%
EXPERIENCE LEVEL     : {experience}
YEARS OF EXPERIENCE  : {years} years
CERTIFICATION COUNT  : {cert_count}
CERTIFICATION LEVEL  : {certs}

SCORE BREAKDOWN:
  Core Skills       : {breakdown['core']['matched']} / {breakdown['core']['total']} matched (weight 3)
  Supporting Skills : {breakdown['supporting']['matched']} / {breakdown['supporting']['total']} matched (weight 2)
  Advanced Skills   : {breakdown['advanced']['matched']} / {breakdown['advanced']['total']} matched (weight 1)
  Total Points      : {breakdown['total_earned']} / {breakdown['total_max']}

MATCHED SKILLS (skills found in resume):
  Core Skills Matched       : {', '.join(core_matched) if core_matched else 'None'}
  Supporting Skills Matched : {', '.join(supporting_matched) if supporting_matched else 'None'}
  Advanced Skills Matched   : {', '.join(advanced_matched) if advanced_matched else 'None'}

MISSING SKILLS (skills NOT found in resume):
  Core Skills Missing       : {', '.join(core_missing) if core_missing else 'None'}
  Supporting Skills Missing : {', '.join(supporting_missing) if supporting_missing else 'None'}
  Advanced Skills Missing   : {', '.join(advanced_missing) if advanced_missing else 'None'}

Based on the above data generate the following:

1. SWOT ANALYSIS using these rules:
   STRENGTHS     : based on matched skills, experience level, years of experience, certifications
   WEAKNESSES    : based on missing skills, low score areas, gaps in core skills
   OPPORTUNITIES : based on what skills can be learned to improve the score and advance career
   THREATS       : based on critical missing core skills required for the role

2. CAREER ROADMAP using these rules:
   CURRENT POSITION : describe where the candidate stands right now based on score, experience level, matched and missing skills
   STAGES           : list of clear actionable stages the candidate must pass through to become fully efficient in their role. Each stage should mention specific skills to learn or improve
   GOAL             : describe what full efficiency looks like for this candidate in their role

Return ONLY a JSON object in this exact format. No extra text. No markdown. No code blocks.

{{
  "strengths":     "write strengths here as a paragraph",
  "weaknesses":    "write weaknesses here as a paragraph",
  "opportunities": "write opportunities here as a paragraph",
  "threats":       "write threats here as a paragraph",
  "roadmap": {{
    "current_position": "describe current position here as a paragraph",
    "stages": [
      "Stage 1: ...",
      "Stage 2: ...",
      "Stage 3: ...",
      "Stage 4: ...",
      "Stage 5: ..."
    ],
    "goal": "describe the final goal here as a paragraph"
  }}
}}"""

    return prompt.strip()


# ─────────────────────────────────────────────────────────────────────────────
# CALL LLAMA API VIA OPENROUTER
# ─────────────────────────────────────────────────────────────────────────────

def call_llama_api(prompt):
    """
    Sends prompt to LLaMA 3.3 70B via OpenRouter and returns response.

    Parameters
    ----------
    prompt : str — built prompt from build_prompt()

    Returns
    -------
    str — raw text response from LLaMA
    """

    # ── Build request body ────────────────────────────────────────────────
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {
                "role":    "user",
                "content": prompt
            }
        ]
    }).encode('utf-8')

    # ── Build request headers ─────────────────────────────────────────────
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    # ── Send request ──────────────────────────────────────────────────────
    req = urllib.request.Request(
        url     = API_URL,
        data    = body,
        headers = headers,
        method  = "POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            raw  = response.read().decode('utf-8')
            data = json.loads(raw)
            return data['choices'][0]['message']['content']

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"API Error {e.code}: {error_body}")

    except urllib.error.URLError as e:
        raise Exception(f"Connection Error: {e.reason}")


# ─────────────────────────────────────────────────────────────────────────────
# PARSE RESPONSE FROM API
# ─────────────────────────────────────────────────────────────────────────────

def parse_response(api_response):
    """
    Parses JSON response from LLaMA into SWOT + roadmap dict.

    Parameters
    ----------
    api_response : str — raw text from LLaMA API

    Returns
    -------
    dict — { swot: {...}, roadmap: {...} }
    """
    try:
        # Clean response just in case LLaMA adds extra text
        cleaned = api_response.strip()
        cleaned = cleaned.replace('```json', '').replace('```', '').strip()

        # Find JSON object inside response
        start = cleaned.find('{')
        end   = cleaned.rfind('}') + 1
        if start != -1 and end != 0:
            cleaned = cleaned[start:end]

        data = json.loads(cleaned)

        swot = {
            'strengths':     data.get('strengths',     'Not available'),
            'weaknesses':    data.get('weaknesses',    'Not available'),
            'opportunities': data.get('opportunities', 'Not available'),
            'threats':       data.get('threats',       'Not available'),
        }

        roadmap_raw = data.get('roadmap', {})
        roadmap = {
            'current_position': roadmap_raw.get('current_position', 'Not available'),
            'stages':           roadmap_raw.get('stages',           []),
            'goal':             roadmap_raw.get('goal',             'Not available'),
        }

        return swot, roadmap

    except json.JSONDecodeError:
        swot = {
            'strengths':     api_response,
            'weaknesses':    'Could not parse response',
            'opportunities': 'Could not parse response',
            'threats':       'Could not parse response',
        }
        roadmap = {
            'current_position': 'Could not parse response',
            'stages':           [],
            'goal':             'Could not parse response',
        }
        return swot, roadmap


# ─────────────────────────────────────────────────────────────────────────────
# MAIN OUTPUT FUNCTION — THIS IS WHAT app.py CALLS
# ─────────────────────────────────────────────────────────────────────────────

def generate_output(scored):
    """
    Full output pipeline.
    Takes scorer output → calls LLaMA API → returns final result.

    Parameters
    ----------
    scored : dict — output from scorer.score_resume()

    Returns
    -------
    dict:
        score            : float — weighted skill score (0.0 to 1.0)
        experience       : str   — NOVICE / INTERMEDIATE / VETERAN
        certs            : str   — exposure label
        years_experience : float — years of experience
        cert_count       : int   — certification count
        matched_skills   : dict  — matched skills in all 3 categories
        missing_skills   : dict  — missing skills in all 3 categories
        swot             : dict  — strengths, weaknesses, opportunities, threats
        roadmap          : dict  — current position, stages, goal
    """

    # ── Step 1: Build prompt from scorer output ───────────────────────────
    prompt = build_prompt(scored)

    # ── Step 2: Call LLaMA API ────────────────────────────────────────────
    api_response = call_llama_api(prompt)

    # ── Step 3: Parse SWOT and roadmap from response ──────────────────────
    swot, roadmap = parse_response(api_response)

    # ── Step 4: Build final result ────────────────────────────────────────
    result = {
        'score':            scored['score'],
        'experience':       scored['experience'],
        'certs':            scored['certs'],
        'years_experience': scored.get('years_experience', 0),
        'cert_count':       scored.get('cert_count', 0),
        'matched_skills':   scored['matched_skills'],
        'missing_skills':   scored['missing_skills'],
        'swot':             swot,
        'roadmap':          roadmap,
    }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# PRINT OUTPUT — clearly shows final result
# ─────────────────────────────────────────────────────────────────────────────

def print_output(result):
    """
    Prints final output in clean readable format.
    """
    print("=" * 60)
    print("  FINAL OUTPUT")
    print("=" * 60)

    # ── Main outputs ──────────────────────────────────────────────────────
    print(f"\n  SCORE          : {result['score']}  ({round(result['score'] * 100, 1)}%)")
    print(f"  EXPERIENCE     : {result['experience']}  ({result['years_experience']} years)")
    print(f"  CERTIFICATIONS : {result['certs']}  ({result['cert_count']} certs)")

    # ── Matched skills ────────────────────────────────────────────────────
    print(f"\n  MATCHED SKILLS:")
    print(f"    ✅ Core       : {', '.join(result['matched_skills']['core']) if result['matched_skills']['core'] else 'None'}")
    print(f"    ✅ Supporting : {', '.join(result['matched_skills']['supporting']) if result['matched_skills']['supporting'] else 'None'}")
    print(f"    ✅ Advanced   : {', '.join(result['matched_skills']['advanced']) if result['matched_skills']['advanced'] else 'None'}")

    # ── Missing skills ────────────────────────────────────────────────────
    print(f"\n  MISSING SKILLS:")
    print(f"    ❌ Core       : {', '.join(result['missing_skills']['core']) if result['missing_skills']['core'] else 'None'}")
    print(f"    ❌ Supporting : {', '.join(result['missing_skills']['supporting']) if result['missing_skills']['supporting'] else 'None'}")
    print(f"    ❌ Advanced   : {', '.join(result['missing_skills']['advanced']) if result['missing_skills']['advanced'] else 'None'}")

    # ── SWOT ──────────────────────────────────────────────────────────────
    print(f"\n  SWOT ANALYSIS:")
    print(f"\n  💪 STRENGTHS:")
    print(f"     {result['swot']['strengths']}")
    print(f"\n  ⚠️  WEAKNESSES:")
    print(f"     {result['swot']['weaknesses']}")
    print(f"\n  🚀 OPPORTUNITIES:")
    print(f"     {result['swot']['opportunities']}")
    print(f"\n  🔴 THREATS:")
    print(f"     {result['swot']['threats']}")

    # ── Roadmap ───────────────────────────────────────────────────────────
    print(f"\n  CAREER ROADMAP:")
    print(f"\n  📍 CURRENT POSITION:")
    print(f"     {result['roadmap']['current_position']}")
    print(f"\n  🗺️  STAGES TO REACH GOAL:")
    for i, stage in enumerate(result['roadmap']['stages'], 1):
        print(f"     {stage}")
    print(f"\n  🏆 GOAL:")
    print(f"     {result['roadmap']['goal']}")

    print("=" * 60)
    print("  ✅ Ready for app.py")
    print("=" * 60)
