import os
from pathlib import Path
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[2]
load_dotenv(ROOT/".env")
class Settings:
 chroma_path=str((ROOT/os.getenv("CHROMA_DB_PATH","vector_db")).resolve())
 collection=os.getenv("CHROMA_COLLECTION","grade9_science_textbooks")
 origins=[x.strip() for x in os.getenv("FRONTEND_ORIGINS","http://127.0.0.1:5500,http://localhost:5500").split(",") if x.strip()]
 max_upload_mb=max(1,int(os.getenv("MAX_UPLOAD_MB","250")))
 max_upload_bytes=max_upload_mb*1024*1024
 uploads=ROOT/"data"/"uploads"
 survey_file=ROOT/"data"/"survey_feedback.json"
settings=Settings()

