from backend.utils.text_chunker import chunk_text
def test_chunk_text():
 chunks=chunk_text("ก"*5000,1000,100)
 assert len(chunks)>1
 assert all(chunks)
