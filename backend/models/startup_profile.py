from pydantic import BaseModel, Field


class StartupProfile(BaseModel):
    startup_name: str = Field(description="Name of the startup")
    tagline: str = Field(default="", description="Short tagline or one-liner")
    problem_statement: str = Field(description="The problem being solved")
    target_customers: str = Field(description="Description of target customers")
    solution: str = Field(description="Description of the solution")
    business_model: str = Field(description="How the startup makes money")
    market_knowledge: str = Field(description="Founder's understanding of the market")
    technical_information: str = Field(description="Technical details about the product")
    founder_assumptions: str = Field(default="", description="Key assumptions by the founder")
    validation_objectives: str = Field(default="", description="What the founder wants to validate")
    industry: str = Field(default="", description="Primary industry")
    stage: str = Field(default="idea", description="Current startup stage")
