"""Structured job profile for the released JD plus the skill ontology.

The JD is "Senior AI Engineer - Founding Team" at Redrob AI. It is deliberately
written to defeat keyword matching: the right candidate reasons about the gap
between what the JD *says* and what it *means*. This module encodes that
understanding as a structured, machine-usable profile.

Everything here is derived from job_description.docx (Phase 2). Keeping it as a
single source of truth lets the ranker, the explainer and the dashboard agree.
"""
from __future__ import annotations

from typing import Dict, List, Set

# --------------------------------------------------------------------------- #
# Skill ontology - canonical concept -> surface forms (lowercased)            #
# --------------------------------------------------------------------------- #
SKILL_ONTOLOGY: Dict[str, List[str]] = {
    # Core retrieval / embeddings stack (the heart of the role)
    "embeddings": [
        "embeddings", "embedding", "sentence-transformers", "sentence transformers",
        "sbert", "openai embeddings", "bge", "e5", "word2vec", "fasttext",
        "vector embeddings", "text embeddings",
    ],
    "retrieval": [
        "retrieval", "semantic search", "rag", "retrieval augmented generation",
        "information retrieval", "ir", "hybrid search", "bm25", "dense retrieval",
        "neural search", "vector search",
    ],
    "vector_db": [
        "faiss", "pinecone", "weaviate", "qdrant", "milvus", "opensearch",
        "elasticsearch", "elastic search", "vespa", "annoy", "hnsw", "vector database",
        "vector db", "chroma", "pgvector",
    ],
    "ranking": [
        "ranking", "learning to rank", "learning-to-rank", "ltr", "recommendation",
        "recommender", "recommendation system", "recsys", "re-ranking", "reranking",
        "search ranking", "relevance",
    ],
    "ml_evaluation": [
        "ndcg", "mrr", "map", "mean average precision", "a/b testing", "ab testing",
        "offline evaluation", "online evaluation", "evaluation framework", "precision",
        "recall", "f1", "auc", "model evaluation",
    ],
    "nlp": [
        "nlp", "natural language processing", "text classification", "ner",
        "named entity recognition", "transformers", "bert", "language models",
        "text mining", "tokenization", "topic modeling",
    ],
    "llm": [
        "llm", "large language models", "gpt", "llama", "mistral", "prompt engineering",
        "fine-tuning llms", "fine tuning", "instruction tuning", "rlhf",
    ],
    "llm_finetune": [
        "lora", "qlora", "peft", "fine-tuning", "fine tuning", "fine-tune",
        "parameter efficient fine-tuning", "supervised fine-tuning", "sft",
    ],
    "ml_core": [
        "machine learning", "deep learning", "ml", "pytorch", "tensorflow", "keras",
        "scikit-learn", "sklearn", "xgboost", "lightgbm", "gradient boosting",
        "neural networks", "mlops", "model training", "feature engineering",
    ],
    "python": ["python", "pandas", "numpy", "fastapi", "flask"],
    "data_eng": [
        "spark", "pyspark", "airflow", "kafka", "dbt", "snowflake", "data pipeline",
        "etl", "data engineering", "warehouse",
    ],
    "distributed": [
        "distributed systems", "kubernetes", "k8s", "docker", "microservices",
        "inference optimization", "large-scale inference", "scalability",
    ],
    "hrtech": [
        "hr-tech", "hrtech", "recruiting", "recruitment", "talent", "marketplace",
        "ats", "candidate matching",
    ],
    # ----- Negative / mismatch domains (CV/speech/robotics without NLP) ----- #
    "cv_speech_robotics": [
        "computer vision", "image classification", "object detection", "segmentation",
        "ocr", "speech recognition", "asr", "tts", "text to speech", "robotics",
        "slam", "lidar", "pose estimation", "face recognition", "opencv", "yolo",
    ],
}

# Must-have concepts ("Things you absolutely need")
REQUIRED_CONCEPTS: List[str] = [
    "embeddings", "retrieval", "vector_db", "ranking", "ml_evaluation", "python", "nlp",
]

# Nice-to-have concepts ("Things we'd like you to have but won't reject you for")
PREFERRED_CONCEPTS: List[str] = [
    "llm_finetune", "llm", "ml_core", "distributed", "hrtech",
]

# Concept weights inside the skill-match score
CONCEPT_WEIGHTS: Dict[str, float] = {
    "embeddings": 1.5,
    "retrieval": 1.5,
    "vector_db": 1.3,
    "ranking": 1.4,
    "ml_evaluation": 1.2,
    "nlp": 1.0,
    "python": 0.8,
    "ml_core": 1.0,
    "llm_finetune": 0.7,
    "llm": 0.6,
    "distributed": 0.5,
    "hrtech": 0.5,
}

# --------------------------------------------------------------------------- #
# Experience expectations                                                      #
# --------------------------------------------------------------------------- #
EXPERIENCE = {
    "min_years": 5.0,
    "max_years": 9.0,
    "ideal_low": 6.0,
    "ideal_high": 8.0,
    "hard_floor": 3.0,   # below this, judgement bar is very high
    "hard_ceiling": 15.0,
}

# --------------------------------------------------------------------------- #
# Location preferences (India product-hub cities). Relocation willingness      #
# substitutes for an exact city match.                                         #
# --------------------------------------------------------------------------- #
PREFERRED_LOCATIONS: List[str] = [
    "pune", "noida", "hyderabad", "mumbai", "delhi", "ncr", "gurgaon", "gurugram",
    "bengaluru", "bangalore",
]
PREFERRED_COUNTRY = "india"

