"""
Database service for MongoDB operations
"""
from pymongo import MongoClient
from typing import Dict, Optional
from datetime import datetime
from config.settings import MONGODB_URI, DATABASE_NAME


class DatabaseService:
    """MongoDB database service for storing analysis results"""
    
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[DATABASE_NAME]
    
    def save_raw_inputs(self, company: Dict, barriers: Dict, kpis: Dict, costs: Dict) -> str:
        """Save raw input data"""
        document = {
            "timestamp": datetime.now(),
            "company_details": company,
            "barriers_raw": barriers,
            "kpi_raw": kpis,
            "cost_raw": costs
        }
        result = self.db.raw_inputs.insert_one(document)
        return str(result.inserted_id)
    
    def save_barrier_scores(self, barrier_scores: Dict) -> str:
        """Save calculated barrier scores"""
        document = {
            "timestamp": datetime.now(),
            "barrier_scores": barrier_scores
        }
        result = self.db.barrier_scores.insert_one(document)
        return str(result.inserted_id)
    
    def save_cost_scores(self, cost_scores: Dict) -> str:
        """Save calculated cost factor scores"""
        document = {
            "timestamp": datetime.now(),
            "cost_scores": cost_scores
        }
        result = self.db.cost_scores.insert_one(document)
        return str(result.inserted_id)
    
    def save_kpi_scores(self, kpi_scores: Dict) -> str:
        """Save calculated KPI scores"""
        document = {
            "timestamp": datetime.now(),
            "kpi_scores": kpi_scores
        }
        result = self.db.kpi_scores.insert_one(document)
        return str(result.inserted_id)
    
    def save_impact_values(self, impact_values: Dict) -> str:
        """Save calculated impact values (ISRI)"""
        document = {
            "timestamp": datetime.now(),
            "impact_values": impact_values
        }
        result = self.db.impact_values.insert_one(document)
        return str(result.inserted_id)
    
    def save_report_metadata(self, barrier_id: int, pdf_path: str, report_type: str) -> str:
        """Save report generation metadata"""
        document = {
            "timestamp": datetime.now(),
            "barrier_id": barrier_id,
            "pdf_path": pdf_path,
            "report_type": report_type
        }
        result = self.db.generated_reports.insert_one(document)
        return str(result.inserted_id)
    
    def close(self):
        """Close database connection"""
        self.client.close()
