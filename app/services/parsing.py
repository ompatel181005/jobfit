import re
from typing import Tuple
from PyPDF2 import PdfReader


TECH_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c", "c#", "go", "rust",
    "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "perl", "shell",
    "bash", "powershell", "lua", "dart", "elixir", "haskell", "objective-c",
    
    # AI/ML Frameworks & Libraries
    "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
    "scipy", "opencv", "yolo", "deepsort", "transformers", "huggingface", "langchain",
    "llama", "gpt", "bert", "fastai", "xgboost", "lightgbm", "catboost",
    "spacy", "nltk", "gensim", "mlflow", "wandb", "tensorboard",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "ansible",
    "jenkins", "gitlab", "github", "circleci", "travis", "helm", "istio",
    "prometheus", "grafana", "datadog", "cloudformation", "ecs", "eks", "lambda",
    
    # Databases
    "sql", "postgres", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "snowflake", "bigquery", "redshift", "neo4j",
    "sqlite", "mariadb", "oracle", "mssql", "couchbase", "influxdb",
    
    # Web Frameworks & Tools
    "fastapi", "flask", "django", "react", "vue", "angular", "nodejs", "node.js",
    "express", "nextjs", "next.js", "gatsby", "svelte", "spring", "springboot",
    "rails", "laravel", "asp.net", "graphql", "rest", "grpc",
    
    # Data Engineering & Processing
    "spark", "pyspark", "kafka", "airflow", "hadoop", "hive", "presto", "flink",
    "beam", "dbt", "dagster", "prefect", "luigi", "nifi", "storm",
    
    # Computer Vision & Robotics
    "onnx", "cuda", "cudnn", "tensorrt", "jetson", "ros", "gazebo", "pcl",
    "mediapipe", "dlib", "pillow", "matplotlib", "seaborn", "plotly",
    
    # Version Control & Collaboration
    "git", "svn", "mercurial", "jira", "confluence", "slack", "notion",
    
    # Testing & Quality
    "pytest", "unittest", "jest", "mocha", "selenium", "cypress", "junit",
    "testng", "cucumber", "postman", "swagger", "openapi",
    
    # OS & Systems
    "linux", "unix", "ubuntu", "centos", "debian", "macos", "windows",
    
    # Other Tools & Technologies
    "api", "microservices", "serverless", "ci/cd", "agile", "scrum", "devops",
    "mlops", "etl", "tableau", "powerbi", "looker", "streamlit", "gradio"
]


RESPONSIBILITY_HINTS = [
    "design", "implement", "optimize", "deploy", "scale", "monitor",
    "mentor", "collaborate", "research", "prototype", "maintain",
    "test", "automate", "document"
]


TITLE_HINTS = ["engineer", "software", "ml", "ai", "research", "data", "backend", "full stack"]


WORD = re.compile(r"[a-zA-Z][a-zA-Z0-9+.#-]{1,}")


def extract_pdf_text(pdf_bytes) -> str:
    reader = PdfReader(pdf_bytes)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def simple_skill_extract(text: str):
    nt = normalize(text)
    found = set()
    for s in TECH_SKILLS:
        if f" {s} " in f" {nt} ":
            found.add(s)
    return sorted(found)


def simple_resp_extract(text: str):
    nt = normalize(text)
    return sorted({w for w in RESPONSIBILITY_HINTS if f" {w} " in f" {nt} "})


def simple_title_extract(text: str):
    nt = normalize(text)
    # grab top 5 tokens that match title hints
    hits = [w for w in WORD.findall(nt) if w in TITLE_HINTS]
    return sorted(set(hits))[:5]


def extract_all(resume_text: str, job_text: str) -> Tuple[dict, dict, dict]:
    r_sk = simple_skill_extract(resume_text)
    j_sk = simple_skill_extract(job_text)
    r_rs = simple_resp_extract(resume_text)
    j_rs = simple_resp_extract(job_text)
    r_tt = simple_title_extract(resume_text)
    j_tt = simple_title_extract(job_text)
    return (
        {"skills": r_sk, "responsibilities": r_rs, "titles": r_tt},
        {"skills": j_sk, "responsibilities": j_rs, "titles": j_tt},
        {"missing_skills": sorted([s for s in j_sk if s not in r_sk])}
    )
