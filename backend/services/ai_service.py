"""
AI service for generating reports using OpenRouter API
Supports multiple models including Mistral, GPT, Claude, Llama, etc.
"""
import httpx
import re
from typing import Dict, List
import datetime
import logging
from config.settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_MODEL,
    OPENROUTER_SITE_URL,
    OPENROUTER_SITE_NAME,
    AI_TEMPERATURE,
    AI_MAX_TOKENS,
    AI_TIMEOUT
)

logger = logging.getLogger(__name__)

# Maximum number of continuation retries when the response is truncated
MAX_CONTINUATION_RETRIES = 2
# Maximum retries for a chunk that fails validation (missing barriers)
MAX_CHUNK_RETRIES = 2


async def _call_openrouter(
    messages: List[Dict[str, str]],
    temperature: float = AI_TEMPERATURE,
    max_tokens: int = AI_MAX_TOKENS,
) -> Dict:
    """
    Low-level helper: send a chat completion request to OpenRouter and return
    the raw JSON response dict.  Raises on HTTP / network errors.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_SITE_NAME,
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=AI_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()


async def _generate_with_retry(
    prompt: str,
    temperature: float = AI_TEMPERATURE,
    max_tokens: int = AI_MAX_TOKENS,
    label: str = "chunk",
) -> str:
    """
    Generate a completion for *prompt*, automatically detecting output
    truncation (finish_reason == 'length') and issuing up to
    MAX_CONTINUATION_RETRIES follow-up requests to complete the text.

    Returns the full, concatenated text.
    """
    messages = [{"role": "user", "content": prompt}]
    accumulated_text = ""

    for attempt in range(1 + MAX_CONTINUATION_RETRIES):
        try:
            api_response = await _call_openrouter(
                messages, temperature=temperature, max_tokens=max_tokens
            )
        except Exception as e:
            logger.error("API call failed for %s (attempt %d): %s", label, attempt + 1, e)
            if accumulated_text:
                return accumulated_text  # Return what we have so far
            raise

        if not api_response or not api_response.get("choices"):
            logger.warning("OpenRouter returned no choices for %s", label)
            return accumulated_text or f"OpenRouter API did not return valid response for {label}."

        choice = api_response["choices"][0]
        chunk_text = choice.get("message", {}).get("content", "")
        finish_reason = choice.get("finish_reason", "stop")

        logger.info(
            "[%s] attempt=%d  finish_reason=%s  chunk_len=%d chars",
            label, attempt + 1, finish_reason, len(chunk_text),
        )

        accumulated_text += chunk_text

        if finish_reason != "length":
            # Response completed naturally — we're done.
            break

        # Response was truncated.  Ask the model to continue.
        logger.info(
            "Response truncated for %s (attempt %d/%d). Requesting continuation...",
            label, attempt + 1, 1 + MAX_CONTINUATION_RETRIES,
        )

        # Build a continuation conversation so the model knows where it
        # left off and continues from that exact point.
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": accumulated_text},
            {
                "role": "user",
                "content": (
                    "Your previous response was cut off. "
                    "Continue EXACTLY where you left off. "
                    "Do NOT repeat any content already provided. "
                    "Do NOT add any preamble — just continue the report."
                ),
            },
        ]
    else:
        logger.warning(
            "Response for %s still truncated after %d retries. "
            "Returning best-effort text.",
            label, MAX_CONTINUATION_RETRIES,
        )

    return accumulated_text


def _validate_barriers_present(text: str, barrier_numbers: List[int]) -> List[int]:
    """
    Check which of the expected barrier numbers are mentioned in the text.
    Returns a list of MISSING barrier numbers.
    """
    missing = []
    for num in barrier_numbers:
        # Look for patterns like "Barrier 4", "Barrier 4:", "### Barrier 4" etc.
        pattern = rf"[Bb]arrier\s+{num}\b"
        if not re.search(pattern, text):
            missing.append(num)
    return missing


# ---------------------------------------------------------------------------
# Comprehensive Barrier Analysis
# ---------------------------------------------------------------------------

async def generate_comprehensive_barrier_analysis(
    company_details: Dict,
    barrier_scores: Dict[str, Dict],
    impact_values: Dict[str, Dict]
) -> str:
    """
    Generate comprehensive AI-powered analysis for ALL 15 barriers in parts.
    Splits generation into 5 smaller chunks (3 barriers each) to stay within
    token limits, then stitches together.

    Args:
        company_details: Company information dictionary
        barrier_scores: Complete barrier scores from barrier_service
        impact_values: Impact values from isri_service

    Returns:
        Markdown-formatted comprehensive barrier analysis report
    """
    if not OPENROUTER_API_KEY:
        return "OpenRouter API key is not configured. Cannot generate report."

    current_time = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p IST")

    # Split barriers into 5 groups of 3 to stay well within token limits
    barrier_groups = [
        list(range(1, 4)),     # Barriers 1-3
        list(range(4, 7)),     # Barriers 4-6
        list(range(7, 10)),    # Barriers 7-9
        list(range(10, 13)),   # Barriers 10-12
        list(range(13, 16)),   # Barriers 13-15
    ]

    parts = []

    # Part 1: Executive Summary + First Group Analysis
    part1 = await _generate_analysis_part(
        company_details, barrier_scores, impact_values,
        barrier_groups[0], current_time, include_summary=True
    )
    parts.append(part1)

    # Parts 2-5: Remaining barrier groups
    for i, group in enumerate(barrier_groups[1:], 2):
        part = await _generate_analysis_part(
            company_details, barrier_scores, impact_values,
            group, current_time, include_summary=False
        )
        parts.append(part)

    # NOTE: comprehensive barrier analysis should NOT include strategic recommendations
    # Recommendations and action plans are produced only in the strategic roadmap.

    # Stitch all parts together
    full_report = "\n\n---\n\n".join(parts)
    return full_report


def _build_barrier_sections(
    barrier_numbers: List[int],
    barrier_scores: Dict[str, Dict],
) -> str:
    """Build the barrier data text block for a group of barriers."""
    sections = []
    for i in barrier_numbers:
        barrier_key = f"barrier{i}"
        barrier_data = barrier_scores[barrier_key]
        section = f"""
