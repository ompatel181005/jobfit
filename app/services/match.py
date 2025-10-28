from typing import Dict
import numpy as np
# Real SBERT embeddings
from .embeddings import embed, cosine


WEIGHTS = {
    "skills": 0.35,
    "responsibilities": 0.2,
    "title": 0.15,
    "semantic": 0.30
}


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / max(1, union)


def component_scores(resume_feats: Dict, job_feats: Dict, resume_text: str, job_text: str):
    s_sk = jaccard(resume_feats.get("skills", []), job_feats.get("skills", []))
    s_rs = jaccard(resume_feats.get("responsibilities", []), job_feats.get("responsibilities", []))
    s_tt = jaccard(resume_feats.get("titles", []), job_feats.get("titles", []))

    e_r, e_j = embed(resume_text)[0], embed(job_text)[0]
    s_sem = max(0.0, min(1.0, (cosine(e_r, e_j) + 1) / 2))  # map [-1,1]→[0,1]

    return {
        "skills": round(s_sk, 4),
        "responsibilities": round(s_rs, 4),
        "title": round(s_tt, 4),
        "semantic": round(s_sem, 4)
    }


def overall_score(components: Dict[str, float]):
    score = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)
    return round(float(score), 4)