# --------------------------------------------------------------------------- #
# Title classification - the decisive anti-keyword-stuffer signal.            #
# --------------------------------------------------------------------------- #
AI_TITLE_TERMS: List[str] = [
    "ai engineer", "ml engineer", "machine learning", "applied scientist",
    "applied ml", "research engineer", "data scientist", "nlp engineer",
    "search engineer", "ranking engineer", "recommendation", "deep learning",
    "ai/ml", "ml ops", "mlops",
]
ADJACENT_TECH_TITLE_TERMS: List[str] = [
    "software engineer", "backend engineer", "data engineer", "platform engineer",
    "fullstack", "full stack", "full-stack", "staff engineer", "principal engineer",
    "engineering manager", "tech lead", "sde", "developer", "architect",
]
NON_TECH_TITLE_TERMS: List[str] = [
    "hr manager", "human resources", "marketing manager", "sales executive",
    "accountant", "graphic designer", "content writer", "civil engineer",
    "mechanical engineer", "customer support", "operations manager",
    "project manager", "business analyst", "recruiter", "designer", "copywriter",
]

# Known IT-services / consulting firms (penalized when they make up the *entire*
# career history, per the JD's explicit "do not want" list).
CONSULTING_FIRMS: Set[str] = {
    "tcs", "tata consultancy services", "infosys", "wipro", "accenture",
    "cognizant", "capgemini", "hcl", "hcl technologies", "tech mahindra",
    "mindtree", "ltimindtree", "lti", "larsen & toubro infotech", "mphasis",
    "dxc", "dxc technology", "hexaware", "persistent", "persistent systems",
    "birlasoft", "coforge", "ibm services", "deloitte", "kpmg", "pwc", "ey",
    "ernst & young", "zensar", "mastech", "syntel", "igate", "virtusa",
}

# Research-only signals (academic / research without production deployment).
RESEARCH_TERMS: List[str] = [
    "research scientist", "research fellow", "postdoc", "post-doctoral",
    "phd researcher", "research assistant", "professor", "lecturer", "academic",
]
RESEARCH_INDUSTRIES: List[str] = ["education", "research", "academia", "university"]

# Free-text the embedding model encodes as the "ideal candidate".
JD_SUMMARY_TEXT = (
    "Senior AI Engineer for a Series A AI-native talent intelligence platform. "
    "Owns the intelligence layer: ranking, retrieval and matching systems. "
    "Production experience with embeddings-based retrieval (sentence-transformers, "
    "OpenAI embeddings, BGE, E5) deployed to real users, handling embedding drift, "
    "index refresh and retrieval-quality regression. Production experience with "
    "vector databases or hybrid search (Pinecone, Weaviate, Qdrant, Milvus, "
    "OpenSearch, Elasticsearch, FAISS). Strong Python and code quality. Hands-on "
    "designing evaluation frameworks for ranking systems: NDCG, MRR, MAP, "
    "offline-to-online correlation, A/B test interpretation. Has shipped at least "
    "one end-to-end ranking, search or recommendation system to real users at "
    "scale at a product company (not pure services). Six to eight years total "
    "experience, four to five in applied ML/AI at product companies. Scrappy "
    "product-engineering attitude, ships fast, writes well, based in or willing to "
    "relocate to Noida or Pune. Not a title-chaser, not research-only, not "
    "consulting-only, not a framework enthusiast, not computer-vision/speech/"
    "robotics without NLP."
)


def structured_profile() -> Dict:
    """Return the JD as a structured, serializable profile (Phase 2 output)."""
    return {
        "role_title": "Senior AI Engineer - Founding Team",
        "company": "Redrob AI",
        "company_stage": "Series A (AI-native talent intelligence)",
        "locations": ["Pune", "Noida", "Hyderabad", "Mumbai", "Delhi NCR"],
        "employment_type": "Full-time (Hybrid)",
        "experience": EXPERIENCE,
        "required_skills": REQUIRED_CONCEPTS,
        "preferred_skills": PREFERRED_CONCEPTS,
        "education_requirements": (
            "No hard degree requirement; CS/ML background helps but plain-language "
            "candidates with real production ML experience are explicitly welcome."
        ),
        "domain_requirements": [
            "embeddings-based retrieval in production",
            "vector databases / hybrid search",
            "ranking / search / recommendation systems shipped to real users",
            "evaluation frameworks (NDCG, MRR, MAP, A/B testing)",
            "product companies over pure services",
        ],
        "soft_skills": [
            "scrappy product-engineering attitude",
            "ships fast, iterates from real users",
            "strong written communication (async-first)",
            "disagree openly, decide quickly",
            "3+ year commitment (not a title-chaser)",
        ],
        "disqualifiers": [
            "pure research / no production deployment",
            "AI experience only recent LangChain-on-OpenAI (<12 months)",
            "senior who hasn't written production code in 18 months",
            "title-chasers (company switch every ~1.5 years)",
            "framework enthusiasts over systems thinkers",
            "consulting-firm-only careers",
            "computer-vision/speech/robotics without NLP/IR",
            "closed-source-only for 5+ years with no external validation",
        ],
        "summary_text": JD_SUMMARY_TEXT,
    }
