import chromadb
from sentence_transformers import SentenceTransformer

from backend.core.config import settings


# ใช้ตัวแปรร่วม เพื่อไม่ต้องโหลดโมเดลซ้ำทุกครั้ง
_client = None
_collection = None
_model = None

MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def collection():
    global _client, _collection

    if _collection is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_path
        )

        try:
            _collection = _client.get_collection(
                settings.collection
            )
        except Exception as e:
            print(f"[RAG] Collection not found: {e}")
            return None

    return _collection


def embedding_model():
    global _model

    if _model is None:
        print("[RAG] Loading multilingual embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("[RAG] Multilingual model loaded")

    return _model


def retrieve(question, top_k=4):
    c = collection()

    if c is None or c.count() == 0:
        return []

    # สร้าง Query Embedding ด้วยโมเดลเดียวกับตอนสร้างฐานข้อมูล
    model = embedding_model()

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()

    # ค้นหาด้วย Embedding โดยตรง
    r = c.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, c.count()),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    docs = r.get("documents", [[]])[0] or []
    metas = r.get("metadatas", [[]])[0] or []
    distances = r.get("distances", [[]])[0] or []

    results = []

    for i, text in enumerate(docs):
        metadata = metas[i] or {}

        results.append({
            "text": text,
            "source_file": metadata.get(
                "source_file", "ไม่ระบุ"
            ),
            "page": metadata.get(
                "page", "ไม่ระบุ"
            ),
            "distance": (
                distances[i]
                if i < len(distances)
                else None
            )
        })

    return results