### Barrier {i}: {barrier_data['name']}

**Assessment:**
- Barrier Score (out of 10): {barrier_data['total']:.2f}
- Severity Level: {barrier_data['level']}

**Indicator Breakdown:**
"""
        for indicator_name, indicator_score in barrier_data['indicators'].items():
            section += f"- {indicator_name.replace('_', ' ').title()}: {indicator_score:.2f}\n"
        sections.append(section)
    return "\n".join(sections)


async def _generate_analysis_part(
    company_details: Dict,
    barrier_scores: Dict[str, Dict],
    impact_values: Dict[str, Dict],
    barrier_numbers: List[int],
    current_time: str,
    include_summary: bool = False
) -> str:
    """Generate analysis for a specific group of barriers, with validation and retry."""

    barrier_data_text = _build_barrier_sections(barrier_numbers, barrier_scores)
    barrier_names = ", ".join(
        f"Barrier {n}" for n in barrier_numbers
    )
    label = f"barriers {barrier_numbers[0]}-{barrier_numbers[-1]}"

    # The critical stop instruction that prevents the model from going beyond
    stop_instruction = (
        f"\n\nCRITICAL RULES:\n"
        f"1. You MUST produce a COMPLETE analysis for EVERY barrier listed: {barrier_names}.\n"
        f"2. Do NOT skip any barrier.\n"
        f"3. Do NOT start analysing any barrier outside the range {barrier_numbers[0]}-{barrier_numbers[-1]}.\n"
        f"4. STOP IMMEDIATELY after finishing Barrier {barrier_numbers[-1]}. Do NOT continue to other barriers.\n"
        f"5. Do NOT include any Impact Value figures or strategic recommendations.\n"
    )

    if include_summary:
        prompt = f"""
Report Generation Date and Time: {current_time}

You are an expert consultant specializing in Indian SME readiness for IoT adoption. Write in the same professional, structured style as the sample barrier_analysis_report.pdf, but a bit more detailed.

**Company Profile:**
- Company: {company_details.get('company_name', 'N/A')}
- Industry: {company_details.get('industry', 'N/A')}
- Employees: {company_details.get('num_employees', 'N/A')}
- Annual Revenue: ₹{company_details.get('annual_revenue', 'N/A')} Cr

**Deliver the following sections:**

## 1) Executive Summary (180-240 words)
- Overall IoT readiness and business context
- Top strengths and critical gaps
- Immediate priorities (no strategic action plans)

## 2) Detailed Barrier Analysis for ONLY Barriers {barrier_numbers[0]}-{barrier_numbers[-1]}
For EACH of the {len(barrier_numbers)} barriers below, produce this structure:
- Barrier Score (out of 10): state the value clearly
- What this barrier means for the company (2-3 sentences)
- Business impact and risks (2-3 bullets)
- Why the severity level matters (1-2 bullets)
- Indicator-driven observations (reference the scores provided)
- KPIs to watch (3-4 specific metrics)

**Barrier Data to use:**

{barrier_data_text}

**Tone and format:**
- Professional consulting tone, concise bullets
- Plain language (avoid jargon)
- Keep the section focused and practical
{stop_instruction}
"""
    else:
        prompt = f"""
