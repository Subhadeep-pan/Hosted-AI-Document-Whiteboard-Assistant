from sentence_transformers import SentenceTransformer

_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device="cpu"
        )

    return _model


def create_embeddings(chunks):
    model = get_model()

    return model.encode(
        chunks,
        batch_size=16,
        show_progress_bar=False,
        convert_to_numpy=True
    )


def create_query_embedding(question):
    model = get_model()

    return model.encode(
        question,
        show_progress_bar=False,
        convert_to_numpy=True
    )