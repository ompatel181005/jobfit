from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class MatchComponents(BaseModel):
    """Individual component scores for resume-job matching"""
    skills: float = Field(..., description="Skills match score (0-1)", ge=0, le=1)
    responsibilities: float = Field(..., description="Responsibilities match score (0-1)", ge=0, le=1)
    title: float = Field(..., description="Title/role match score (0-1)", ge=0, le=1)
    semantic: float = Field(..., description="Semantic similarity score (0-1)", ge=0, le=1)


class MatchResult(BaseModel):
    """Overall match result with component breakdown"""
    score: float = Field(..., description="Weighted overall match score (0-1)", ge=0, le=1)
    components: MatchComponents


class ImprovementsItem(BaseModel):
    """A single resume improvement recommendation"""
    title: str = Field(..., max_length=100, description="Improvement title")
    reason: str = Field(..., max_length=300, description="Why this improvement matters")
    example: str = Field(..., max_length=300, description="Actionable example")


class AnalysisResponse(BaseModel):
    """Complete analysis response from JobFit AI"""
    match: MatchResult = Field(..., description="Match scores breakdown")
    skills: Dict[str, List[str]] = Field(..., description="Skills found in resume, job, and missing")
    improvements: List[ImprovementsItem] = Field(..., min_length=3, max_length=3, description="Top 3 tailored improvements")
    summary: Optional[str] = Field(
        default=None,
        description="Human-readable summary of the analysis"
    )
    notes: str = Field(
        default="All match scores are in range [0,1] where higher is better. "
                "1.0 = perfect match, 0.0 = no match.",
        description="Additional context about scores"
    )
