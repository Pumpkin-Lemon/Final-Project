from pathlib import Path
from backend.services.pdf_service import index_pdf
PDF_DIR=Path(__file__).resolve().parents[1]/"data"/"ipst_pdfs"
def main():
 PDF_DIR.mkdir(parents=True,exist_ok=True);files=sorted(PDF_DIR.glob("*.pdf"))
 if not files:print(f"นำ PDF ไปวางที่ {PDF_DIR}");return
 total=0
 for p in files:
  n=index_pdf(p);total+=n;print(f"{p.name}: {n} chunks")
 print(f"รวม {total} chunks")
if __name__=="__main__":main()
