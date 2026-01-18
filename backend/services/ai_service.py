"""
AI service for generating reports using OpenRouter API
Supports multiple models including Mistral, GPT, Claude, etc.
"""
import httpx
from typing import Dict, List
import datetime
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


async def generate_comprehensive_barrier_analysis(
    company_details: Dict,
    barrier_scores: Dict[str, Dict],
    impact_values: Dict[str, Dict]
) -> str:
    """
    Generate comprehensive AI-powered analysis for ALL 15 barriers in parts
    Splits generation into 4 chunks to stay within token limits, then stitches together
    Using OpenRouter API with Mistral model
    
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
    
    # Split barriers into 4 groups to stay within token limits
    barrier_groups = [
        list(range(1, 5)),    # Barriers 1-4
        list(range(5, 9)),    # Barriers 5-8
        list(range(9, 13)),   # Barriers 9-12
        list(range(13, 16))   # Barriers 13-15
    ]
    
    parts = []
    
    # Part 1: Executive Summary + First Group Analysis
    part1 = await _generate_analysis_part(
        company_details, barrier_scores, impact_values,
        barrier_groups[0], current_time, include_summary=True
    )
    parts.append(part1)
    
    # Parts 2-4: Remaining barrier groups
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


async def _generate_analysis_part(
    company_details: Dict,
    barrier_scores: Dict[str, Dict],
    impact_values: Dict[str, Dict],
    barrier_numbers: List[int],
    current_time: str,
    include_summary: bool = False
) -> str:
    """Generate analysis for a specific group of barriers"""
    
    barrier_sections = []
    
    for i in barrier_numbers:
        barrier_key = f"barrier{i}"
        barrier_data = barrier_scores[barrier_key]
        # For barrier analysis reports we include the barrier score (out of 10) and
        # an indicator breakdown. DO NOT include any impact value or strategic
        # recommendations here — those belong only in the strategic roadmap.
        section = f"""
### Barrier {i}: {barrier_data['name']}

**Assessment:**
- Barrier Score (out of 10): {barrier_data['total']:.2f}
- Severity Level: {barrier_data['level']}

**Indicator Breakdown:**
"""
        for indicator_name, indicator_score in barrier_data['indicators'].items():
            section += f"- {indicator_name.replace('_', ' ').title()}: {indicator_score:.2f}\n"
        
        barrier_sections.append(section)
    
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

## 2) Detailed Barrier Analysis for Barriers {barrier_numbers[0]}-{barrier_numbers[-1]}
For EACH barrier below, produce this structure:
- Barrier Score (out of 10): state the value clearly
- What this barrier means for the company (2-3 sentences)
- Business impact and risks (2-3 bullets)
- Why the severity level matters (1-2 bullets)
- Indicator-driven observations (reference the scores provided)
- KPIs to watch (3-4 specific metrics)

IMPORTANT: Do NOT include any Impact Value figures or strategic recommendations in this comprehensive barrier analysis. Strategic recommendations, phased plans and suggested actions must be produced only in the Strategic Roadmap report.

**Barrier Data to use:**

{chr(10).join(barrier_sections)}

**Tone and format:**
- Professional consulting tone, concise bullets
- Plain language (avoid jargon)
- Keep the section focused and practical
"""
    else:
        prompt = f"""
Continue the IoT Readiness Analysis for {company_details.get('company_name', 'N/A')} in the same style as the sample barrier_analysis_report.pdf, slightly more detailed.

**Task:** Provide detailed analysis for Barriers {barrier_numbers[0]}-{barrier_numbers[-1]} using this structure per barrier:
- Barrier Score (out of 10): state the value clearly
- What this barrier means for the company (2-3 sentences)
- Business impact and risks (2-3 bullets)
- Why the severity level matters (1-2 bullets)
- Indicator-driven observations (reference the scores provided)
- KPIs to watch (3-4 specific metrics)

IMPORTANT: Do NOT include any Impact Value figures or strategic recommendations in this comprehensive barrier analysis. Strategic recommendations, phased plans and suggested actions must be produced only in the Strategic Roadmap report.

**Barrier Data to use:**

{chr(10).join(barrier_sections)}

**Tone and format:**
- Professional consulting tone, concise bullets
- Plain language (avoid jargon)
- Keep the section focused and practical
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_SITE_NAME,
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": AI_TEMPERATURE,
        "max_tokens": AI_MAX_TOKENS,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=AI_TIMEOUT
            )
            response.raise_for_status()
            api_response = response.json()
            
            if api_response and api_response.get("choices"):
                return api_response["choices"][0]["message"]["content"]
            else:
                return f"OpenRouter API did not return valid response for barriers {barrier_numbers[0]}-{barrier_numbers[-1]}."
                
    except httpx.HTTPStatusError as e:
        return f"OpenRouter API HTTP error (Part {barrier_numbers[0]}-{barrier_numbers[-1]}): {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"OpenRouter API request error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


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

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_SITE_NAME,
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": AI_TEMPERATURE,
        "max_tokens": AI_MAX_TOKENS,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=AI_TIMEOUT
            )
            response.raise_for_status()
            api_response = response.json()
            
            if api_response and api_response.get("choices"):
                return api_response["choices"][0]["message"]["content"]
            else:
                return "OpenRouter API did not return valid response for recommendations."
                
    except httpx.HTTPStatusError as e:
        return f"OpenRouter API HTTP error (Recommendations): {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"OpenRouter API request error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


async def generate_strategic_roadmap(
    company_details: Dict,
    top_barriers: List[tuple],
    barrier_scores: Dict[str, Dict]
) -> str:
    """
    Generate detailed strategic roadmap for the TOP 3 critical barriers
    Using OpenRouter API with Mistral model
    
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

**Guidelines:**
- Be highly specific and actionable
- Focus on practical, implementable steps
- Consider SME resource constraints
- Include change management aspects
- Write in professional consulting tone
- Use Indian business context
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_SITE_NAME,
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": AI_MAX_TOKENS,  # Using reduced token limit
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=AI_TIMEOUT
            )
            response.raise_for_status()
            mistral_response = response.json()
            
            if mistral_response and mistral_response.get("choices"):
                return mistral_response["choices"][0]["message"]["content"]
            else:
                return "OpenRouter API did not return a valid response for the roadmap."
                
    except httpx.HTTPStatusError as e:
        return f"OpenRouter API HTTP error: {e.response.status_code} - {e.response.text}"
    except httpx.RequestError as e:
        return f"OpenRouter API request error: {e}"
    except Exception as e:
        return f"Unexpected error during OpenRouter API call: {e}"
