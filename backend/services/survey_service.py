import json
from datetime import datetime,timezone
from backend.core.config import settings
def save(data):
 p=settings.survey_file;p.parent.mkdir(parents=True,exist_ok=True)
 try:rows=json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
 except Exception:rows=[]
 rows.append({**data,"created_at":datetime.now(timezone.utc).isoformat()});p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8");return len(rows)
def summary():
 labels=["ความพึงพอใจ OCR","Socratic Cards","ความพึงพอใจโดยรวม"]
 try:rows=json.loads(settings.survey_file.read_text(encoding="utf-8"))
 except Exception:rows=[]
 keys=["rating_ocr","rating_socratic","rating_overall"]
 vals=[round(sum(r[k] for r in rows)/len(rows),2) if rows else 0 for k in keys]
 return {"labels":labels,"values":vals,"responses":len(rows)}
