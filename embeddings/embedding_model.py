from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

# Load model globally to avoid reloading on every call
model = SentenceTransformer(EMBEDDING_MODEL)

def get_embedding(text):
    """
    Returns the vector embedding for the given text.
    """
    if not text:
        return []
    return model.encode(text).tolist()

def get_embeddings_batch(texts):
    """
    Returns vector embeddings for a list of texts.
    """
    return model.encode(texts).tolist()