Continue the IoT Readiness Analysis for {company_details.get('company_name', 'N/A')} in the same style as the sample barrier_analysis_report.pdf, slightly more detailed.

**Task:** Provide detailed analysis for ONLY Barriers {barrier_numbers[0]}-{barrier_numbers[-1]}.

For EACH of the {len(barrier_numbers)} barriers below, use this structure:
- Barrier Score (out of 10): state the value clearly
- What this barrier means for the company (2-3 sentences)
- Business impact and risks (2-3 bullets)
- Why the severity level matters (1-2 bullets)
- Indicator-driven observations (reference the scores provided)
- KPIs to watch (3-4 specific metrics)

**Barrier Data to use:**

{barrier_data_text}

**Tone and format:**
- Professional consulting tone, concise bullets
- Plain language (avoid jargon)
- Keep the section focused and practical
{stop_instruction}
"""

    # Try generating with validation — retry the entire chunk if barriers are missing
    for chunk_attempt in range(1 + MAX_CHUNK_RETRIES):
        try:
            result = await _generate_with_retry(prompt, label=label)
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error for %s: %s - %s", label, e.response.status_code, e.response.text)
            return f"OpenRouter API HTTP error (Part {label}): {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            logger.error("Request error for %s: %s", label, e)
            return f"OpenRouter API request error: {e}"
        except Exception as e:
            logger.error("Unexpected error for %s: %s", label, e)
            return f"Unexpected error: {e}"

        # Validate: check that every expected barrier is mentioned
        missing = _validate_barriers_present(result, barrier_numbers)

        if not missing:
            logger.info("✅ All barriers present for %s", label)
            return result

        logger.warning(
            "⚠️  Missing barriers %s in response for %s (attempt %d/%d). Retrying...",
            missing, label, chunk_attempt + 1, 1 + MAX_CHUNK_RETRIES,
        )

        if chunk_attempt < MAX_CHUNK_RETRIES:
            # On retry, make the prompt even more explicit about what's needed
            retry_names = ", ".join(f"Barrier {n}" for n in barrier_numbers)
            prompt = f"""
You are an expert IoT consultant. Analyse the following barriers for {company_details.get('company_name', 'N/A')}.

YOU MUST WRITE A COMPLETE ANALYSIS FOR EACH OF THESE BARRIERS: {retry_names}.
There are exactly {len(barrier_numbers)} barriers. Do not skip any.

For each barrier, provide:
- Barrier Score (out of 10): state the value clearly
- What this barrier means for the company (2-3 sentences)
- Business impact and risks (2-3 bullets)
- Why the severity level matters (1-2 bullets)
- Indicator-driven observations (reference the scores provided)
- KPIs to watch (3-4 specific metrics)

**Barrier Data:**

{barrier_data_text}

STOP after Barrier {barrier_numbers[-1]}. Do NOT continue to any other barrier.
Do NOT include Impact Value figures or strategic recommendations.
"""

    # Return whatever we got, even if incomplete
    logger.warning("Returning incomplete result for %s after all retries", label)
    return result


# ---------------------------------------------------------------------------
# Summary / Recommendations (internal helper – kept for potential future use)
# ---------------------------------------------------------------------------

async def _generate_summary_recommendations(
    company_details: Dict,
    barrier_scores: Dict[str, Dict],
    impact_values: Dict[str, Dict],
    current_time: str
) -> str:
    """Generate prioritization matrix and strategic recommendations"""

    # Sort barriers by impact value
    sorted_barriers = sorted(
        [(k, v) for k, v in impact_values.items()],
        key=lambda x: x[1]['impact_value'],
        reverse=True
    )

    # Build summary data
    priority_data = []
    for barrier_key, impact_data in sorted_barriers[:5]:  # Top 5
        barrier_data = barrier_scores[barrier_key]
        priority_data.append(f"- {barrier_data['name']}: Impact Value {impact_data['impact_value']:.4f}, Severity: {barrier_data['level']}")

    prompt = f"""
Complete the IoT Readiness Analysis for {company_details.get('company_name', 'N/A')} in the style of strategic_roadmap_report.pdf (slightly more detailed, clear sections).

**Company:** {company_details.get('company_name', 'N/A')} | {company_details.get('industry', 'N/A')} | {company_details.get('num_employees', 'N/A')} employees

Deliver TWO sections:

## 3) Prioritization Matrix
- Categorize all 15 barriers by urgency (Critical / High / Moderate / Low)
- Identify quick wins vs long-term investments
- Consider both impact value and implementation difficulty
- Present top priorities succinctly

**Top Priority Barriers (data to ground your matrix):**
{chr(10).join(priority_data)}

