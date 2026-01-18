"""
Cost factor calculation service
"""
from typing import Dict
from models.input_models import CostFactorInput


def calculate_cost_factor_scores(cost_factors: CostFactorInput) -> Dict[str, float]:
    """
    Calculate cost factor impact scores for all 15 barriers
    Returns a dictionary with barrier keys and their cost impact scores
    """
    cost_values = [
        cost_factors.aftermarket_services_warranty,
        cost_factors.depreciation,
        cost_factors.labour,
        cost_factors.maintenance_repair,
        cost_factors.raw_materials_consumables,
        cost_factors.rental_operating_lease,
        cost_factors.research_development,
        cost_factors.selling_general_administrative_expense,
        cost_factors.utilities,
        cost_factors.earnings_before_interest_taxes_ebit,
        cost_factors.financing_costs_interest,
        cost_factors.taxation_compliance_costs,
        cost_factors.supply_chain_logistics_costs,
        cost_factors.technology_digital_infrastructure_costs,
        cost_factors.training_skill_development_costs,
        cost_factors.regulatory_compliance_costs,
        cost_factors.insurance_costs,
        cost_factors.marketing_customer_acquisition_costs,
        cost_factors.environmental_social_responsibility_costs,
        cost_factors.quality_control_assurance
    ]

    # Weight matrices for each barrier (20 cost factors × 15 barriers)
    barrier_weights = [
        [0, 0, 2, 0, 0, 0, 2, 1, 0, 2, 1, 1, 1, 3, 3, 1, 1, 1, 2, 1],  # Barrier 1
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  # Barrier 2
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 3, 3, 1, 1, 1, 2, 1],  # Barrier 3
        [0, 0, 2, 0, 0, 0, 2, 1, 0, 1, 1, 1, 1, 3, 3, 1, 1, 1, 2, 1],  # Barrier 4
        [0, 0, 2, 0, 0, 0, 2, 1, 0, 2, 1, 1, 1, 3, 3, 1, 1, 1, 2, 1],  # Barrier 5
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  # Barrier 6
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  # Barrier 7
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1],  # Barrier 8
        [0, 0, 2, 0, 0, 0, 1, 2, 0, 3, 3, 1, 2, 1, 1, 1, 1, 1, 1, 1],  # Barrier 9
        [2, 1, 3, 2, 2, 1, 3, 3, 2, 3, 2, 2, 3, 3, 3, 3, 1, 3, 2, 3],  # Barrier 10
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 2, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1],  # Barrier 11
        [0, 0, 2, 0, 0, 0, 2, 1, 0, 3, 2, 3, 2, 1, 1, 3, 1, 1, 1, 1],  # Barrier 12
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 2, 2, 3, 2, 1, 1, 3, 1, 1, 1, 1],  # Barrier 13
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 2, 2, 3, 2, 1, 1, 3, 1, 1, 1, 1],  # Barrier 14
        [0, 0, 2, 0, 0, 0, 1, 1, 0, 2, 1, 1, 2, 3, 3, 1, 1, 1, 1, 1],  # Barrier 15
    ]

    results = {}
    for i in range(15):
        score_sum = sum(cost_values[j] * barrier_weights[i][j] for j in range(20))
        results[f"barrier_{i + 1}"] = score_sum

    return results
