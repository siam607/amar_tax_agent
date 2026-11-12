
import os
import json
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv
from crewai.tools import tool

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

DB_PATH = Path(__file__).parent / "tax_db.json"


# -----------------------------------
# 1. Load Local Tax Database
# -----------------------------------

def load_tax_db():

    with open(DB_PATH, "r", encoding="utf-8") as file:
        local_db = json.load(file)

    remote_url = os.getenv("TAX_DB_API_URL")

    if remote_url:

        try:
            response = requests.get(
                remote_url,
                timeout=10
            )

            response.raise_for_status()

            logging.info("Remote Tax API loaded successfully.")

            return response.json()

        except Exception as error:

            logging.warning(f"Remote API failed: {error}")
            logging.warning("Using Local JSON Database as fallback.")

    else:

        logging.info(
            "Remote API not configured. Using Local JSON Database."
        )

    return local_db


# -----------------------------------
# 2. Custom Tool: Tax DB Lookup
# -----------------------------------

@tool("lookup_tax_db")
def lookup_tax_db() -> str:
    """Retrieve tax thresholds, slabs, minimum tax,
    investment rebate and document rules from the database."""

    db = load_tax_db()

    return json.dumps(db, indent=2)


# -----------------------------------
# 3. Custom Tool: Tax Calculation
# -----------------------------------

@tool("calculate_slab_tax")
def calculate_slab_tax(
    income: float,
    threshold: float,
    investment: float,
    minimum_tax: float
) -> str:
    """Calculate gross tax, investment rebate and minimum
    payable tax using the Local Tax Database."""

    db = load_tax_db()
    warnings = []

    # 1. Validate Input

    if income < 0:
        return json.dumps({
            "error": "Income cannot be negative.",
            "gross_tax": 0,
            "investment_rebate": 0,
            "minimum_tax": 0,
            "net_payable_tax": 0,
            "warnings": ["Invalid negative income."]
        }, indent=2)

    if threshold < 0:
        return json.dumps({
            "error": "Tax-free threshold cannot be negative."
        }, indent=2)

    if minimum_tax < 0:
        warnings.append("Negative minimum tax is invalid.")
        minimum_tax = 0

    if investment < 0:
        warnings.append("Negative investment is invalid.")
        investment = 0

    if investment > income:
        warnings.append(
            "Investment exceeds total income. Please verify."
        )

    # 2. Calculate Taxable Income

    taxable_income = max(0, income - threshold)

    # 3. Calculate Gross Tax

    gross_tax = 0
    remaining_income = taxable_income

    for slab in db["slabs_after_threshold"]:

        limit = slab["limit"]
        rate = slab["rate"]

        if remaining_income <= 0:
            break

        if limit is None:
            slab_income = remaining_income
        else:
            slab_income = min(remaining_income, limit)

        gross_tax += slab_income * rate
        remaining_income -= slab_income

    # 4. Calculate Investment Rebate

    rebate_rules = db["investment_rebate"]

    maximum_investment = (
        income *
        rebate_rules["max_investment_percent_of_income"]
    )

    allowable_investment = min(
        investment,
        maximum_investment
    )

    investment_rebate = (
        allowable_investment *
        rebate_rules["rate"]
    )

    # 5. Calculate Tax After Rebate

    net_tax_before_minimum = max(
        0,
        gross_tax - investment_rebate
    )

    # 6. Apply Minimum Tax

    net_payable_tax = max(
        net_tax_before_minimum,
        minimum_tax
    )

    # 7. Prepare Final Result

    result = {

        "total_income": round(income, 2),

        "tax_free_threshold": round(threshold, 2),

        "taxable_income": round(taxable_income, 2),

        "gross_tax": round(gross_tax, 2),

        "allowable_investment": round(
            allowable_investment, 2
        ),

        "investment_rebate": round(
            investment_rebate, 2
        ),

        "net_tax_before_minimum": round(
            net_tax_before_minimum, 2
        ),

        "minimum_tax": round(minimum_tax, 2),

        "net_payable_tax": round(
            net_payable_tax, 2
        ),

        "warnings": warnings

    }

    return json.dumps(result, indent=2)


# -----------------------------------
# 4. Custom Tool: Document Lookup
# -----------------------------------

@tool("lookup_documents")
def lookup_documents(
    profession: str,
    income_sources: str,
    has_tin: bool,
    investment: float
) -> str:
    """Generate a customized tax return document checklist
    based on profession, income sources, TIN and investment."""

    db = load_tax_db()

    required_docs = db["required_docs"]

    documents = []
    warnings = []

    # TIN Documents

    if has_tin:
        documents.append("TIN Certificate")
    else:
        documents.append("TIN Registration")

    # Common Documents

    documents.extend(
        doc for doc in required_docs["common"]
        if doc != "TIN Certificate"
    )

    sources = [
        item.strip().lower()
        for item in income_sources.split(",")
        if item.strip()
    ]

    # Profession-based fallback

    if not sources:

        profession = profession.lower()

        if any(word in profession for word in [
            "engineer", "employee", "software",
            "job", "salaried"
        ]):
            sources.append("salaried")

        elif "freelance" in profession:
            sources.append("freelancer")

        elif "business" in profession:
            sources.append("business")

        elif "landlord" in profession:
            sources.append("landlord")

        else:
            warnings.append(
                "Profession not found. Using general checklist."
            )

    # Income Source Documents

    valid_sources = [
        "salaried",
        "business",
        "freelancer",
        "landlord"
    ]

    for source in sources:

        if source in valid_sources:

            documents.extend(
                required_docs[source]
            )

        else:

            warnings.append(
                f"Unknown income source: {source}"
            )

    # Investment Documents

    if investment > 0:

        documents.extend(
            required_docs["investor"]
        )

    # Remove Duplicate Documents

    documents = list(dict.fromkeys(documents))

    return json.dumps({

        "documents_needed": documents,

        "warnings": warnings

    }, indent=2)
