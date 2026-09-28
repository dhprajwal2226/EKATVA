"""
Candidate Generation and Blocking Engine.
Prevents O(N²) quadratic comparison using indexing, domain blocking,
and vector similarity pruning.
SIH 2026 - National Material Master Platform.
"""

from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.ai.embeddings import cosine_similarity


def generate_candidate_pairs(
    source_material: Any,
    candidate_pool: List[Any],
    top_k: int = 25,
) -> List[Tuple[Any, float]]:
    """
    Filter candidate materials for a source material using blocking rules:
    1. Blocking on Material Type & Category
    2. Vector embedding nearest-neighbor similarity
    3. Lexical token overlap

    Returns: List of tuples (target_material, preliminary_score) sorted descending by score.
    """
    candidates_with_scores: List[Tuple[Any, float]] = []

    src_type = (source_material.attributes.material_type or "").upper() if source_material.attributes else ""
    src_mat = (source_material.attributes.material or "").upper() if source_material.attributes else ""
    src_tokens = set((source_material.normalized_description or "").split())
    src_vec = source_material.embedding.embedding if source_material.embedding else None

    for target in candidate_pool:
        # Exclude self
        if target.id == source_material.id:
            continue

        tgt_type = (target.attributes.material_type or "").upper() if target.attributes else ""
        tgt_mat = (target.attributes.material or "").upper() if target.attributes else ""
        tgt_tokens = set((target.normalized_description or "").split())
        tgt_vec = target.embedding.embedding if target.embedding else None

        # BLOCKING RULE 1: If both have clear, incompatible material types (e.g. Cable vs Pipe), skip immediately
        if src_type and tgt_type and src_type != tgt_type:
            # Different primary types cannot be identical
            continue

        # Preliminary scoring
        # 1. Token Jaccard overlap
        token_overlap = 0.0
        if src_tokens and tgt_tokens:
            union_len = len(src_tokens.union(tgt_tokens))
            if union_len > 0:
                token_overlap = len(src_tokens.intersection(tgt_tokens)) / union_len

        # 2. Vector similarity if available
        vec_sim = 0.0
        if src_vec and tgt_vec:
            vec_sim = cosine_similarity(src_vec, tgt_vec)

        # 3. Domain attribute bonus
        attr_bonus = 0.0
        if src_type and tgt_type and src_type == tgt_type:
            attr_bonus += 0.20
        if src_mat and tgt_mat and src_mat == tgt_mat:
            attr_bonus += 0.20

        prelim_score = max(vec_sim, token_overlap) * 0.6 + attr_bonus

        # Only retain candidates exceeding minimum pre-filter score
        if prelim_score >= settings.MIN_CANDIDATE_SCORE or token_overlap > 0.15 or vec_sim > 0.40:
            candidates_with_scores.append((target, prelim_score))

    # Sort descending by preliminary score and return Top-K
    candidates_with_scores.sort(key=lambda x: x[1], reverse=True)
    return candidates_with_scores[:top_k]
