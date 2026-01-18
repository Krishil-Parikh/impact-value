# ISRI Backend API

## Overview
This is the reorganized backend for the Indian SME Readiness Index (ISRI) calculation system. The backend provides comprehensive IoT readiness assessment for Indian SMEs through barrier analysis, cost/KPI factor evaluation, and AI-powered reporting using **OpenRouter API**.

## Technology Stack

**API Integration:**
- 🤖 **OpenRouter API** - Unified interface for multiple AI models
- 🧠 **Mistral Large 2512** (default model via OpenRouter)
- Alternative: Claude, GPT, or any other OpenRouter-supported model

**Backend:**
- FastAPI + Uvicorn
- Pydantic models for validation
- MongoDB for data persistence
- WeasyPrint for PDF generation

## Project Structure
```
backend/
├── app.py                          # Main FastAPI application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── README.md                       # This file
├── config/
│   ├── __init__.py
│   └── settings.py                 # Configuration settings
├── models/
│   ├── __init__.py
│   └── input_models.py             # Pydantic input models
├── services/
│   ├── __init__.py
│   ├── barrier_service.py          # Barrier score calculations
│   ├── cost_service.py             # Cost factor calculations
│   ├── kpi_service.py              # KPI factor calculations
│   ├── isri_service.py             # Impact value calculations
│   ├── ai_service.py               # Mistral AI integration
│   └── database_service.py         # MongoDB operations
├── utils/
│   ├── __init__.py
│   └── pdf_utils.py                # PDF generation utilities
└── barrier_analysis/               # Pre-generated barrier PDFs

```

## Features

### ✅ Complete ISRI Calculation System
- **15 Barrier Assessments**: Comprehensive evaluation of IoT adoption barriers
- **Cost Factor Analysis**: 20 cost categories mapped to barriers
- **KPI Factor Analysis**: 17 KPI indicators for business impact
- **Impact Value Calculation**: Weighted scoring (30% barrier, 30% cost, 40% KPI)

### ✅ AI-Powered Report Generation
- **Comprehensive Barrier Analysis**: Detailed analysis of ALL 15 barriers using Mistral AI
- **Strategic Roadmap**: Phased implementation plan for TOP 3 critical barriers
- **Professional PDFs**: Markdown-to-PDF conversion with custom styling

### ✅ Data Persistence
- **MongoDB Integration**: Stores all calculations and results
- **Historical Tracking**: Maintains audit trail of assessments

## Installation

### 1. Prerequisites
- Python 3.10+
- MongoDB (local or Atlas)
- Mistral AI API key

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
SITE_URL=http://localhost:3000
SITE_NAME=ISRI Assessment
MONGODB_URI=mongodb://localhost:27017/
```

**How to get OpenRouter API Key:**
1. Go to https://openrouter.ai/keys
2. Sign up or log in
3. Create a new API key
4. Paste it in `.env`

### 4. Run the Server
```bash
# Development mode (with auto-reload)
python app.py

# Or using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Main Endpoint
**POST** `/generate_full_report`

Performs complete ISRI analysis and returns ZIP file with reports.

**Request Body**: `ComprehensiveInput` (JSON)
```json
{
  "company_details": {
    "company_name": "ABC Manufacturing",
    "industry": "Automotive",
    "num_employees": 250,
    "annual_revenue": 50.0
  },
  "barrier1": {
    "num_training_programs": 3.0,
    "pct_employees_trained": 25.0,
    "pct_budget_training_of_payroll": 1.5
  },
  // ... barriers 2-15
  "cost_factor_inputs": { ... },
  "kpi_factor_inputs": { ... }
}
```

**Response**: ZIP file containing:
- `01_Comprehensive_Barrier_Analysis.pdf` - Analysis of all 15 barriers
- `02_Strategic_Roadmap_Top_3_Barriers.pdf` - Detailed roadmap for top 3

### Utility Endpoints
- **GET** `/` - Health check
- **GET** `/health` - Detailed health status
- **GET** `/api/barrier-definitions` - List of all 15 barriers

