
import hashlib
from pathlib import Path

import chromadb
import fitz
from sentence_transformers import SentenceTransformer

from backend.core.config import settings


# ==========================================
# CONFIGURATION
# ==========================================

PDF_FOLDER = Path("data/uploads")

NEW_COLLECTION = "grade9_science_textbooks_multilingual"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

CHUNK_SIZE = 1800
CHUNK_OVERLAP = 300
MIN_CHUNK_SIZE = 100

BATCH_SIZE = 32
DB_BATCH_SIZE = 100


# ==========================================
# FILE HASH (MEMORY FRIENDLY)
# ==========================================

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


# ==========================================
# FIND UNIQUE PDF FILES
# ==========================================

def find_unique_pdfs():
    pdf_files = sorted(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "ไม่พบไฟล์ PDF ใน data/uploads"
        )

    unique_files = {}

    for pdf_path in pdf_files:
        file_hash = calculate_sha256(pdf_path)

        if file_hash not in unique_files:
            unique_files[file_hash] = (
                pdf_path,
                file_hash
            )
        else:
            print(f"[SKIP DUPLICATE] {pdf_path.name}")

    return list(unique_files.values())


# ==========================================
# SPLIT TEXT INTO CHUNKS
# ==========================================

def split_text(text):
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            if len(chunk) < MIN_CHUNK_SIZE:
                if chunks:
                    chunks[-1] += " " + chunk
            else:
                chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


# ==========================================
# EXTRACT PDF CONTENT (STREAMING)
# ==========================================

def iter_pdf_records(pdf_path, file_hash):
    doc = fitz.open(pdf_path)

    try:
        for page_index, page in enumerate(doc):
            page_text = page.get_text("text")

            chunks = split_text(page_text)

            for chunk_index, chunk in enumerate(chunks):
                yield {
                    "id": (
                        f"{file_hash[:16]}_"
                        f"p{page_index + 1}_"
                        f"c{chunk_index + 1}"
                    ),
                    "text": chunk,
                    "metadata": {
                        "source_file": pdf_path.name,
                        "page": page_index + 1,
                        "chunk": chunk_index + 1,
                    }
                }

    finally:
        doc.close()


# ==========================================
# SAVE ONE BATCH
# ==========================================

def save_batch(collection, model, records):
    if not records:
        return

    texts = [item["text"] for item in records]

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    collection.upsert(
        ids=[item["id"] for item in records],
        documents=texts,
        metadatas=[
            item["metadata"] for item in records
        ],
        embeddings=embeddings.tolist()
    )


# ==========================================
# MAIN
# ==========================================

def main():
    print("=" * 60)
    print("SciTutor - Multilingual Database Builder")
    print("=" * 60)

    pdf_files = find_unique_pdfs()

    print(f"\nUnique PDF files: {len(pdf_files)}")

    for pdf_path, file_hash in pdf_files:
        print(f"  - {pdf_path.name}")
        print(f"    SHA256: {file_hash[:16]}...")

    # Load multilingual model
    print("\n[1/4] Loading multilingual embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("[OK] Model loaded")

    # Connect to ChromaDB
    print("\n[2/4] Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=str(settings.chroma_path)
    )

    collection = client.get_or_create_collection(
        name=NEW_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

    print(f"[OK] Collection: {NEW_COLLECTION}")
    print(f"Existing chunks: {collection.count()}")

    # Extract and index
    print("\n[3/4] Extracting PDF and generating embeddings...")

    total_indexed = 0
    batch = []

    for pdf_path, file_hash in pdf_files:
        print(f"\nReading: {pdf_path.name}")

        for record in iter_pdf_records(pdf_path, file_hash):
            batch.append(record)

            if len(batch) >= DB_BATCH_SIZE:
                save_batch(collection, model, batch)

                total_indexed += len(batch)
                print(f"  Processed: {total_indexed}")

                batch.clear()

    # Save remaining records
    if batch:
        save_batch(collection, model, batch)

        total_indexed += len(batch)
        print(f"  Processed: {total_indexed}")

        batch.clear()

    if total_indexed == 0:
        raise RuntimeError(
            "ไม่พบข้อความที่สามารถนำไปทำ Embeddings ได้"
        )

    # Verify
    print("\n[4/4] Verifying database...")

    final_count = collection.count()

    print("\n" + "=" * 60)
    print("DATABASE BUILD COMPLETE!")
    print("=" * 60)

    print("Collection:", NEW_COLLECTION)
    print("Chunks processed:", total_indexed)
    print("Total chunks in collection:", final_count)
    print("Database:", settings.chroma_path)


if __name__ == "__main__":
    main()
