import io
import os
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from typing import Optional
import logging

from .models import AnalysisResponse, MatchComponents, MatchResult
from .services.parsing import extract_pdf_text, extract_all
from .services.match import component_scores, overall_score
from .services.improvements import gen_improvements

app = FastAPI(default_response_class=ORJSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile,
    job_text: Optional[str] = Form(default=None),
    job_url: Optional[str] = Form(default=None),
):
    # Validate file size (max 10MB)
    MAX_PDF_SIZE = 10 * 1024 * 1024
    resume_bytes = await resume.read()
    if len(resume_bytes) > MAX_PDF_SIZE:
        raise HTTPException(status_code=400, detail="PDF file too large. Maximum size is 10MB.")
    
    logger.info(f"Analyzing resume: {resume.filename}, size: {len(resume_bytes)} bytes")
    
    try:
        # 1) Ingest résumé
        pdf_bytes = io.BytesIO(resume_bytes)
        resume_text = extract_pdf_text(pdf_bytes)
        if not resume_text.strip():
            resume_text = "(No text extracted — is this a scanned PDF?)"

        # 2) Ingest job (text first; URL parsing optional user extension)
        if not job_text and not job_url:
            job_text = "Software engineer with Python, FastAPI, Docker, AWS. Bonus: Kafka, Kubernetes."

        if job_url and not job_text:
            # Minimal URL fetch; user can extend to robust scraping
            import requests
            from bs4 import BeautifulSoup
            try:
                html = requests.get(job_url, timeout=10).text
                job_text = BeautifulSoup(html, "html.parser").get_text(" ")[:20000]
            except Exception:
                job_text = ""

        job_text = (job_text or "").strip()

        # 3) Extract features from both texts (Agent 1: Extraction)
        resume_feats, job_feats, skills_gap = extract_all(resume_text, job_text)

        # 4) Calculate match components (Agent 2: Matching with embeddings)
        components = component_scores(resume_feats, job_feats, resume_text, job_text)
        score = overall_score(components)

        # 5) Generate improvements (Agent 3: LLM-based recommendations)
        improvements = gen_improvements(resume_text, job_text, skills_gap.get("missing_skills", []))

        # 6) Build response

        # 7) Generate human-readable summary
        match_percent = int(score * 100)
        missing_count = len(skills_gap.get("missing_skills", []))
        summary_parts = [f"Your resume matches {match_percent}% of the job posting."]
        
        if missing_count > 0:
            top_missing = skills_gap.get("missing_skills", [])[:3]
            summary_parts.append(f"Consider adding experience with: {', '.join(top_missing)}.")
        
        if score >= 0.75:
            summary_parts.append("Strong match! Your profile aligns well with this role.")
        elif score >= 0.50:
            summary_parts.append("Good foundation. Focus on the suggested improvements to strengthen your application.")
        else:
            summary_parts.append("Significant gaps identified. Review improvements carefully to boost your match score.")
        
        summary = " ".join(summary_parts)
        
        return AnalysisResponse(
            match=MatchResult(
                score=score,
                components=MatchComponents(**components)
            ),
            skills={
                "resume": resume_feats.get("skills", []),
                "job": job_feats.get("skills", []),
                "missing": skills_gap.get("missing_skills", [])
            },
            improvements=improvements,
            summary=summary
        )
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        logger.info("Analysis completed")
