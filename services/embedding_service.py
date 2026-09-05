from fastembed import TextEmbedding

_model = None

def get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _model

def generate_embedding(text):
    return list(get_model().embed([text]))[0]