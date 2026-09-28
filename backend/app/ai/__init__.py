"""AI Module exports."""

from app.ai.attribute_extraction import extract_attributes
from app.ai.technical_rules import evaluate_technical_conflicts, SEVERITY_CRITICAL, SEVERITY_MAJOR
from app.ai.fuzzy_matching import compute_fuzzy_similarity
from app.ai.embeddings import generate_embedding, cosine_similarity
from app.ai.candidate_generation import generate_candidate_pairs

__all__ = [
    "extract_attributes",
    "evaluate_technical_conflicts",
    "compute_fuzzy_similarity",
    "generate_embedding",
    "cosine_similarity",
    "generate_candidate_pairs",
    "SEVERITY_CRITICAL",
    "SEVERITY_MAJOR",
]
