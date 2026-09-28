from functools import lru_cache

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    # Imported lazily so the rest of the package (and its tests) work without the model.
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def semantic_similarity(text_a: str, text_b: str) -> float:
    from sklearn.metrics.pairwise import cosine_similarity
    model = get_model()
    embeddings = model.encode([text_a, text_b], normalize_embeddings=True)
    return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
