
import chromadb
from sentence_transformers import SentenceTransformer
from backend.core.config import settings

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "grade9_science_textbooks_multilingual"

model = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(
    path=str(settings.chroma_path)
)

collection = client.get_collection(COLLECTION_NAME)

questions = [
    "การโยนเหรียญบาทเพื่อศึกษาพันธุศาสตร์ทำอย่างไร",
    "จีโนไทป์และฟีโนไทป์แตกต่างกันอย่างไร",
    "อัตราส่วนจีโนไทป์ของลูกจากการผสมพันธุ์เป็นเท่าใด",
    "สิ่งใดเป็นตัวกำหนดฟีโนไทป์ของสิ่งมีชีวิต"
]

print("Collection:", COLLECTION_NAME)
print("Total chunks:", collection.count())

# ตรวจสอบว่าข้อความสำคัญจาก PDF ถูกจัดเก็บหรือไม่
print("\n========== CONTENT CHECK ==========")

all_data = collection.get(
    include=["documents", "metadatas"]
)

keywords = ["จีโนไทป์", "ฟีโนไทป์", "เหรียญ"]

for keyword in keywords:
    print(f"\nKeyword: {keyword}")
    found = 0

    for i, document in enumerate(all_data["documents"]):
        if keyword in document:
            metadata = all_data["metadatas"][i]
            print(
                "Page:", metadata.get("page"),
                "| Chunk:", metadata.get("chunk")
            )
            print("Text:", document[:500])
            found += 1

            if found >= 3:
                break

    if found == 0:
        print("NOT FOUND")

# ทดสอบ semantic search
print("\n========== SEMANTIC SEARCH ==========")

for question in questions:
    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    )

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=10,
        include=["documents", "metadatas", "distances"]
    )

    print("\n" + "=" * 70)
    print("QUESTION:", question)
    print("=" * 70)

    for i, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        print(f"\nResult {i + 1}")
        print("Page:", metadata.get("page"))
        print("Distance:", round(distance, 4))
        print("Similarity:", round(1 - distance, 4))
        print("Text:", document[:700])

print("\n========== TARGET PAGE INSPECTION ==========")

for page_number in [109, 110]:
    results = collection.get(
        where={"page": page_number},
        include=["documents", "metadatas"]
    )

    print(f"\n========== PDF PAGE {page_number} ==========")

    for i, document in enumerate(results["documents"]):
        print(f"\n--- CHUNK {i + 1} ---")
        print(document)