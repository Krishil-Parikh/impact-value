"""
KPI factor calculation service
"""
from typing import Dict
from models.input_models import KPIFactorInput


def calculate_kpi_scores(kpi_inputs: KPIFactorInput) -> Dict[str, float]:
    """
    Calculate KPI impact scores for all 15 barriers
    Returns a dictionary with barrier keys and their KPI impact scores
    """
    kpi_values = [
        kpi_inputs.asset_equipment_efficiency,
        kpi_inputs.utilities_efficiency,
        kpi_inputs.inventory_efficiency,
        kpi_inputs.process_quality,
        kpi_inputs.product_quality,
        kpi_inputs.safety_security,
        kpi_inputs.planning_scheduling_effectiveness,
        kpi_inputs.time_to_market,
        kpi_inputs.production_flexibility,
        kpi_inputs.customer_satisfaction,
        kpi_inputs.supply_chain_efficiency,
        kpi_inputs.market_share_growth,
        kpi_inputs.employee_productivity,
        kpi_inputs.return_on_investment_roi,
        kpi_inputs.financial_health_and_stability,
        kpi_inputs.talent_retention,
        kpi_inputs.customer_retention_rate
    ]

    # Weight matrices for each barrier (17 KPI factors × 15 barriers)
    barrier_weights = [
        [1, 1, 1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 3, 2, 2, 3, 2],  # Barrier 1
        [1, 1, 1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 3, 2, 2, 3, 2],  # Barrier 2
        [1, 1, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 3, 2, 2, 3, 2],  # Barrier 3
        [1, 1, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 3, 2, 2, 3, 2],  # Barrier 4
        [1, 1, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 3, 2, 2, 2, 2],  # Barrier 5
        [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 3, 3, 1, 2],  # Barrier 6
        [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2],  # Barrier 7
        [1, 0, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1],  # Barrier 8
        [2, 1, 2, 1, 1, 0, 1, 2, 2, 1, 2, 2, 2, 3, 3, 1, 1],  # Barrier 9
        [3, 2, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3],  # Barrier 10
        [2, 1, 2, 1, 1, 1, 2, 2, 2, 1, 3, 1, 2, 2, 2, 1, 2],  # Barrier 11
        [1, 0, 1, 1, 1, 0, 1, 2, 1, 1, 2, 1, 1, 3, 3, 1, 1],  # Barrier 12
        [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 3, 3, 1, 2],  # Barrier 13
        [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 3, 3, 1, 2],  # Barrier 14
        [1, 0, 1, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 3],  # Barrier 15
    ]

    results = {}
    for i in range(15):
        score_sum = sum(kpi_values[j] * barrier_weights[i][j] for j in range(17))
        results[f"barrier_{i + 1}"] = score_sum

    return results
