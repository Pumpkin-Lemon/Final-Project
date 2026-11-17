from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

from backend.models.schemas import AnalyzeRequest, AnalyzeResponse, SurveyRequest
from backend.services.rag_service import retrieve
from backend.services.lora_service import answer
from backend.services.pdf_service import index_pdf
from backend.services.survey_service import save, summary
from backend.core.config import settings



class CitationItem(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    source_file: str = Field(min_length=1)
    page: int | str


class AnalyzeAPIResponse(AnalyzeResponse):
    status: Literal["success"]
    citations: list[CitationItem]


router = APIRouter()
UPLOAD_CHUNK_SIZE = 1024 * 1024  # อ่านและเขียนครั้งละ 1 MB เพื่อลดการใช้ RAM


@router.post("/analyze-with-pdf-rag", response_model=AnalyzeAPIResponse)
def analyze(req: AnalyzeRequest):
    try:
        return {"status": "success", **answer(req.question, retrieve(req.question))}
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(502, f"ประมวลผลด้วยโมเดล AI ไม่สำเร็จ: {e}")


@router.post("/index-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "รองรับเฉพาะ PDF")

    # รองรับทั้ง path separator ของ Windows และ Linux โดยเก็บเฉพาะชื่อไฟล์
    safe_filename = Path(file.filename.replace("\\", "/")).name
    if not safe_filename or safe_filename in {".", ".."}:
        raise HTTPException(400, "ชื่อไฟล์ PDF ไม่ถูกต้อง")

    settings.uploads.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid4().hex}_{safe_filename}"
    destination = settings.uploads / unique_name
    temporary = settings.uploads / f"{unique_name}.part"
    total_bytes = 0
    first_chunk = True

    try:
        with temporary.open("wb") as output:
            while True:
                chunk = await file.read(UPLOAD_CHUNK_SIZE)
                if not chunk:
                    break

                total_bytes += len(chunk)
                if total_bytes > settings.max_upload_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"ไฟล์เกิน {settings.max_upload_mb} MB",
                    )

                if first_chunk:
                    first_chunk = False
                    if not chunk.startswith(b"%PDF"):
                        raise HTTPException(400, "ไฟล์ PDF ไม่ถูกต้อง")

                output.write(chunk)

        if total_bytes == 0:
            raise HTTPException(400, "ไฟล์ PDF ว่างเปล่า")

        temporary.replace(destination)

    except HTTPException:
        temporary.unlink(missing_ok=True)
        raise
    except Exception as e:
        temporary.unlink(missing_ok=True)
        raise HTTPException(500, f"บันทึกไฟล์ PDF ไม่สำเร็จ: {e}") from e
    finally:
        await file.close()

    try:
        chunks_indexed = index_pdf(destination)
    except Exception as e:
        raise HTTPException(500, f"จัดทำดัชนี PDF ไม่สำเร็จ: {e}") from e

    return {
        "status": "indexed",
        "filename": safe_filename,
        "stored_filename": destination.name,
        "file_size_mb": round(total_bytes / (1024 * 1024), 2),
        "max_upload_mb": settings.max_upload_mb,
        "chunks_indexed": chunks_indexed,
    }


@router.post("/survey")
def survey(req: SurveyRequest):
    return {"status": "saved", "responses": save(req.model_dump())}


@router.get("/survey/summary")
def survey_summary():
    return summary()
