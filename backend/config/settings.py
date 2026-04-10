"""
Configuration settings for the ISRI application
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend folder (if present)
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=str(dotenv_path))

# AI Provider selection — "gemini" or "openrouter"
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openrouter")

# Google Gemini API Configuration
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemma-3-27b-it")
GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"

# OpenRouter AI Configuration (fallback)
OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
# OPENROUTER_MODEL: str = "mistralai/mistral-large-2512"
OPENROUTER_MODEL: str = "mistralai/mixtral-8x7b-instruct"
OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_SITE_URL: str = os.getenv("SITE_URL", "http://localhost:3000")
OPENROUTER_SITE_NAME: str = os.getenv("SITE_NAME", "ISRI Assessment")

# ISRI Calculation Weights
WEIGHT_BARRIER_SCORE = 0.3
WEIGHT_COST_FACTOR = 0.3
WEIGHT_KPI_FACTOR = 0.4

# Report Generation Settings
OUTPUT_DIR = "generated_reports"
CHART_DIR = "charts"
BARRIER_ANALYSIS_DIR = "barrier_analysis"

# AI Generation Settings
AI_TEMPERATURE = 0.5
AI_MAX_TOKENS = 8000  # Enough room for verbose models like Llama 3.1
AI_TIMEOUT = 120.0
