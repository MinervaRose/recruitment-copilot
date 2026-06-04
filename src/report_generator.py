from __future__ import annotations

from src.scoring import MatchResult


def _format_list(items: list[str], empty: str) -> str:
    return ", ".join(items) if items else empty


def _bullet_list(items: list[str], empty: str = "None") -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def _executive_summary(result: MatchResult, candidate_name: str) -> str:
    skills = _format_list(result.matched_skills[:5], "the target skill set")
    if result.overall_score >= 95:
        fit = "an exceptional match"
    elif result.overall_score >= 85:
        fit = "a strong potential fit"
    elif result.overall_score >= 70:
        fit = "a possible fit requiring targeted verification"
    else:
        fit = "a weak or uncertain fit requiring careful manual review"

    return (
        f"{candidate_name} appears to be {fit} for this role. "
        f"The strongest detected evidence relates to {skills}. "
        "The briefing below highlights detected strengths, gaps to verify, and interview questions for a human recruiter."
    )


def generate_briefing(result: MatchResult, candidate_name: str = "Candidate") -> str:
    strengths = _format_list(result.matched_skills, "No direct skill match detected")
    gaps = _format_list(result.missing_skills, "No major gaps detected")
    partial = _format_list(result.partial_skills, "None")
    highlights = _bullet_list(result.evidence_highlights, "No specific evidence highlights detected")

    signal_lines = "None"
    if result.signal_matches:
        signal_lines = "\n".join(
            f"- **{signal}**: {', '.join(keywords[:8])}"
            for signal, keywords in result.signal_matches.items()
        )

    return f"""# Recruiter Briefing — {candidate_name}

## Executive Summary
{_executive_summary(result, candidate_name)}

## Overall Recommendation
**{result.recommendation}**  
Overall match score: **{result.overall_score}%**  
Confidence: **{result.confidence}**

## Why This Score?
- **Technical fit ({result.technical_score}%)**: based on explicit overlap between required skills and CV evidence.
- **Experience fit ({result.experience_score}%)**: based on project, delivery, business and stakeholder signals.
- **Education fit ({result.education_score}%)**: based on degree, certification and formal learning signals.
- **Communication evidence ({result.communication_score}%)**: based on teaching, mentoring, training and non-technical explanation signals.
- **Portfolio evidence ({result.portfolio_score}%)**: based on project, GitHub, dashboard, notebook and prototype signals.

## Top Evidence Highlights
{highlights}

## Candidate Strengths
{strengths}

## Skills to Verify
{gaps}

## Partial / Adjacent Evidence
{partial}

## Additional Evidence Signals
{signal_lines}

## Suggested Interview Questions
1. Can the candidate describe a project where they used the strongest matched skill in a real business or operational context?
2. Can the candidate explain how they would handle one of the missing or weaker skill areas?
3. Can the candidate give an example of communicating technical findings to a non-technical stakeholder?
4. Can the candidate walk through a complete project from problem definition to delivery?
5. Which portfolio project best demonstrates the candidate's ability to create business value?

## Human Review Note
This briefing is designed to support human recruiters. It should not be used as an automated hiring decision.
"""
