
from pydantic import BaseModel, Field
from typing import List


class TaxpayerEligibility(BaseModel):

    taxpayer_category: str = Field(
        description="Category of the taxpayer"
    )

    filing_mandatory: bool = Field(
        description="Whether tax filing is mandatory"
    )

    tax_free_threshold: int = Field(
        description="Tax-free income threshold in BDT"
    )

    minimum_tax: int = Field(
        description="Minimum applicable tax in BDT"
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Important tax warnings or conditions"
    )
