"""
SCORER — PART 2
===============
INPUT  : result dict from resume_parser_FINAL.py

OUTPUT : {
    score          : float — weighted score 0.0 to 1.0
    experience     : str   — NOVICE / INTERMEDIATE / VETERAN
    certs          : str   — ideal or not ideal exposure

    matched_skills : {
        core        : list — matched core skills
        supporting  : list — matched supporting skills
        advanced    : list — matched advanced skills
    }

    missing_skills : {
        core        : list — missing core skills
        supporting  : list — missing supporting skills
        advanced    : list — missing advanced skills
    }

    breakdown : {
        core        : { matched, total, points, max }
        supporting  : { matched, total, points, max }
        advanced    : { matched, total, points, max }
        total_earned: int
        total_max   : int
    }
}

SCORING FORMULA:
    earned   = (core_matched × 3) + (supporting_matched × 2) + (advanced_matched × 1)
    max      = (core_total   × 3) + (supporting_total   × 2) + (advanced_total   × 1)
    score    = earned / max

EXPERIENCE LEVEL:
    years < 5          → NOVICE
    5 ≤ years ≤ 10     → INTERMEDIATE
    years > 10         → VETERAN

CERTIFICATION LEVEL:
    cert_count < 3     → Not an ideal amount of diverse exposure
    cert_count ≥ 3     → An ideal amount of diverse exposure
"""


# ─────────────────────────────────────────────────────────────────────────────
# WEIGHTS
# ─────────────────────────────────────────────────────────────────────────────

WEIGHT_CORE        = 3
WEIGHT_SUPPORTING  = 2
WEIGHT_ADVANCED    = 1


# ─────────────────────────────────────────────────────────────────────────────
# SCORE CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

def calculate_score(parsed):
    """
    Calculates weighted skill score.

    Formula:
        earned = (core_matched × 3) + (supporting_matched × 2) + (advanced_matched × 1)
        max    = (core_total   × 3) + (supporting_total   × 2) + (advanced_total   × 1)
        score  = earned / max

    Parameters
    ----------
    parsed : dict — output from resume_parser_FINAL.process_resume_file()

    Returns
    -------
    float — score between 0.0 and 1.0
    """

    # ── Matched counts ────────────────────────────────────────────────────
    core_matched       = parsed['core']['count']
    supporting_matched = parsed['supporting']['count']
    advanced_matched   = parsed['advanced']['count']

    # ── Total required counts ─────────────────────────────────────────────
    core_total         = len(parsed['core']['required'])
    supporting_total   = len(parsed['supporting']['required'])
    advanced_total     = len(parsed['advanced']['required'])

    # ── Earned points ─────────────────────────────────────────────────────
    earned = (
        (core_matched       * WEIGHT_CORE)       +
        (supporting_matched * WEIGHT_SUPPORTING) +
        (advanced_matched   * WEIGHT_ADVANCED)
    )

    # ── Maximum possible points ───────────────────────────────────────────
    max_possible = (
        (core_total       * WEIGHT_CORE)       +
        (supporting_total * WEIGHT_SUPPORTING) +
        (advanced_total   * WEIGHT_ADVANCED)
    )

    # ── Final score ───────────────────────────────────────────────────────
    score = round(earned / max_possible, 4) if max_possible > 0 else 0.0

    return score


# ─────────────────────────────────────────────────────────────────────────────
# EXPERIENCE LEVEL
# ─────────────────────────────────────────────────────────────────────────────

def calculate_experience_level(years):
    """
    Classifies years of experience.

    Parameters
    ----------
    years : float — years of experience from parser

    Returns
    -------
    str — NOVICE / INTERMEDIATE / VETERAN
    """
    if years < 5:
        return 'NOVICE'
    elif 5 <= years <= 10:
        return 'INTERMEDIATE'
    else:
        return 'VETERAN'


# ─────────────────────────────────────────────────────────────────────────────
# CERTIFICATION LEVEL
# ─────────────────────────────────────────────────────────────────────────────

def calculate_cert_level(cert_count):
    """
    Classifies certification count.

    Parameters
    ----------
    cert_count : int — number of certifications from parser

    Returns
    -------
    str — exposure label
    """
    if cert_count < 3:
        return 'Not an ideal amount of diverse exposure'
    else:
        return 'An ideal amount of diverse exposure'


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SCORER FUNCTION — THIS IS WHAT app.py CALLS
# ─────────────────────────────────────────────────────────────────────────────

