"""Mock embeddings for quick testing without downloading models"""
import numpy as np

_warned = False

def get_model():
    global _warned
    if not _warned:
        print("⚠️  Using MOCK embeddings (install sentence-transformers for real embeddings)")
        _warned = True
    return None

def embed(texts):
    """Return mock embeddings"""
    if isinstance(texts, str):
        texts = [texts]
    # Return random normalized vectors
    return np.random.rand(len(texts), 384).astype(np.float32)

def cosine(a, b) -> float:
    """Return mock cosine similarity"""
    # Return a value between 0.5 and 0.9 for testing
    return float(0.7 + np.random.rand() * 0.2)
