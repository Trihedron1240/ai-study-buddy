"""Utility helpers for generating and comparing text embeddings.

The implementation here purposely keeps the embeddings simple and deterministic
so that the example can run without external services.  It is **not** meant to
produce high‑quality vectors – it merely allows the search endpoint and worker
process to share a common representation.
"""

from __future__ import annotations

import hashlib
import math
from typing import List


DIMENSION = 64  # size of our fake embedding vector


def embed_text(text: str) -> List[float]:
    """Generate a tiny deterministic embedding for ``text``.

    The algorithm hashes every word and distributes the bytes across a fixed
    length vector.  The vector is normalised so that cosine similarity reduces
    to a dot product.
    """

    vec = [0.0] * DIMENSION
    for word in text.lower().split():
        h = hashlib.sha256(word.encode("utf-8")).digest()
        for i, b in enumerate(h):
            vec[i % DIMENSION] += b
    # normalise
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Return cosine similarity between two normalised vectors."""

    if not a or not b:
        return 0.0
    return sum(x * y for x, y in zip(a, b))
