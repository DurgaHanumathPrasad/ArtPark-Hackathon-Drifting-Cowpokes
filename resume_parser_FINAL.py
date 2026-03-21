"""
RESUME PARSER — PART 1
======================
INPUT  : A resume file (PDF or DOCX) + domain + role
OUTPUT : {
    domain            : str
    role              : str
    years_experience  : float
    cert_count        : int
    matched_core      : list   ← resume skills matched to CORE criteria
    matched_supporting: list   ← resume skills matched to SUPPORTING criteria
    matched_advanced  : list   ← resume skills matched to ADVANCED criteria
    unmatched         : list   ← resume skills that matched nothing
}
"""

import re
import os
import sys
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# FILE READER — PDF and DOCX
# ─────────────────────────────────────────────────────────────────────────────

def read_resume_file(file_path):
    """
    Reads a resume file and returns plain text string.

    Supports:
        .pdf  → reads using pdfplumber
        .docx → reads using python-docx
        .txt  → reads directly

    Parameters
    ----------
    file_path : str — full path to the uploaded resume file

    Returns
    -------
    str — plain text content of the resume
    """
    ext = os.path.splitext(file_path)[1].lower()

    # ── PDF ───────────────────────────────────────────────────────────────
    if ext == '.pdf':
        try:
            import pdfplumber
            text = ''
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
            return text.strip()
        except ImportError:
            raise ImportError(
                "pdfplumber not installed. Run: pip install pdfplumber"
            )

    # ── DOCX ──────────────────────────────────────────────────────────────
    elif ext == '.docx':
        try:
            from docx import Document
            doc  = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text.strip()
        except ImportError:
            raise ImportError(
                "python-docx not installed. Run: pip install python-docx"
            )

    # ── TXT ───────────────────────────────────────────────────────────────
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()

    else:
        raise ValueError(
            f"Unsupported file format: {ext}. Please upload PDF, DOCX or TXT."
        )


# ─────────────────────────────────────────────────────────────────────────────
# CRITERIA IMPORTS — all 24 domain files from criteria/ folder
# ─────────────────────────────────────────────────────────────────────────────

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'criteria'))

from ACCOUNTANT_skills_copyable           import ACCOUNTANT_CORE_SKILLS,           ACCOUNTANT_ROLE_SKILLS
from ADVOCATE_skills_copyable             import ADVOCATE_CORE_SKILLS,              ADVOCATE_ROLE_SKILLS
from AGRICULTURE_skills_copyable          import AGRICULTURE_CORE_SKILLS,           AGRICULTURE_ROLE_SKILLS
from APPAREL_skills_copyable              import APPAREL_CORE_SKILLS,               APPAREL_ROLE_SKILLS
from ARTS_skills_copyable                 import ARTS_CORE_SKILLS,                  ARTS_ROLE_SKILLS
from AUTOMOBILE_skills_copyable           import AUTOMOBILE_CORE_SKILLS,            AUTOMOBILE_ROLE_SKILLS
from AVIATION_skills_copyable             import AVIATION_CORE_SKILLS,              AVIATION_ROLE_SKILLS
from BANKING_skills_copyable              import BANKING_CORE_SKILLS,               BANKING_ROLE_SKILLS
from BPO_skills_copyable                  import BPO_CORE_SKILLS,                   BPO_ROLE_SKILLS
from BUSINESS_DEVELOPMENT_skills_copyable import BUSINESS_DEVELOPMENT_CORE_SKILLS,  BUSINESS_DEVELOPMENT_ROLE_SKILLS
from CHEF_skills_copyable                 import CHEF_CORE_SKILLS,                  CHEF_ROLE_SKILLS
from CONSTRUCTION_skills_copyable         import CONSTRUCTION_CORE_SKILLS,          CONSTRUCTION_ROLE_SKILLS
from CONSULTANT_skills_copyable           import CONSULTANT_CORE_SKILLS,            CONSULTANT_ROLE_SKILLS
from DESIGNER_skills_copyable             import DESIGNER_CORE_SKILLS,              DESIGNER_ROLE_SKILLS
from DIGITAL_MEDIA_skills_copyable        import DIGITAL_MEDIA_CORE_SKILLS,         DIGITAL_MEDIA_ROLE_SKILLS
from ENGINEERING_skills_copyable          import ENGINEERING_CORE_SKILLS,           ENGINEERING_ROLE_SKILLS
from FINANCE_skills_copyable              import FINANCE_CORE_SKILLS,               FINANCE_ROLE_SKILLS
from FITNESS_skills_copyable              import FITNESS_CORE_SKILLS,               FITNESS_ROLE_SKILLS
from HEALTHCARE_skills_copyable           import HEALTHCARE_CORE_SKILLS,            HEALTHCARE_ROLE_SKILLS
from HR_skills_copyable                   import HR_CORE_SKILLS,                    HR_ROLE_SKILLS
from INFORMATION_TECHNOLOGY_skills_copyable import INFORMATION_TECHNOLOGY_CORE_SKILLS, INFORMATION_TECHNOLOGY_ROLE_SKILLS
from PUBLIC_RELATIONS_skills_copyable     import PUBLIC_RELATIONS_CORE_SKILLS,      PUBLIC_RELATIONS_ROLE_SKILLS
from SALES_skills_copyable                import SALES_CORE_SKILLS,                 SALES_ROLE_SKILLS
from TEACHER_skills_copyable              import TEACHER_CORE_SKILLS,               TEACHER_ROLE_SKILLS


