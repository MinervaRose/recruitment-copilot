from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class MatchResult:
    overall_score: int
    technical_score: int
    experience_score: int
    education_score: int
    communication_score: int
    portfolio_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    partial_skills: List[str]
    signal_matches: Dict[str, List[str]]
    evidence_highlights: List[str]
    recommendation: str
    confidence: str


SKILL_ALIASES: Dict[str, List[str]] = {
    "Python": ["python", "pandas", "numpy", "streamlit", "jupyter", "google colab", "scikit-learn", "sklearn"],
    "SQL": ["sql", "postgresql", "mysql", "sqlite", "queries", "query", "database"],
    "Power BI": ["power bi", "powerbi", "dax"],
    "Tableau": ["tableau"],
    "Machine Learning": ["machine learning", "ml", "model training", "predictive model", "tensorflow", "pytorch", "scikit-learn", "sklearn"],
    "NLP": ["nlp", "natural language", "text classification", "language model"],
    "Generative AI": ["generative ai", "generative ia", "genai", "llm", "large language model", "openai", "claude", "prompt engineering", "langchain", "transformers", "ia générative", "intelligence artificielle générative"],
    "Cloud": ["aws", "azure", "gcp", "google cloud", "cloud"],
    "dbt": ["dbt"],
    "Snowflake": ["snowflake"],
    "Git": ["git", "github", "gitlab"],
    "Data Visualization": ["dashboard", "dashboards", "data visualization", "data visualisation", "visualization", "visualisation", "dataviz", "plotly", "matplotlib", "tableau", "power bi"],
    "Stakeholder Communication": [
        "stakeholder", "stakeholders", "non-technical", "non technical", "client", "clients",
        "presentation", "presented", "explained", "explain", "teaching", "teacher", "tutor", "tutoring",
        "mentor", "mentoring", "openclassrooms", "training", "trainer", "workshop", "students",
        "learners", "apprenants", "accompagnement", "accompagne", "youtube", "education",
        "educational", "course", "cours", "pédagog", "pedagog", "learning materials",
        "supports de cours", "vulgarisation", "consultant", "consultante", "communication"
    ],
    "Automation": ["automation", "automated", "workflow", "workflows", "process automation", "make", "zapier", "n8n", "airtable", "github actions", "scripts", "pipeline"],
}

SIGNAL_ALIASES: Dict[str, List[str]] = {
    "Communication / teaching evidence": [
        "stakeholder", "stakeholders", "non-technical", "non technical", "client", "clients", "presentation",
        "presented", "explained", "explain", "teaching", "teacher", "tutor", "tutoring", "mentor",
        "mentoring", "openclassrooms", "training", "trainer", "workshop", "students", "learners",
        "apprenants", "accompagnement", "accompagne", "youtube", "education", "educational",
        "course", "cours", "pédagog", "pedagog", "learning materials", "supports de cours",
        "vulgarisation", "consultant", "consultante", "communication", "formation", "formateur"
    ],
    "Portfolio / project evidence": [
        "github", "portfolio", "project", "projects", "projet", "projets", "dashboard", "dashboards", "notebook",
        "streamlit", "tableau", "power bi", "observatory", "prototype", "built", "developed",
        "created", "implemented", "deployed", "repository", "repo", "application", "app"
    ],
    "Certification / education evidence": [
        "certificate", "certification", "nanodegree", "msc", "master", "mba", "degree",
        "licence", "scholarship", "udacity", "course", "university", "université", "diploma", "diplôme"
    ],
    "Business / operational evidence": [
        "business", "operational", "process", "workflow", "automation", "reporting", "dashboard",
        "stakeholder", "client", "crm", "sales", "customer", "data analysis", "decision", "organisation",
        "organisation", "consultant", "consultante", "company", "entreprise", "kpi", "indicators", "indicateurs"
    ],
}

