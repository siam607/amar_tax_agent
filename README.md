
# Amar Tax AI Agent

A Multi-Agent Virtual Tax Advisor for Bangladesh
built using Python, CrewAI and Google Gemini.

## Project Overview

Amar Tax helps users understand their individual
income tax readiness using a specialized
Multi-Agent System.

## AI Agents

1. Classifier Agent - Taxpayer Eligibility
2. Calculator Agent - Tax Computation
3. Document Agent - Document Checklist
4. Reviewer Agent - Compliance Validation

## Technologies

- Python
- CrewAI
- Google Gemini
- Pydantic
- JSON
- Markdown

## Features

- Taxpayer classification
- Tax slab calculation
- Investment rebate calculation
- Document checklist generation
- Compliance review
- Structured Pydantic output
- Custom CrewAI tools
- Local JSON database fallback
- Error handling

## Installation

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Create a .env file and add:

GEMINI_API_KEY=your_api_key

## Run

```bash
python main.py
```

## Output

The final Tax Readiness Report is saved as:

tax_report.md

## Assumptions

- The supplied simulated 2026-27 JSON database
  is the source of truth.
- Taxable income equals total income.
- Slabs start after the tax-free threshold.
- Allowable investment is capped at 20% of income.
- Investment rebate is 15%.
- Net tax is compared with minimum tax.
- Income at or below the threshold is not
  mandatory for filing under this assignment's rules.
- A person below 18 cannot file independently.

## Disclaimer

This is an academic simulation based on the
assignment database, not official tax advice.