# ─────────────────────────────────────────────────────────────────────────────
# CRITERIA LOOKUP DICTIONARIES
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# AUTO-DETECT DOMAIN FROM RESUME TEXT
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN_KEYWORDS = {
    "ACCOUNTANT":             ["accountant","accounting","cpa","gaap","ledger","bookkeeping","audit","tax","ifrs","reconciliation"],
    "ADVOCATE":               ["advocate","social work","case manager","counselor","community","outreach","nonprofit","welfare"],
    "AGRICULTURE":            ["agriculture","farming","crop","soil","livestock","extension agent","horticulture","agri","harvest"],
    "APPAREL":                ["apparel","fashion","garment","merchandising","retail","clothing","textile","buyer","stylist"],
    "ARTS":                   ["artist","creative","arts","graphic","illustration","photography","music","design","animation"],
    "AUTOMOBILE":             ["automobile","automotive","vehicle","car","mechanic","dealership","insurance","claims","motor"],
    "AVIATION":               ["aviation","aircraft","pilot","airframe","faa","airline","flight","airport","aerospace","avionics"],
    "BANKING":                ["banking","bank","teller","loan","mortgage","credit","financial institution","branch","investment"],
    "BPO":                    ["bpo","call center","customer service","process","outsourcing","back office","helpdesk","crm"],
    "BUSINESS-DEVELOPMENT":   ["business development","bd","sales pipeline","lead generation","partnerships","revenue growth"],
    "CHEF":                   ["chef","cook","culinary","kitchen","restaurant","food service","pastry","sous chef","cuisine"],
    "CONSTRUCTION":           ["construction","contractor","site manager","superintendent","blueprint","building","civil","carpenter"],
    "CONSULTANT":             ["consultant","consulting","advisory","strategy","management consulting","client solutions"],
    "DESIGNER":               ["designer","ux","ui","graphic design","product design","figma","adobe","interior design","cad"],
    "DIGITAL-MEDIA":          ["digital media","social media","content","seo","digital marketing","blogger","media","online"],
    "ENGINEERING":            ["engineer","engineering","mechanical","electrical","civil","chemical","systems","design engineer"],
    "FINANCE":                ["finance","financial","fp&a","treasury","budget","forecast","cfo","controller","analyst"],
    "FITNESS":                ["fitness","personal trainer","gym","exercise","wellness","yoga","nutrition","coach","health"],
    "HEALTHCARE":             ["healthcare","medical","nurse","doctor","clinical","hospital","patient","pharmacy","health"],
    "HR":                     ["human resources","hr","recruiter","talent","payroll","employee relations","hris","onboarding"],
    "INFORMATION-TECHNOLOGY": ["software","developer","programmer","it","network","database","cloud","devops","cybersecurity","python","java"],
    "PUBLIC-RELATIONS":       ["public relations","pr","communications","media relations","press","brand","marketing communications"],
    "SALES":                  ["sales","account executive","sales representative","territory","quota","crm","b2b","b2c"],
    "TEACHER":                ["teacher","educator","instructor","curriculum","classroom","school","lesson plan","student"],
}