HIGHLIGHT_RULES: Dict[str, List[str]] = {
    "OpenClassrooms / mentoring experience": ["openclassrooms", "mentor", "mentoring", "apprenants"],
    "Teaching, training or educational content": ["teacher", "teaching", "training", "course", "cours", "youtube", "education", "pédagog", "pedagog"],
    "GitHub or portfolio evidence": ["github", "portfolio", "repository", "repo", "notebook", "projects", "projets"],
    "Dashboard / data visualization practice": ["dashboard", "tableau", "power bi", "plotly", "data visualization", "data visualisation"],
    "AI / machine learning background": ["artificial intelligence", "intelligence artificielle", "machine learning", "generative ai", "ia générative", "llm", "langchain"],
    "Business-facing data work": ["business", "client", "stakeholder", "reporting", "process", "kpi", "data analysis", "consultant", "consultante"],
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_required_skills(job_description: str) -> List[str]:
    job = normalize(job_description)
    required = []
    for skill, aliases in SKILL_ALIASES.items():
        if any(alias in job for alias in aliases):
            required.append(skill)
    return required


def find_signals(text: str, signal_aliases: Dict[str, List[str]]) -> Dict[str, List[str]]:
    text_lower = normalize(text)
    signals: Dict[str, List[str]] = {}
    for signal_name, aliases in signal_aliases.items():
        hits = []
        for alias in aliases:
            if alias in text_lower and alias not in hits:
                hits.append(alias)
        if hits:
            signals[signal_name] = hits
    return signals


def find_evidence_highlights(cv_text: str) -> List[str]:
    cv = normalize(cv_text)
    highlights = []
    for label, aliases in HIGHLIGHT_RULES.items():
        if any(alias in cv for alias in aliases):
            highlights.append(label)
    return highlights[:6]


def match_skills(cv_text: str, job_description: str) -> Tuple[List[str], List[str], List[str]]:
    cv = normalize(cv_text)
    required = extract_required_skills(job_description)
    if not required:
        required = ["Python", "SQL", "Data Visualization", "Stakeholder Communication"]

    matched, missing, partial = [], [], []
    for skill in required:
        aliases = SKILL_ALIASES[skill]
        hits = sum(1 for alias in aliases if alias in cv)
        if hits >= 1:
            matched.append(skill)
        else:
            if skill == "Cloud" and any(x in cv for x in ["deployment", "api", "server", "hosted"]):
                partial.append(skill)
            elif skill == "dbt" and any(x in cv for x in ["data pipeline", "etl", "elt", "data engineering"]):
                partial.append(skill)
            elif skill == "Snowflake" and any(x in cv for x in ["database", "warehouse", "sql"]):
                partial.append(skill)
            elif skill == "Automation" and any(x in cv for x in ["github actions", "pipeline", "workflow", "scripts"]):
                partial.append(skill)
            else:
                missing.append(skill)
    return matched, missing, partial


def score_from_signals(signal_matches: Dict[str, List[str]], signal_name: str, base: int = 45, points_per_hit: int = 10) -> int:
    hits = len(signal_matches.get(signal_name, []))
    return max(0, min(100, base + hits * points_per_hit))


def estimate_experience_score(cv_text: str, job_description: str) -> int:
    cv = normalize(cv_text)
    job = normalize(job_description)
    score = 55
    if any(term in cv for term in ["years", "ans", "experience", "expérience"]):
        score += 10
    if any(term in cv for term in ["project", "projet", "portfolio", "deployed", "built", "créé", "created", "developed", "implemented", "réalisé"]):
        score += 15
    if any(term in cv for term in ["client", "stakeholder", "business", "mentor", "teacher", "training", "tutor", "students", "learners", "apprenants", "consultant", "consultante"]):
        score += 10
    if any(term in job for term in ["senior", "lead", "manager"]) and not any(term in cv for term in ["senior", "lead", "manager"]):
        score -= 10
    return max(0, min(100, score))


def estimate_education_score(cv_text: str) -> int:
    cv = normalize(cv_text)
    score = 50
    if any(term in cv for term in ["master", "msc", "mba", "degree", "licence", "bachelor"]):
        score += 25
    if any(term in cv for term in ["certification", "certificate", "nanodegree", "scholarship", "udacity", "course"]):
        score += 15
    if any(term in cv for term in ["artificial intelligence", "intelligence artificielle", "data science", "computer science", "statistics"]):
        score += 10
    return max(0, min(100, score))


def calculate_match(cv_text: str, job_description: str) -> MatchResult:
    matched, missing, partial = match_skills(cv_text, job_description)
    signal_matches = find_signals(cv_text, SIGNAL_ALIASES)
    evidence_highlights = find_evidence_highlights(cv_text)

    total = len(matched) + len(missing) + len(partial)
    technical_score = int(round(((len(matched) + 0.5 * len(partial)) / total) * 100)) if total else 0
    experience_score = estimate_experience_score(cv_text, job_description)
    education_score = estimate_education_score(cv_text)
    communication_score = score_from_signals(signal_matches, "Communication / teaching evidence", base=35, points_per_hit=8)
    portfolio_score = score_from_signals(signal_matches, "Portfolio / project evidence", base=45, points_per_hit=8)

    overall = int(round(
        technical_score * 0.42
        + experience_score * 0.20
        + education_score * 0.13
        + communication_score * 0.13
        + portfolio_score * 0.12
    ))

    if overall >= 95:
        recommendation = "Exceptional match"
        confidence = "High"
    elif overall >= 85:
        recommendation = "Strong potential fit"
        confidence = "High"
    elif overall >= 70:
        recommendation = "Possible fit — interview recommended"
        confidence = "Medium"
    elif overall >= 50:
        recommendation = "Partial fit — manual review recommended"
        confidence = "Medium"
    else:
        recommendation = "Weak fit — verify manually"
        confidence = "Low"

    return MatchResult(
        overall_score=overall,
        technical_score=technical_score,
        experience_score=experience_score,
        education_score=education_score,
        communication_score=communication_score,
        portfolio_score=portfolio_score,
        matched_skills=matched,
        missing_skills=missing,
        partial_skills=partial,
        signal_matches=signal_matches,
        evidence_highlights=evidence_highlights,
        recommendation=recommendation,
        confidence=confidence,
    )
