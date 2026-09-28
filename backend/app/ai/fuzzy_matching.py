"""
Fuzzy Matching Engine using RapidFuzz with Pure-Python Fallbacks.
Computes token_set_ratio, token_sort_ratio, and WRatio.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any
from app.utils.text import normalize_description

try:
    from rapidfuzz import fuzz as rf_fuzz

    def _rf_token_set_ratio(s1: str, s2: str) -> float:
        return float(rf_fuzz.token_set_ratio(s1, s2)) / 100.0

    def _rf_token_sort_ratio(s1: str, s2: str) -> float:
        return float(rf_fuzz.token_sort_ratio(s1, s2)) / 100.0

    def _rf_wratio(s1: str, s2: str) -> float:
        return float(rf_fuzz.WRatio(s1, s2)) / 100.0

    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

    def _levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return _levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

    def _ratio(s1: str, s2: str) -> float:
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0
        dist = _levenshtein_distance(s1, s2)
        total_len = len(s1) + len(s2)
        return max(0.0, 1.0 - (2.0 * dist / total_len))

    def _rf_token_sort_ratio(s1: str, s2: str) -> float:
        t1 = " ".join(sorted(s1.split()))
        t2 = " ".join(sorted(s2.split()))
        return _ratio(t1, t2)

    def _rf_token_set_ratio(s1: str, s2: str) -> float:
        set1 = set(s1.split())
        set2 = set(s2.split())
        intersection = set1.intersection(set2)
        diff1to2 = set1.difference(set2)
        diff2to1 = set2.difference(set1)

        sorted_inter = " ".join(sorted(intersection))
        sorted_1to2 = " ".join(sorted(diff1to2))
        sorted_2to1 = " ".join(sorted(diff2to1))

        combined1 = (sorted_inter + " " + sorted_1to2).strip()
        combined2 = (sorted_inter + " " + sorted_2to1).strip()
        sorted_inter = sorted_inter.strip()

        ratios = [
            _ratio(sorted_inter, combined1) if sorted_inter else 0.0,
            _ratio(sorted_inter, combined2) if sorted_inter else 0.0,
            _ratio(combined1, combined2),
        ]
        return max(ratios)

    def _rf_wratio(s1: str, s2: str) -> float:
        ts = _rf_token_set_ratio(s1, s2)
        tsort = _rf_token_sort_ratio(s1, s2)
        base = _ratio(s1, s2)
        return max(base, ts, tsort)


def compute_fuzzy_similarity(text_a: str, text_b: str) -> Dict[str, Any]:
    """
    Compute comprehensive lexical fuzzy similarity between two material descriptions.
    Uses normalized representation to eliminate formatting noise.
    """
    norm_a = normalize_description(text_a)
    norm_b = normalize_description(text_b)

    if not norm_a or not norm_b:
        return {
            "token_set_ratio": 0.0,
            "token_sort_ratio": 0.0,
            "wratio": 0.0,
            "composite_fuzzy": 0.0,
        }

    ts_score = round(_rf_token_set_ratio(norm_a, norm_b), 4)
    sort_score = round(_rf_token_sort_ratio(norm_a, norm_b), 4)
    w_score = round(_rf_wratio(norm_a, norm_b), 4)

    # Weighted composite fuzzy score: token_set handles supersets/subsets, sort handles reordered words
    composite = round(0.40 * ts_score + 0.30 * sort_score + 0.30 * w_score, 4)

    return {
        "token_set_ratio": ts_score,
        "token_sort_ratio": sort_score,
        "wratio": w_score,
        "composite_fuzzy": composite,
    }