def detect_domain(resume_text):
    """
    Auto-detects the domain from resume text by keyword matching.
    Returns the domain with the most keyword hits.
    """
    text_lower = resume_text.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "INFORMATION-TECHNOLOGY"


def detect_role(resume_text, domain):
    """
    Auto-detects the role from resume text using the same
    extraction logic as the original dataset processing.
    Then fuzzy-matches it against known roles in the domain.
    """
    text = str(resume_text).strip()
    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text).strip()
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()

    stop = (r'(?:Summary|Skill Highlights|Professional Summary|Professional Profile|'
            r'Career Overview|Career Focus|Executive Profile|Experience|Highlights|'
            r'Objective|Profile|Qualifications|Core Competencies|Areas of Expertise|'
            r'Accomplishments|Work History|Special Hiring)')

    m = re.match(r'^(.+?)\s+' + stop, text_clean, re.IGNORECASE)
    if not m:
        for kw in ['Skills', 'Education', 'Background']:
            m = re.match(rf'^(.+?)\s+{kw}\b', text_clean, re.IGNORECASE)
            if m:
                break

    if m:
        raw_role = m.group(1).strip()
    else:
        raw_role = text_clean[:80].rsplit(' ', 1)[0].strip()

    raw_role = re.sub(r'\s+', ' ', raw_role).upper().strip()
    raw_role = re.sub(r'^[A-Z]\s+(?=[A-Z])', '', raw_role).strip()
    words    = raw_role.split()
    extracted = ' '.join(words[:8]) if len(words) > 8 else raw_role

    # Now fuzzy match against known roles in domain
    role_dict = DOMAIN_ROLE.get(domain, {})
    known_roles = list(role_dict.keys())

    if not known_roles:
        return extracted

    best_role  = extracted
    best_score = 0
    for known in known_roles:
        score = max(
            _levenshtein_ratio(_normalise(extracted), _normalise(known)),
            _partial_ratio(_normalise(extracted), _normalise(known)),
            _token_set_ratio(_normalise(extracted), _normalise(known)),
        )
        if score > best_score:
            best_score = score
            best_role  = known

    # If no good match found, return extracted role as-is
    return best_role if best_score >= 60 else extracted


DOMAIN_CORE = {
    "ACCOUNTANT":             ACCOUNTANT_CORE_SKILLS,
    "ADVOCATE":               ADVOCATE_CORE_SKILLS,
    "AGRICULTURE":            AGRICULTURE_CORE_SKILLS,
    "APPAREL":                APPAREL_CORE_SKILLS,
    "ARTS":                   ARTS_CORE_SKILLS,
    "AUTOMOBILE":             AUTOMOBILE_CORE_SKILLS,
    "AVIATION":               AVIATION_CORE_SKILLS,
    "BANKING":                BANKING_CORE_SKILLS,
    "BPO":                    BPO_CORE_SKILLS,
    "BUSINESS-DEVELOPMENT":   BUSINESS_DEVELOPMENT_CORE_SKILLS,
    "CHEF":                   CHEF_CORE_SKILLS,
    "CONSTRUCTION":           CONSTRUCTION_CORE_SKILLS,
    "CONSULTANT":             CONSULTANT_CORE_SKILLS,
    "DESIGNER":               DESIGNER_CORE_SKILLS,
    "DIGITAL-MEDIA":          DIGITAL_MEDIA_CORE_SKILLS,
    "ENGINEERING":            ENGINEERING_CORE_SKILLS,
    "FINANCE":                FINANCE_CORE_SKILLS,
    "FITNESS":                FITNESS_CORE_SKILLS,
    "HEALTHCARE":             HEALTHCARE_CORE_SKILLS,
    "HR":                     HR_CORE_SKILLS,
    "INFORMATION-TECHNOLOGY": INFORMATION_TECHNOLOGY_CORE_SKILLS,
    "PUBLIC-RELATIONS":       PUBLIC_RELATIONS_CORE_SKILLS,
    "SALES":                  SALES_CORE_SKILLS,
    "TEACHER":                TEACHER_CORE_SKILLS,
}

