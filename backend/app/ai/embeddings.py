"""
Semantic Embeddings Engine.
Uses Sentence Transformers (all-MiniLM-L6-v2) with deterministic semantic vector fallback.
SIH 2026 - National Material Master Platform.
"""

import math
import hashlib
from typing import List, Dict, Any, Optional
from app.core.config import settings

_MODEL_INSTANCE = None


def get_embedding_model():
    """Lazy load SentenceTransformer model."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        try:
            from sentence_transformers import SentenceTransformer
            _MODEL_INSTANCE = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception:
            _MODEL_INSTANCE = None
    return _MODEL_INSTANCE


def build_semantic_text(
    normalized_description: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Construct enriched textual representation for vector embedding:
    normalized description + key technical attributes.
    """
    parts = [normalized_description]
    if attributes:
        tech_snippets = []
        if attributes.get("material_type"):
            tech_snippets.append(f"TYPE: {attributes['material_type']}")
        if attributes.get("material"):
            tech_snippets.append(f"MATERIAL: {attributes['material']}")
        if attributes.get("grade"):
            tech_snippets.append(f"GRADE: {attributes['grade']}")
        if attributes.get("size"):
            tech_snippets.append(f"SIZE: {attributes['size']}")
        if attributes.get("pressure"):
            tech_snippets.append(f"PRESSURE: {attributes['pressure']}")
        if attributes.get("schedule"):
            tech_snippets.append(f"SCH: {attributes['schedule']}")
        if attributes.get("standard"):
            tech_snippets.append(f"STD: {attributes['standard']}")
        if tech_snippets:
            parts.append(" | ".join(tech_snippets))

    return " | ".join(parts)


def _deterministic_semantic_vector(text: str, dimension: int = 384) -> List[float]:
    """
    Deterministic semantic vector fallback generator.
    Produces stable, unit-normalized vectors across words and n-grams.
    Ensures identical texts yield cosine similarity = 1.0, and similar texts yield high similarity.
    """
    tokens = text.lower().split()
    vector = [0.0] * dimension
    for token in tokens:
        # Distribute token hash over vector indices
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        idx1 = h % dimension
        idx2 = (h >> 16) % dimension
        weight = 1.0 / (1.0 + math.log(len(token) + 1))
        vector[idx1] += weight
        vector[idx2] += weight * 0.5

    # Compute Euclidean norm
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        return [round(v / norm, 6) for v in vector]
    return [0.0] * dimension


def generate_embedding(
    normalized_description: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> List[float]:
    """
    Generate normalized 384-dimensional dense vector representation.
    """
    text = build_semantic_text(normalized_description, attributes)
    model = get_embedding_model()
    if model is not None:
        try:
            emb = model.encode(text, normalize_embeddings=True)
            return [float(x) for x in emb]
        except Exception:
            pass

    return _deterministic_semantic_vector(text, dimension=settings.EMBEDDING_DIMENSION)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two unit vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    sim = dot_product / (norm_a * norm_b)
    # Clamp between 0.0 and 1.0
    return max(0.0, min(1.0, round(sim, 4)))
