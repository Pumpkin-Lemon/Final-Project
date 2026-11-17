import json
import re
import urllib.request
import urllib.error

from pydantic import ValidationError

from backend.models.schemas import AnalyzeResponse
from backend.services.ollama_service import INSTRUCTIONS


LORA_URL = "http://127.0.0.1:8001/generate"


def _call_lora(messages, max_new_tokens=2048):
    payload = {
        "messages": messages,
        "max_new_tokens": max_new_tokens
    }

    request_data = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")

    request = urllib.request.Request(
        LORA_URL,
        data=request_data,
        headers={
            "Content-Type": "application/json; charset=utf-8"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        error_detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"LoRA inference API error ({e.code}): {error_detail}"
        ) from e

    except urllib.error.URLError as e:
        raise RuntimeError(
            f"ไม่สามารถเชื่อมต่อ LoRA inference service ได้: {e.reason}"
        ) from e

    content = result.get("content", "")

    if "</think>" in content:
        content = content.rsplit("</think>", 1)[-1]

    content = re.sub(
        r"<think>.*?</think>",
        "",
        content,
        flags=re.DOTALL
    ).strip()

    if not content:
        raise RuntimeError("LoRA inference service ไม่ได้ส่งคำตอบกลับมา")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"LoRA ส่ง JSON ไม่ถูกต้อง: {e}\n"
            f"คำตอบที่ได้รับ: {content[:1000]}"
        ) from e

    try:
        validated = AnalyzeResponse.model_validate(data)
    except ValidationError as e:
        raise RuntimeError(
            f"LoRA ส่ง JSON ไม่ตรง Response Contract: {e}"
        ) from e

    return validated.model_dump(), content


def _distance_key(item):
    try:
        return float(item.get("distance", float("inf")))
    except (TypeError, ValueError, AttributeError):
        return float("inf")


def answer(question, contexts):
    selected_contexts = []

    for item in contexts or []:
        if not isinstance(item, dict):
            continue

        body = str(item.get("text", "")).strip()
        source_file = item.get("source_file")
        page = item.get("page")

        if not body or source_file is None or page is None:
            continue

        source_file_text = str(source_file).strip()
        page_text = str(page).strip()

        if (
            not source_file_text
            or source_file_text == "ไม่ระบุ"
            or not page_text
            or page_text == "ไม่ระบุ"
        ):
            continue

        selected_contexts.append(item)

    ordered_contexts = sorted(selected_contexts, key=_distance_key)

    context_parts = []

    for index, item in enumerate(ordered_contexts, 1):
        body = str(item.get("text", "")).strip()

        if not body:
            continue

        context_parts.append(
            f"[เอกสารอ้างอิง {index}]\n"
            f"ไฟล์ {item.get('source_file')} หน้า {item.get('page')}\n"
            f"{body}\n"
            f"[/เอกสารอ้างอิง {index}]"
        )

    context = "\n\n".join(context_parts) or "ไม่พบเนื้อหาในฐานข้อมูล PDF"

    messages = [
        {
            "role": "system",
            "content": INSTRUCTIONS
        },
        {
            "role": "user",
            "content": (
                f"โจทย์: {question}\n\n"
                f"บริบทจาก PDF:\n{context}"
            )
        }
    ]

    # รอบแรก: สร้างคำตอบตาม Response Contract
    data, original_content = _call_lora(messages)

    # รอบเสริม: สร้างเฉพาะส่วนการเรียนรู้ที่ขาด
    # ไม่ทำงานเมื่อไม่มีบริบท หรือคำตอบระบุว่าไม่พบข้อมูล
    missing_parts = []

    if not data["socraticCards"]:
        missing_parts.append(
            "- socraticCards: สร้างคำถามชวนคิดอย่างน้อย 2 ข้อ "
            "แต่ละข้อมี question, hint และ checkpoint"
        )

    if not data["steps"]:
        missing_parts.append(
            "- steps: สร้างขั้นตอนอธิบายความเข้าใจ 2-4 ขั้น "
            "แต่ละขั้นมี title และ detail"
        )

    not_found = (
        "ไม่พบข้อมูลที่เกี่ยวข้องกับคำถามนี้ในเอกสาร PDF"
        in data["answer"]
    )

    if missing_parts and ordered_contexts and not not_found:
        retry_instruction = (
            "โปรดปรับปรุง JSON ที่คุณตอบไปก่อนหน้า "
            "โดยเติมเฉพาะฟิลด์ที่ยังว่างตามรายการนี้:\n"
            + "\n".join(missing_parts)
            + "\n\n"
            "ข้อกำหนดสำคัญ:\n"
            "1. ใช้เฉพาะหลักฐานจากบริบท PDF ในข้อความก่อนหน้า\n"
            "2. ห้ามแต่งข้อเท็จจริง ตัวเลข สูตร หรือเนื้อหาที่ไม่มีหลักฐาน\n"
            "3. คำถามชวนคิดต้องเกี่ยวข้องกับโจทย์โดยตรง "
            "และต้องมีคำใบ้พร้อมจุดตรวจสอบความเข้าใจ\n"
            "4. ขั้นตอนต้องเรียงลำดับให้ผู้เรียนเข้าใจเนื้อหาได้ง่าย\n"
            "5. หากหลักฐานไม่เพียงพอจริง ๆ ให้คงฟิลด์นั้นเป็น []\n"
            "6. รักษา answer, vars และ pdfRef จากคำตอบเดิมทุกประการ\n"
            "7. ส่งกลับเป็น JSON Object ที่มี Key ทั้ง 5 รายการเท่านั้น "
            "ห้ามมี Markdown หรือข้อความอื่น"
        )

        retry_messages = messages + [
            {
                "role": "assistant",
                "content": original_content
            },
            {
                "role": "user",
                "content": retry_instruction
            }
        ]

        try:
            retry_data, _ = _call_lora(
                retry_messages,
                max_new_tokens=2048
            )

            # รับเฉพาะส่วนที่ขาด ไม่เขียนทับคำตอบหลัก
            if not data["socraticCards"] and retry_data["socraticCards"]:
                data["socraticCards"] = retry_data["socraticCards"]

            if not data["steps"] and retry_data["steps"]:
                data["steps"] = retry_data["steps"]

        except Exception as e:
            # รอบเสริมล้มเหลว ให้ใช้คำตอบรอบแรกต่อไป
            print(
                f"[LoRA] Supplementary generation skipped: {e}",
                flush=True
            )

    citations = []
    seen = set()

    for item in ordered_contexts:
        source_file = item.get("source_file")
        page = item.get("page")

        if source_file is None or page is None:
            continue

        citation_key = (source_file, page)

        if citation_key not in seen:
            citations.append({
                "source_file": source_file,
                "page": page
            })
            seen.add(citation_key)

    data["citations"] = citations

    if citations:
        data["pdfRef"] = "; ".join(
            f"หน้า {item['page']}"
            for item in citations
        )
    else:
        data["pdfRef"] = "ไม่พบแหล่งอ้างอิง"

    return data