DOMAIN_ROLE = {
    "ACCOUNTANT":             ACCOUNTANT_ROLE_SKILLS,
    "ADVOCATE":               ADVOCATE_ROLE_SKILLS,
    "AGRICULTURE":            AGRICULTURE_ROLE_SKILLS,
    "APPAREL":                APPAREL_ROLE_SKILLS,
    "ARTS":                   ARTS_ROLE_SKILLS,
    "AUTOMOBILE":             AUTOMOBILE_ROLE_SKILLS,
    "AVIATION":               AVIATION_ROLE_SKILLS,
    "BANKING":                BANKING_ROLE_SKILLS,
    "BPO":                    BPO_ROLE_SKILLS,
    "BUSINESS-DEVELOPMENT":   BUSINESS_DEVELOPMENT_ROLE_SKILLS,
    "CHEF":                   CHEF_ROLE_SKILLS,
    "CONSTRUCTION":           CONSTRUCTION_ROLE_SKILLS,
    "CONSULTANT":             CONSULTANT_ROLE_SKILLS,
    "DESIGNER":               DESIGNER_ROLE_SKILLS,
    "DIGITAL-MEDIA":          DIGITAL_MEDIA_ROLE_SKILLS,
    "ENGINEERING":            ENGINEERING_ROLE_SKILLS,
    "FINANCE":                FINANCE_ROLE_SKILLS,
    "FITNESS":                FITNESS_ROLE_SKILLS,
    "HEALTHCARE":             HEALTHCARE_ROLE_SKILLS,
    "HR":                     HR_ROLE_SKILLS,
    "INFORMATION-TECHNOLOGY": INFORMATION_TECHNOLOGY_ROLE_SKILLS,
    "PUBLIC-RELATIONS":       PUBLIC_RELATIONS_ROLE_SKILLS,
    "SALES":                  SALES_ROLE_SKILLS,
    "TEACHER":                TEACHER_ROLE_SKILLS,
}


# ─────────────────────────────────────────────────────────────────────────────
# SYNONYM MAP
# ─────────────────────────────────────────────────────────────────────────────

SYNONYMS = {
    "microsoft excel":                         "ms excel",
    "microsoft word":                          "ms word",
    "microsoft office":                        "ms office",
    "microsoft powerpoint":                    "ms powerpoint",
    "structured query language":               "sql",
    "human resources":                         "hr",
    "artificial intelligence":                 "ai",
    "machine learning":                        "ml",
    "natural language processing":             "nlp",
    "customer relationship management":        "crm",
    "enterprise resource planning":            "erp",
    "key performance indicator":               "kpi",
    "project management professional":         "pmp",
    "certified public accountant":             "cpa",
    "generally accepted accounting principles":"gaap",
    "international financial reporting standards": "ifrs",
    "search engine optimisation":              "seo",
    "search engine optimization":              "seo",
    "search engine marketing":                 "sem",
    "occupational safety and health":          "osha",
    "health insurance portability and accountability": "hipaa",
    "agile scrum":                             "agile",
    "scrum agile":                             "agile",
}


# ─────────────────────────────────────────────────────────────────────────────
# PURE PYTHON STEMMER
# ─────────────────────────────────────────────────────────────────────────────