def score_resume(parsed):
    """
    Full scoring pipeline.
    Takes parser output → returns complete score result.

    Parameters
    ----------
    parsed : dict — output from resume_parser_FINAL.process_resume_file()

    Returns
    -------
    dict:
        score          : float — weighted skill score (0.0 to 1.0)
        experience     : str   — NOVICE / INTERMEDIATE / VETERAN
        certs          : str   — exposure label
        matched_skills : dict  — matched skills in all 3 categories
        missing_skills : dict  — missing skills in all 3 categories
        breakdown      : dict  — detailed points breakdown
    """

    # ── 1. Calculate skill score ──────────────────────────────────────────
    score = calculate_score(parsed)

    # ── 2. Calculate experience level ────────────────────────────────────
    experience = calculate_experience_level(parsed['years_experience'])

    # ── 3. Calculate certification level ─────────────────────────────────
    certs = calculate_cert_level(parsed['cert_count'])

    # ── 4. Matched skills — pulled directly from parser output ───────────
    matched_skills = {
        'core':       parsed['core']['matched'],       # matched core skills
        'supporting': parsed['supporting']['matched'], # matched supporting skills
        'advanced':   parsed['advanced']['matched'],   # matched advanced skills
    }

    # ── 5. Missing skills — pulled directly from parser output ───────────
    missing_skills = {
        'core':       parsed['core']['missing'],       # missing core skills
        'supporting': parsed['supporting']['missing'], # missing supporting skills
        'advanced':   parsed['advanced']['missing'],   # missing advanced skills
    }

    # ── 6. Breakdown ─────────────────────────────────────────────────────
    core_matched       = parsed['core']['count']
    supporting_matched = parsed['supporting']['count']
    advanced_matched   = parsed['advanced']['count']
    core_total         = len(parsed['core']['required'])
    supporting_total   = len(parsed['supporting']['required'])
    advanced_total     = len(parsed['advanced']['required'])

    breakdown = {
        'core': {
            'matched': core_matched,
            'total':   core_total,
            'weight':  WEIGHT_CORE,
            'points':  core_matched       * WEIGHT_CORE,
            'max':     core_total         * WEIGHT_CORE,
        },
        'supporting': {
            'matched': supporting_matched,
            'total':   supporting_total,
            'weight':  WEIGHT_SUPPORTING,
            'points':  supporting_matched * WEIGHT_SUPPORTING,
            'max':     supporting_total   * WEIGHT_SUPPORTING,
        },
        'advanced': {
            'matched': advanced_matched,
            'total':   advanced_total,
            'weight':  WEIGHT_ADVANCED,
            'points':  advanced_matched   * WEIGHT_ADVANCED,
            'max':     advanced_total     * WEIGHT_ADVANCED,
        },
        'total_earned': (core_matched       * WEIGHT_CORE       +
                         supporting_matched * WEIGHT_SUPPORTING +
                         advanced_matched   * WEIGHT_ADVANCED),
        'total_max':    (core_total         * WEIGHT_CORE       +
                         supporting_total   * WEIGHT_SUPPORTING +
                         advanced_total     * WEIGHT_ADVANCED),
    }

    # ── 7. Final result ───────────────────────────────────────────────────
    result = {
        'score':          score,
        'experience':     experience,
        'certs':          certs,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'breakdown':      breakdown,
    }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# PRINT OUTPUT — clearly shows all outputs
# ─────────────────────────────────────────────────────────────────────────────

def print_score(result):
    """
    Prints scorer output in clean readable format.
    Shows score, experience, certs, matched skills and missing skills.
    """
    print("=" * 60)
    print("  SCORER OUTPUT")
    print("=" * 60)

    # ── Main 3 outputs ────────────────────────────────────────────────────
    print(f"\n  SCORE          : {result['score']}  ({round(result['score'] * 100, 1)}%)")
    print(f"  EXPERIENCE     : {result['experience']}")
    print(f"  CERTIFICATIONS : {result['certs']}")

    # ── Score breakdown ───────────────────────────────────────────────────
    print(f"\n  SCORE BREAKDOWN:")
    b = result['breakdown']
    print(f"    Core Skills       : {b['core']['matched']}/{b['core']['total']}"
          f"  →  {b['core']['points']} / {b['core']['max']} pts  (weight {WEIGHT_CORE})")
    print(f"    Supporting Skills : {b['supporting']['matched']}/{b['supporting']['total']}"
          f"  →  {b['supporting']['points']} / {b['supporting']['max']} pts  (weight {WEIGHT_SUPPORTING})")
    print(f"    Advanced Skills   : {b['advanced']['matched']}/{b['advanced']['total']}"
          f"  →  {b['advanced']['points']} / {b['advanced']['max']} pts  (weight {WEIGHT_ADVANCED})")
    print(f"    ──────────────────────────────────────────────")
    print(f"    TOTAL             : {b['total_earned']} / {b['total_max']} pts")

    # ── Matched skills ────────────────────────────────────────────────────
    print(f"\n  MATCHED SKILLS:")

    print(f"\n    ✅ Core Skills Matched ({len(result['matched_skills']['core'])}):")
    for s in result['matched_skills']['core']:
        print(f"        • {s}")

    print(f"\n    ✅ Supporting Skills Matched ({len(result['matched_skills']['supporting'])}):")
    for s in result['matched_skills']['supporting']:
        print(f"        • {s}")

    print(f"\n    ✅ Advanced Skills Matched ({len(result['matched_skills']['advanced'])}):")
    for s in result['matched_skills']['advanced']:
        print(f"        • {s}")

    # ── Missing skills ────────────────────────────────────────────────────
    print(f"\n  MISSING SKILLS:")

    print(f"\n    ❌ Core Skills Missing ({len(result['missing_skills']['core'])}):")
    for s in result['missing_skills']['core']:
        print(f"        • {s}")

    print(f"\n    ❌ Supporting Skills Missing ({len(result['missing_skills']['supporting'])}):")
    for s in result['missing_skills']['supporting']:
        print(f"        • {s}")

    print(f"\n    ❌ Advanced Skills Missing ({len(result['missing_skills']['advanced'])}):")
    for s in result['missing_skills']['advanced']:
        print(f"        • {s}")

    print("=" * 60)
    print("  ✅ Ready for OUTPUT.py")
    print("=" * 60)
