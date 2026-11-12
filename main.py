
import json
from pathlib import Path

from crewai import Crew, Process

from agents import (
    classifier_agent,
    calculator_agent,
    document_agent,
    reviewer_agent
)

from tasks import (
    eligibility_task,
    calculation_task,
    document_task,
    review_task
)

from tools import load_tax_db


# ===================================
# USER PROFILE
# ===================================

user_profile = {

    "age": 34,

    "gender": "Female",

    "profession": "Software Engineer",

    "income": 1500000,

    "investment": 200000,

    "location": "Dhaka",

    "has_tin": True,

    "is_disabled": False,

    "is_freedom_fighter": False,

    "income_sources": "salaried,freelancer",

    "claims_required_to_file": False
}


# ===================================
# LOAD LOCAL DATABASE
# ===================================

print("\nLoading Tax Database...")

tax_db = load_tax_db()

user_profile["tax_rules"] = json.dumps(
    tax_db,
    indent=2
)


# ===================================
# CREATE CREW
# ===================================

tax_crew = Crew(

    agents=[
        classifier_agent,
        calculator_agent,
        document_agent,
        reviewer_agent
    ],

    tasks=[
        eligibility_task,
        calculation_task,
        document_task,
        review_task
    ],

    process=Process.sequential,

    verbose=True
)


# ===================================
# EXECUTE CREW
# ===================================

try:

    print("\n===================================")
    print("       AMAR TAX AI AGENT")
    print("===================================")

    result = tax_crew.kickoff(
        inputs=user_profile
    )

    # Final Output
    report = result.raw

    print("\n========== FINAL TAX REPORT ==========\n")

    print(report)

    # Save Report
    report_path = Path("tax_report.md")

    report_path.write_text(
        report,
        encoding="utf-8"
    )

    print("\nReport saved successfully!")

    print("File: tax_report.md")

except Exception as error:

    print("\nERROR OCCURRED!")

    print(type(error).__name__)

    print(str(error))