## 4) Strategic Recommendations
- Top 5 actionable recommendations for IoT adoption
- Expected outcomes and benefits (1 line each)
- Timeline buckets: Quick Wins (0-3 months), Build & Scale (4-9 months), Sustain (10-18+ months)
- Change management and risk notes (brief)

**Tone and format:**
- Professional consulting tone, concise bullets
- Plain language, practical steps
- Keep it readable and implementation-oriented
"""

    try:
        return await _generate_with_retry(prompt, label="recommendations")
    except httpx.HTTPStatusError as e:
        return f"OpenRouter API HTTP error (Recommendations): {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"OpenRouter API request error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


# ---------------------------------------------------------------------------
# Strategic Roadmap
# ---------------------------------------------------------------------------

async def generate_strategic_roadmap(
    company_details: Dict,
    top_barriers: List[tuple],
    barrier_scores: Dict[str, Dict]
) -> str:
    """
    Generate detailed strategic roadmap for the TOP 3 critical barriers
    Using OpenRouter API

    Args:
        company_details: Company information dictionary
        top_barriers: List of tuples (barrier_key, impact_data) for top 3 barriers
        barrier_scores: Complete barrier scores for context

    Returns:
        Markdown-formatted strategic roadmap report
    """
    if not OPENROUTER_API_KEY:
        return "OpenRouter API key is not configured. Cannot generate roadmap."

    # Build context for each of the top 3 barriers
    barrier_contexts = []

    for rank, (barrier_key, impact_data) in enumerate(top_barriers, 1):
        barrier_data = barrier_scores[barrier_key]

        # Present the impact value inline with the barrier title for clarity
        context = f"""
**Priority {rank}: {barrier_data['name']} — Impact Value: {impact_data['impact_value']:.4f}**

Severity: {barrier_data['level']}
Barrier Score: {barrier_data['total']:.2f} / 10

This barrier ranks as priority #{rank} due to its significant impact on IoT adoption readiness.
Current indicator performance shows specific challenges that need immediate attention.
"""
        barrier_contexts.append(context)

    prompt = f"""
You are a strategic IoT transformation consultant for Indian SMEs. Create a detailed, actionable roadmap to address the TOP 3 CRITICAL BARRIERS identified for this company.

**Company Context:**
- Name: {company_details.get('company_name', 'N/A')}
- Industry: {company_details.get('industry', 'N/A')}
- Size: {company_details.get('num_employees', 'N/A')} employees
- Revenue: ₹{company_details.get('annual_revenue', 'N/A')} Cr

**Top 3 Critical Barriers:**

{chr(10).join(barrier_contexts)}

**Required Roadmap Structure:**

# Strategic IoT Readiness Roadmap

## Executive Overview
- Brief summary of the critical challenges
- Overall transformation timeline (18-24 months)
- Expected business outcomes

## For Each of the 3 Barriers:

### Barrier [Name]

#### 1. Problem Statement
- Why this is critical for the organization
- Current state vs desired state
- Business impact if unaddressed

#### 2. Strategic Approach
- High-level strategy to overcome this barrier
- Key success factors

#### 3. Phased Implementation Plan

**Phase 1: Foundation (Months 0-3)**
- Specific immediate actions
- Quick wins to build momentum
- Resources required
- Deliverables

**Phase 2: Build & Scale (Months 4-9)**
- Core implementation activities
- Training and change management
- Technology/process deployment
- Expected milestones

**Phase 3: Optimize & Sustain (Months 10-18+)**
- Long-term optimization
- Continuous improvement mechanisms
- Scaling strategies
- Sustainability measures

#### 4. Key Performance Indicators (KPIs)
- 3-5 specific, measurable KPIs
- Target values and timelines

#### 5. Risk Mitigation
- Key risks and mitigation strategies

#### 6. Budget Considerations
- Estimated investment areas (without specific amounts)
- ROI expectations

## Cross-Barrier Success Factors
- Common themes across all three barriers
- Integrated change management approach
- Governance structure

## Conclusion
- Path forward summary
- Expected transformation outcomes

CRITICAL: You MUST cover ALL 3 barriers completely. Do NOT skip any barrier.

**Guidelines:**
- Be highly specific and actionable
- Focus on practical, implementable steps
- Consider SME resource constraints
- Include change management aspects
- Write in professional consulting tone
- Use Indian business context
"""

    try:
        return await _generate_with_retry(
            prompt, temperature=0.7, label="strategic roadmap"
        )
    except httpx.HTTPStatusError as e:
        return f"OpenRouter API HTTP error: {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"OpenRouter API request error: {e}"
    except Exception as e:
        return f"Unexpected error during OpenRouter API call: {e}"
