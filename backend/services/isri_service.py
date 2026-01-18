"""
ISRI (Impact Value) calculation service
Combines barrier, cost, and KPI scores to calculate final impact values
"""
from typing import Dict, List, Tuple
from config.settings import WEIGHT_BARRIER_SCORE, WEIGHT_COST_FACTOR, WEIGHT_KPI_FACTOR


def calculate_impact_values(
    barrier_scores: Dict[str, Dict],
    cost_scores: Dict[str, float],
    kpi_scores: Dict[str, float]
) -> Dict[str, Dict]:
    """
    Calculate the final impact value (ISRI) for each barrier
    
    Args:
        barrier_scores: Dictionary with barrier scores from barrier_service
        cost_scores: Dictionary with cost impact scores from cost_service
        kpi_scores: Dictionary with KPI impact scores from kpi_service
    
    Returns:
        Dictionary with barrier names as keys and impact details as values
    """
    # Calculate totals for normalization
    barrier_score_total = sum(b["total"] for b in barrier_scores.values())
    cost_score_total = sum(cost_scores.values())
    kpi_score_total = sum(kpi_scores.values())

    impact_values = {}

    for i in range(1, 16):
        barrier_key = f"barrier{i}"
        cost_key = f"barrier_{i}"
        
        # Get raw scores
        barrier_raw = barrier_scores[barrier_key]["total"]
        cost_raw = cost_scores[cost_key]
        kpi_raw = kpi_scores[cost_key]

        # Normalize scores
        barrier_norm = (barrier_raw / barrier_score_total) if barrier_score_total != 0 else 0
        cost_norm = (cost_raw / cost_score_total) if cost_score_total != 0 else 0
        kpi_norm = (kpi_raw / kpi_score_total) if kpi_score_total != 0 else 0

        # Calculate final impact value
        impact = (
            (WEIGHT_BARRIER_SCORE * barrier_norm) +
            (WEIGHT_COST_FACTOR * cost_norm) +
            (WEIGHT_KPI_FACTOR * kpi_norm)
        )

        impact_values[barrier_key] = {
            "barrier_name": barrier_scores[barrier_key]["name"],
            "barrier_score": barrier_raw,
            "barrier_level": barrier_scores[barrier_key]["level"],
            "cost_score": cost_raw,
            "kpi_score": kpi_raw,
            "barrier_score_normalized": barrier_norm,
            "cost_score_normalized": cost_norm,
            "kpi_score_normalized": kpi_norm,
            "impact_value": impact
        }

    return impact_values


def get_top_n_barriers(impact_values: Dict[str, Dict], n: int = 3) -> List[Tuple[str, Dict]]:
    """
    Get the top N barriers by impact value
    
    Args:
        impact_values: Dictionary of impact values from calculate_impact_values
        n: Number of top barriers to return (default: 3)
    
    Returns:
        List of tuples (barrier_key, barrier_data) sorted by impact value (highest first)
    """
    sorted_barriers = sorted(
        impact_values.items(),
        key=lambda x: x[1]["impact_value"],
        reverse=True
    )
    return sorted_barriers[:n]
