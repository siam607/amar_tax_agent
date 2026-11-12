
from crewai import Task
from model import TaxpayerEligibility

from agents import (
    classifier_agent,
    calculator_agent,
    document_agent,
    reviewer_agent
)

from model import TaxpayerEligibility


# 1. Taxpayer Eligibility Task
eligibility_task = Task(
    description="""
    Analyze the taxpayer's information.

    Determine:
    - Taxpayer category
    - Whether tax filing is mandatory
    - Tax-free income threshold
    - Minimum tax amount
    - Any warnings or special conditions

    Minimum tax rules:
    - Dhaka and Chattogram: 5000 BDT
    - Other City Corporations: 4000 BDT
    - Other areas: 3000 BDT
    - Rangpur is an Other City Corporation.

    Use the available tax database.
    """,

    expected_output="A structured taxpayer eligibility report.",

    agent=classifier_agent,

    output_pydantic=TaxpayerEligibility
)


# 2. Tax Calculation Task
calculation_task = Task(
    description="""
    Calculate the taxpayer's income tax.

    Use the taxpayer eligibility information
    from the previous task.

    Calculate applicable tax, rebates and payable tax.
    """,

    expected_output="A detailed income tax calculation.",

    agent=calculator_agent,

    context=[eligibility_task]
)


# 3. Document Preparation Task
document_task = Task(
    description="""
    Prepare a tax report based on the eligibility
    and tax calculation results.

    Include all important taxpayer information.
    """,

    expected_output="A complete taxpayer tax report.",

    agent=document_agent,

    context=[eligibility_task, calculation_task]
)


# 4. Final Review Task
review_task = Task(
    description="""
    Review all previous tasks.

    Check calculations and taxpayer information.

    Prepare the final report in a Markdown table.

    Also provide a short summary in Bangla
    using 3-4 lines.
    """,

    expected_output="A reviewed final tax report in Markdown with a Bangla summary.",

    agent=reviewer_agent,

    context=[
        eligibility_task,
        calculation_task,
        document_task
    ]
)


