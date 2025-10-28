import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from ..prompts import IMPROVEMENTS_SYSTEM, IMPROVEMENTS_USER_TMPL

# Load environment variables from .env file
load_dotenv()

# Configure Gemini client
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set in environment")

genai.configure(api_key=API_KEY)

# Choose a fast, low-cost model for weekend MVP
# Alternatives: "gemini-1.5-pro" (stronger), "gemini-1.5-flash" (faster/cheaper)
MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

JSON_INSTRUCTIONS = (
    "Return ONLY a JSON array with exactly 3 objects and these fields: "
    "title (<=80 chars), reason (<=300 chars), example (<=300 chars). No extra text."
)


def _extract_json_array(text: str):
    text = text.strip()
    # Try to find a JSON array inside the text (in case of pre/postamble)
    s, e = text.find("["), text.rfind("]")
    if s != -1 and e != -1 and e > s:
        text = text[s:e+1]
    return json.loads(text)


def gen_improvements(resume_text: str, job_text: str, missing_skills: list = None):
    """
    Generate exactly 3 tailored resume improvements using Gemini LLM.
    
    Args:
        resume_text: The candidate's resume text
        job_text: The job description text
        missing_skills: List of skills in job description but not in resume
    """
    missing_skills = missing_skills or []
    try:
        # Build context-aware prompt with missing skills
        skills_context = ""
        if missing_skills:
            skills_context = f"\n\nIMPORTANT - Missing Skills: {', '.join(missing_skills[:10])}\nPrioritize improvements that address these gaps.\n"
        
        prompt = (
            f"System: {IMPROVEMENTS_SYSTEM}\n\n"
            f"{JSON_INSTRUCTIONS}\n"
            f"{skills_context}"
            f"Resume text:\n\n{resume_text[:12000]}\n\n"
            f"Job description:\n\n{job_text[:8000]}\n"
        )

        # Use response_mime_type to strongly bias JSON output
        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=512,
                response_mime_type="application/json",
            ),
        )

        raw = resp.text or "[]"
        data = _extract_json_array(raw)
        items = (data or [])[:3]
        norm = []
        for it in items:
            norm.append({
                "title": str(it.get("title", "Resume Improvement"))[:80].strip(),
                "reason": str(it.get("reason", ""))[:300].strip(),
                "example": str(it.get("example", ""))[:300].strip(),
            })
        while len(norm) < 3:
            norm.append({
                "title": "Tailor Your Resume",
                "reason": "Adjust your resume to better match the job description.",
                "example": "Use keywords from the job posting in your bullet points."
            })
        return norm
    except Exception as e:
        return [
            {"title": "Resume Improvement", "reason": str(e)[:200], "example": "N/A"},
            {"title": "Tailor Your Resume", "reason": "Match keywords from the job posting.", "example": "N/A"},
            {"title": "Quantify Achievements", "reason": "Use numbers to show impact.", "example": "N/A"}
        ]