## Key Improvements from Previous Version

### 🎯 Fixed Issues
1. **Top 3 Barrier Logic**: Now correctly identifies and ranks barriers by impact value
2. **Complete Report Generation**: 
   - Generates analysis for ALL 15 barriers (not just top 3)
   - Generates detailed roadmap specifically for top 3 critical barriers
3. **Proper Calculation**: Aligned with correct formulas and normalization
4. **Organized Structure**: Modular design with separated concerns

### 🏗️ Architecture Changes
- **Modularized Services**: Separate files for each calculation type
- **Clear Separation**: Models, services, utils, and config in separate modules
- **Database Integration**: Optional MongoDB storage
- **Better Error Handling**: Proper exception handling and logging
- **CORS Support**: Ready for frontend integration

## Usage Example

```python
import requests

# Prepare input data
data = {
    "company_details": {
        "company_name": "Tech Solutions Pvt Ltd",
        "industry": "Manufacturing",
        "num_employees": 150,
        "annual_revenue": 25.5
    },
    # ... add all barrier, cost, and KPI inputs
}

# Make request
response = requests.post(
    "http://localhost:8000/generate_full_report",
    json=data
)

# Save ZIP file
with open("isri_report.zip", "wb") as f:
    f.write(response.content)
```

## Calculation Logic

### Barrier Scores (0-10 scale)
Each barrier has 2-3 indicators with specific weights and calculation methods:
- **Inverted Ratio**: `1 - (value / target)`
- **Percentage**: `value / 100`
- **Ratio**: `value / crisis_level`
- **Frequency Mapping**: Discrete values mapped to scores

### Impact Value Formula
```
Impact = (0.3 × Normalized_Barrier_Score) + 
         (0.3 × Normalized_Cost_Score) + 
         (0.4 × Normalized_KPI_Score)
```

## Development

### Adding New Features
1. Add models to `models/input_models.py`
2. Add calculation logic to appropriate service
3. Update `app.py` endpoint if needed
4. Update this README

### Testing
```bash
# Run with test data
python -c "from app import *; print('Import successful')"
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the `backend` directory
   - Check all `__init__.py` files exist

2. **MongoDB Connection**
   - Verify MongoDB is running: `mongosh`
   - Check connection string in `.env`

3. **PDF Generation Fails**
   - Install system dependencies for WeasyPrint
   - On Windows: Install GTK3 runtime
   - On macOS: `brew install python-tk cairo pango gdk-pixbuf libffi`
   - On Linux: `sudo apt install libcairo2-dev libpango-1.0-0 libpango-cairo-1.0-0`

4. **OpenRouter API Errors**
   - Verify API key is valid: https://openrouter.ai/keys
   - Check you have available credits
   - Verify rate limits aren't exceeded
   - Check model name is correct: `mistralai/mistral-large-2512`

5. **Model Not Available**
   - If using custom model, verify it's supported by OpenRouter
   - Check: https://openrouter.ai/docs#models

## Security Notes

⚠️ **Important**: 
- Never commit `.env` file (already in .gitignore)
- Keep API keys secure - **never share them in chat or code**
- OpenRouter is better than direct API keys (can rotate without code changes)
- Use environment variables in production
- Implement proper authentication for production use

## Changing the AI Model

You can easily switch to other models supported by OpenRouter:

**Edit `config/settings.py`:**
```python
# Option 1: Claude (best quality, slower)
OPENROUTER_MODEL: str = "anthropic/claude-3-opus"

# Option 2: GPT-4 (expensive, very good)
OPENROUTER_MODEL: str = "openai/gpt-4-turbo"

# Option 3: Local models via Ollama integration
OPENROUTER_MODEL: str = "ollama/mistral"

# See all models: https://openrouter.ai/docs#models
```

No other code changes needed - it's that simple!

## License
Proprietary - All rights reserved

## Support
For issues or questions, contact the development team.
