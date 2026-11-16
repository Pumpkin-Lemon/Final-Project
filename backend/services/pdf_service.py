from pathlib import Path

import chromadb
import fitz

from backend.core.config import settings

INDEX_BATCH_SIZE = 500
CHUNK_SIZE = 1800
CHUNK_STEP = 1500


def index_pdf(path: Path) -> int:
    """Extract PDF text and upsert it in batches to limit peak memory use."""
    client = chromadb.PersistentClient(path=settings.chroma_path)
    collection = client.get_or_create_collection(settings.collection)

    doc = fitz.open(path)
    batch_ids: list[str] = []
    batch_texts: list[str] = []
    batch_metadatas: list[dict] = []
    total_indexed = 0

    def flush_batch() -> None:
        nonlocal total_indexed
        if not batch_ids:
            return
        collection.upsert(
            ids=batch_ids,
            documents=batch_texts,
            metadatas=batch_metadatas,
        )
        total_indexed += len(batch_ids)
        batch_ids.clear()
        batch_texts.clear()
        batch_metadatas.clear()

    try:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if len(text) < 30:
                continue

            for chunk_number, start in enumerate(range(0, len(text), CHUNK_STEP)):
                chunk_text = text[start : start + CHUNK_SIZE]
                if not chunk_text.strip():
                    continue

                batch_ids.append(f"{path.stem}_p{page_number}_c{chunk_number}")
                batch_texts.append(chunk_text)
                batch_metadatas.append(
                    {
                        "source_file": path.name,
                        "page": page_number,
                        "chunk": chunk_number,
                        "book_type": "IPST Grade 9 Science",
                    }
                )

                if len(batch_ids) >= INDEX_BATCH_SIZE:
                    flush_batch()

        flush_batch()
    finally:
        doc.close()

    return total_indexed