def _stem(word):
    w = word.lower()
    if len(w) <= 3:
        return w
    for sfx, rep in [('inging','ing'),('ating','ate'),('izing','ize'),
                     ('ising','ise'),('ing',''),('tion','te'),('sion','se'),
                     ('ations','ate'),('ments','ment'),('ities','ity'),
                     ('ies','y'),('ness',''),('ment',''),('ity',''),
                     ('ful',''),('ous',''),('ive',''),('ize',''),
                     ('ise',''),('ers',''),('ed',''),('ly',''),
                     ('er',''),('es',''),('s','')]:
        if w.endswith(sfx) and len(w) - len(sfx) > 2:
            w = w[:-len(sfx)] + rep
            break
    return w


def _normalise(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    for phrase, replacement in SYNONYMS.items():
        text = text.replace(phrase, replacement)
    words = [_stem(w) for w in text.split()]
    return ' '.join(words)


# ─────────────────────────────────────────────────────────────────────────────
# PURE PYTHON FUZZY MATCHING
# ─────────────────────────────────────────────────────────────────────────────

def _levenshtein_ratio(s1, s2):
    if not s1 and not s2: return 100.0
    if not s1 or not s2:  return 0.0
    l1, l2 = len(s1), len(s2)
    prev = list(range(l2 + 1))
    for i, c1 in enumerate(s1, 1):
        curr = [i]
        for j, c2 in enumerate(s2, 1):
            curr.append(min(prev[j]+1, curr[j-1]+1,
                            prev[j-1]+(0 if c1==c2 else 1)))
        prev = curr
    return round(100*(1 - prev[l2]/max(l1, l2)), 2)


def _partial_ratio(s1, s2):
    if not s1 or not s2: return 0.0
    short, long = (s1, s2) if len(s1) <= len(s2) else (s2, s1)
    ls, ll = len(short), len(long)
    best = 0.0
    for i in range(ll - ls + 1):
        score = _levenshtein_ratio(short, long[i:i+ls])
        if score > best:
            best = score
    return best


def _token_set_ratio(s1, s2):
    t1 = set(s1.split())
    t2 = set(s2.split())
    inter     = ' '.join(sorted(t1 & t2))
    only1     = ' '.join(sorted(t1 - t2))
    only2     = ' '.join(sorted(t2 - t1))
    s_inter_1 = (inter + ' ' + only1).strip()
    s_inter_2 = (inter + ' ' + only2).strip()
    return max(
        _levenshtein_ratio(inter, s_inter_1),
        _levenshtein_ratio(inter, s_inter_2),
        _levenshtein_ratio(s_inter_1, s_inter_2),
    )


def _is_match(resume_skill, criteria_skill, threshold=75):
    r = _normalise(resume_skill)
    c = _normalise(criteria_skill)
    if not r or not c:
        return False
    best = max(
        _levenshtein_ratio(r, c),
        _partial_ratio(r, c),
        _token_set_ratio(r, c),
    )
    return best >= threshold


# ─────────────────────────────────────────────────────────────────────────────
# EXPERIENCE EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

MONTH_MAP = {
    'jan':1,'feb':2,'mar':3,'apr':4,'may':5,'jun':6,
    'jul':7,'aug':8,'sep':9,'oct':10,'nov':11,'dec':12,
    'january':1,'february':2,'march':3,'april':4,'june':6,
    'july':7,'august':8,'september':9,'october':10,
    'november':11,'december':12,
}

DATE_PATTERN = re.compile(
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'
    r'|january|february|march|april|june|july|august'
    r'|september|october|november|december)'
    r'\s+(\d{4})\s+(?:to|-|–)\s+'
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'
    r'|january|february|march|april|june|july|august'
    r'|september|october|november|december|current|present)'
    r'\s*(\d{4})?',
    re.IGNORECASE
)

def _extract_experience(text):
    total_months = 0
    now = datetime.now()
    for sm, sy, em, ey in DATE_PATTERN.findall(text):
        try:
            start = datetime(int(sy), MONTH_MAP[sm.lower()], 1)
            end   = now if em.lower() in ('current','present') \
                    else datetime(int(ey), MONTH_MAP[em.lower()], 1)
            total_months += max(
                (end.year-start.year)*12 + (end.month-start.month), 0
            )
        except Exception:
            continue
    return round(total_months / 12, 1)


# ─────────────────────────────────────────────────────────────────────────────
# CERTIFICATION COUNTER
# ─────────────────────────────────────────────────────────────────────────────

CERT_KEYWORDS = re.compile(
    r'(?:certif|licens|certified|diploma|accredited|'
    r'credential|registered|chartered|awarded|qualified)',
    re.IGNORECASE
)

def _extract_certifications(text):
    cert_match = re.search(
        r'(?:Accomplishments|Certifications?|Licenses?|Credentials?)'
        r'(.*?)'
        r'(?:Experience|Education|Skills?|Work\s+History|$)',
        text, re.DOTALL | re.IGNORECASE
    )
    if cert_match:
        lines = [l.strip() for l in cert_match.group(1).split('\n') if l.strip()]
        return sum(1 for l in lines if CERT_KEYWORDS.search(l))
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# SKILL EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

def _extract_skills(text):
    sm = re.search(
        r'(?:Skill[s\s]*Highlights?|Core\s+Competencies|Key\s+Skills?|Skills?)'
        r'(.*?)'
        r'(?:Education|Certifications?|Experience|Accomplishments|Work\s+History|$)',
        text, re.DOTALL | re.IGNORECASE
    )
    raw    = sm.group(1) if sm else text
    tokens = re.split(r'[,\n•·|;\-–—]', raw)
    skills = []
    seen   = set()
    for t in tokens:
        t   = t.strip()
        t   = re.sub(r'[^a-zA-Z0-9\s\(\)/\+\#\.]', ' ', t)
        t   = re.sub(r'\s+', ' ', t).strip()
        key = t.lower()
        if 3 <= len(t) <= 60 and not t.isdigit() and key not in seen:
            skills.append(t)
            seen.add(key)
    return skills


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PARSE FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def parse_resume(resume_text, domain, role):
    """
    Reads ANY resume text and returns structured data ready for the scorer.

    Parameters
    ----------
    resume_text : str   — raw resume text
    domain      : str   — e.g. "FINANCE", "HR", "INFORMATION-TECHNOLOGY"
    role        : str   — e.g. "FINANCE MANAGER", "HR GENERALIST"

    Returns
    -------
    dict:
        domain             : str
        role               : str
        years_experience   : float
        cert_count         : int
        matched_core       : list
        matched_supporting : list
        matched_advanced   : list
        unmatched          : list
    """
    domain = domain.upper().strip()
    role   = role.upper().strip()

    resume_skills       = _extract_skills(resume_text)
    years_exp           = _extract_experience(resume_text)
    cert_count          = _extract_certifications(resume_text)

    core_criteria       = DOMAIN_CORE.get(domain, [])
    role_skills_dict    = DOMAIN_ROLE.get(domain, {})
    role_criteria       = role_skills_dict.get(role, {})
    supporting_criteria = role_criteria.get('supporting', [])
    advanced_criteria   = role_criteria.get('advanced',   [])

    matched_core        = []
    matched_supporting  = []
    matched_advanced    = []
    unmatched           = []

    for skill in resume_skills:
        placed = False

        if not placed:
            for c in core_criteria:
                if _is_match(skill, c):
                    matched_core.append(skill)
                    placed = True
                    break

        if not placed:
            for c in supporting_criteria:
                if _is_match(skill, c):
                    matched_supporting.append(skill)
                    placed = True
                    break

        if not placed:
            for c in advanced_criteria:
                if _is_match(skill, c):
                    matched_advanced.append(skill)
                    placed = True
                    break

        if not placed:
            unmatched.append(skill)

    # ── Build structured output ────────────────────────────────────────────
    result = {

        # ── Basic Info ──────────────────────────────────────────────────
        'domain':           domain,
        'role':             role,
        'years_experience': years_exp,
        'cert_count':       cert_count,

        # ── Skills classified into 3 categories ─────────────────────────
        'core': {
            'matched':   matched_core,                        # skills found in resume that match CORE criteria
            'count':     len(matched_core),                   # how many matched
            'required':  core_criteria,                       # what was required
            'missing':   [c for c in core_criteria            # what was NOT found
                          if not any(_is_match(s, c) for s in resume_skills)],
        },

        'supporting': {
            'matched':   matched_supporting,                  # skills found in resume that match SUPPORTING
            'count':     len(matched_supporting),
            'required':  supporting_criteria,
            'missing':   [c for c in supporting_criteria
                          if not any(_is_match(s, c) for s in resume_skills)],
        },

        'advanced': {
            'matched':   matched_advanced,                    # skills found in resume that match ADVANCED
            'count':     len(matched_advanced),
            'required':  advanced_criteria,
            'missing':   [c for c in advanced_criteria
                          if not any(_is_match(s, c) for s in resume_skills)],
        },

        # ── Skills in resume that matched nothing in criteria ────────────
        'unmatched':    unmatched,
    }

    return result


# ─────────────────────────────────────────────────────────────────────────────
# PRINT OUTPUT — clearly shows all 3 categories
# ─────────────────────────────────────────────────────────────────────────────

def print_result(result):
    """
    Prints the parser output in a clean readable format.
    Shows all 3 skill categories separately.
    """
    print("=" * 60)
    print("  RESUME PARSER OUTPUT")
    print("=" * 60)
    print(f"  Domain           : {result['domain']}")
    print(f"  Role             : {result['role']}")
    print(f"  Years Experience : {result['years_experience']}")
    print(f"  Certifications   : {result['cert_count']}")
    print("=" * 60)

    print(f"\n  CORE SKILLS  (weight 3)")
    print(f"  ✅ Matched ({result['core']['count']}):")
    for s in result['core']['matched']:
        print(f"      • {s}")
    print(f"  ❌ Missing ({len(result['core']['missing'])}):")
    for s in result['core']['missing']:
        print(f"      • {s}")

    print(f"\n  SUPPORTING SKILLS  (weight 2)")
    print(f"  ✅ Matched ({result['supporting']['count']}):")
    for s in result['supporting']['matched']:
        print(f"      • {s}")
    print(f"  ❌ Missing ({len(result['supporting']['missing'])}):")
    for s in result['supporting']['missing']:
        print(f"      • {s}")

    print(f"\n  ADVANCED SKILLS  (weight 1)")
    print(f"  ✅ Matched ({result['advanced']['count']}):")
    for s in result['advanced']['matched']:
        print(f"      • {s}")
    print(f"  ❌ Missing ({len(result['advanced']['missing'])}):")
    for s in result['advanced']['missing']:
        print(f"      • {s}")

    print(f"\n  UNMATCHED SKILLS (not in any criteria)")
    for s in result['unmatched']:
        print(f"      • {s}")
    print("=" * 60)
    print("  ✅ Ready for SCORER")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# FULL PIPELINE — THIS IS WHAT app.py CALLS
# ─────────────────────────────────────────────────────────────────────────────

def process_resume_file(file_path):
    """
    Full pipeline entry point for app.py:
      1. Read file (PDF / DOCX / TXT) → plain text
      2. Auto-detect domain from resume text
      3. Auto-detect role from resume text
      4. Parse text → extract skills, years, certs
      5. Fuzzy match → classified into core / supporting / advanced
      6. Return structured result dict → goes to scorer

    Parameters
    ----------
    file_path : str — path to uploaded resume file

    Returns
    -------
    dict with keys:
        domain, role, years_experience, cert_count,
        core        → { matched, count, required, missing }
        supporting  → { matched, count, required, missing }
        advanced    → { matched, count, required, missing }
        unmatched   → list
    """
    resume_text = read_resume_file(file_path)
    domain      = detect_domain(resume_text)
    role        = detect_role(resume_text, domain)
    result      = parse_resume(resume_text, domain, role)
    return result
