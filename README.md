# SciLearn & Practice

SciLearn & Practice เป็นเว็บแอปพลิเคชันสำหรับช่วยอธิบายและแก้โจทย์วิทยาศาสตร์ระดับชั้นมัธยมศึกษาปีที่ 3 โดยใช้เทคนิค Retrieval-Augmented Generation (RAG) เพื่อค้นหาข้อมูลจากเอกสาร PDF ที่จัดเก็บไว้ในฐานข้อมูล ก่อนนำบริบทที่เกี่ยวข้องไปประกอบการสร้างคำตอบด้วยโมเดล Qwen3-4B ที่ปรับแต่งด้วย LoRA

ระบบประกอบด้วย Frontend สำหรับรับโจทย์และแสดงผล Backend ที่พัฒนาด้วย FastAPI ระบบค้นคืนข้อมูลจาก ChromaDB และ LoRA Inference Server ซึ่งทำงานแยกจาก Environment ของ Backend

ผลลัพธ์ประกอบด้วยคำอธิบาย ตัวแปรที่เกี่ยวข้อง คำถามชวนคิด ขั้นตอนการแก้โจทย์ และข้อมูลอ้างอิงจากเอกสาร PDF

## Features

- **AI-powered Science Tutoring:** ช่วยอธิบายโจทย์วิทยาศาสตร์เป็นภาษาไทย เหมาะสำหรับนักเรียนระดับ ม.3
- **PDF-based RAG:** ค้นคืนเนื้อหาจากเอกสาร PDF ที่จัดเก็บใน ChromaDB
- **Multilingual Embedding:** ใช้ Sentence Transformers รุ่น `paraphrase-multilingual-MiniLM-L12-v2` สำหรับสร้าง Embeddings
- **LLM Integration:** ใช้โมเดล `Qwen3-4B` ที่ปรับแต่งด้วย LoRA Adapter เป็นโมเดลหลักในการสร้างคำตอบ
- **Structured Responses:** ส่งผลลัพธ์ในรูปแบบ JSON ตาม Response Contract
- **Image Preview:** รองรับการเลือกรูปภาพและแสดงตัวอย่างก่อนส่งคำถาม แต่ยังไม่มีระบบ OCR ผู้ใช้ต้องพิมพ์โจทย์เป็นข้อความ
- **PDF Indexing:** ผู้ดูแลระบบสามารถอัปโหลดและจัดทำดัชนีเอกสาร PDF ผ่าน Backend API โดยไม่มีฟังก์ชันอัปโหลด PDF สำหรับผู้ใช้ทั่วไป
- **Source Citations:** แสดงชื่อไฟล์และเลขหน้าจาก Metadata ของเอกสารที่ค้นคืนได้
- **Survey Feedback:** บันทึกและสรุปผลการประเมินจากผู้ใช้งาน

## System Architecture

SciLearn & Practice ใช้สถาปัตยกรรม Client–Server โดยแบ่งการทำงานออกเป็นส่วนต่าง ๆ ดังนี้

1. **Frontend:** รับคำถาม แสดงผลการวิเคราะห์ ขั้นตอนการแก้โจทย์ และข้อมูลอ้างอิง โดยทำงานจากหน้าเว็บที่ FastAPI เสิร์ฟ
2. **FastAPI Backend:** เสิร์ฟ Frontend และรับคำขอ API เพื่อประมวลผลคำถาม จัดการเอกสาร PDF และข้อมูลแบบประเมิน
3. **RAG Service:** สร้าง Query Embedding และค้นคืนเนื้อหาที่เกี่ยวข้องจาก ChromaDB
4. **ChromaDB:** จัดเก็บข้อมูลเอกสารและ Metadata สำหรับการค้นคืน
5. **LoRA Inference Server:** โหลด Qwen3-4B และ LoRA Adapter เพื่อรับคำถามและบริบทจาก Backend แล้วสร้างคำตอบในรูปแบบ JSON

### Processing Flow

```text
Browser → FastAPI → ChromaDB Retrieval → LoRA Inference Server → JSON Response → Browser
```

Backend ติดต่อ LoRA Inference Server ผ่าน localhost โดยตรง ส่วน Frontend ติดต่อเฉพาะ FastAPI เท่านั้น Ollama ยังคงเก็บไว้เป็นทางเลือกสำรองแบบ Manual แยกจากเส้นทางการประมวลผลหลัก

## Technology Stack

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic
- ChromaDB
- Sentence Transformers
- PyMuPDF

### AI / Machine Learning
- Qwen3-4B
- LoRA Adapter for inference
- Ollama `qwen3:4b` (Manual fallback, not automatic)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### Frontend
- HTML
- CSS
- JavaScript

### Development and Testing
- Pytest
- HTTPX
- Python Virtual Environment

## Project Structure

```text
SciTutor-Workbench02/
├── backend/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── lora_service.py
│   │   ├── ollama_service.py
│   │   ├── pdf_service.py
│   │   ├── rag_service.py
│   │   └── survey_service.py
│   ├── utils/
│   │   └── text_chunker.py
│   ├── init_db_from_pdf.py
│   └── main.py
├── frontend/
│   ├── assets/
│   │   ├── icons/
│   │   └── images/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── api.js
│   │   ├── app.js
│   │   ├── code-viewer.js
│   │   ├── config.js
│   │   ├── pdf-manager.js
│   │   ├── solver.js
│   │   ├── survey.js
│   │   └── theme.js
│   └── index.html
├── data/
│   └── (runtime data and uploaded PDFs)
├── docs/
│   ├── api-guide.md
│   ├── architecture.md
│   └── migration-notes.md
├── tests/
│   ├── test_api.py
│   └── test_utils.py
├── .env.example
├── .gitignore
├── cleanup_gemini_to_ollama.ps1
├── index.html
├── rebuild_multilingual_db
├── rebuild_multilingual_db.py
├── requirements.txt
├── start_scitutor.ps1
├── test_multilingual_search.py
└── README.md
```

หมายเหตุ:
- `.env`, `.venv`, `vector_db`, `.git`, cache และไฟล์สำรองไม่แสดงในโครงสร้างนี้
- `data/` ใช้เป็นพื้นที่เก็บข้อมูลที่ระบบสร้างหรือใช้งานระหว่างการทำงาน
- โครงสร้างนี้แสดงไฟล์ Source Code และเอกสารหลัก ไม่รวมไฟล์สำรองหรือข้อมูล Runtime

## Installation and Setup

### 1. Clone the Repository

```powershell
git clone <repository-url>
cd SciTutor-Workbench02
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure Environment Variables

สร้างไฟล์ `.env` จาก `.env.example` และกำหนดค่าตามสภาพแวดล้อมของเครื่อง

### 6. Start the LoRA Inference Server

LoRA Inference Server ทำงานใน Python Environment แยกต่างหากจาก Backend โดยใช้ไฟล์และโมเดลที่จัดเก็บไว้ใน `D:\SciTutor-Training`

เปิด PowerShell หน้าต่างแรก แล้วรัน:

```powershell
& "D:\SciTutor-Training\venv\Scripts\python.exe" "D:\SciTutor-Training\inference\lora_server.py"
```

รอจน Server โหลดโมเดลเสร็จและแสดงสถานะพร้อมรับคำขอ โดย Server จะรับการเชื่อมต่อเฉพาะภายในเครื่องที่ `127.0.0.1:8001`

**Important:**
- ต้องเปิด LoRA Server ค้างไว้ขณะใช้งาน Backend
- อย่าปิดหน้าต่าง LoRA Server ระหว่างใช้งาน
- LoRA Server ใช้ Environment แยกจาก `.venv` ของโปรเจกต์
- ไม่ต้องติดตั้ง Training Dependencies เพิ่มใน `requirements.txt` ของ Backend

Ollama `qwen3:4b` ยังคงเป็นทางเลือกสำรองแบบ Manual แต่ไม่ใช่โมเดลหลักของ API และไม่มีการสลับไปใช้โดยอัตโนมัติ

### 7. Prepare the ChromaDB Collection

หากต้องการสร้างฐานข้อมูลจากเอกสาร PDF ให้ดำเนินการดังนี้:

1. สร้างโฟลเดอร์ `data/uploads/` หากยังไม่มี
2. นำไฟล์ PDF ที่ต้องการจัดทำดัชนีใส่ไว้ในโฟลเดอร์ดังกล่าว
3. ตรวจสอบว่า `CHROMA_COLLECTION` ในไฟล์ `.env` เป็น `grade9_science_textbooks_multilingual`
4. รันคำสั่ง:

```powershell
New-Item -ItemType Directory -Force .\data\uploads
& ".\.venv\Scripts\python.exe" rebuild_multilingual_db.py
```

สคริปต์จะอ่านข้อความจาก PDF สร้าง Embeddings และบันทึกข้อมูลลง ChromaDB โดยใช้ Multilingual Embedding Model ซึ่งอาจต้องดาวน์โหลดโมเดลในครั้งแรก

หากยังไม่มีไฟล์ PDF สามารถข้ามขั้นตอนนี้ได้ แต่ระบบจะยังไม่มีข้อมูลเอกสารสำหรับค้นคืนจนกว่าจะมีการจัดทำดัชนี

### 8. Start the Backend

หลังจาก LoRA Inference Server พร้อมทำงานแล้ว ให้เปิด PowerShell อีกหน้าต่างด้วยสิทธิ์ Administrator

ไปยังโฟลเดอร์โปรเจกต์และรัน Launcher:

```powershell
# Open PowerShell in the project root before running the launcher
.\start_scitutor.ps1
```

Launcher จะตรวจสอบเครือข่าย Wi-Fi และ IPv4 Address ปัจจุบัน ก่อนเริ่ม FastAPI บน Wi-Fi IP ที่ตรวจพบ ณ ขณะนั้น โดยใช้ Port `8000`

เปิดเว็บเบราว์เซอร์ด้วย URL ที่ Launcher แสดง และตรวจสอบสถานะ Backend ผ่าน `/health`

**Startup Order:**
1. เปิด LoRA Inference Server และรอจนพร้อมใช้งาน
2. เปิด FastAPI ด้วย `start_scitutor.ps1`
3. เข้าใช้งานผ่าน URL ที่ Launcher แสดง

หาก LoRA Server ไม่ทำงาน Backend จะไม่สามารถเรียกใช้โมเดลหลักเพื่อสร้างคำตอบได้

## Environment Configuration

SciLearn & Practice ใช้ไฟล์ `.env` สำหรับกำหนดค่าการทำงานของ Backend

ตัวอย่างค่าที่ใช้:

```env
CHROMA_DB_PATH=vector_db
CHROMA_COLLECTION=grade9_science_textbooks_multilingual
FRONTEND_ORIGINS=http://127.0.0.1:5500,http://localhost:5500,http://localhost:63342
MAX_UPLOAD_MB=250
```

### Configuration Details

| Variable | Description |
|---|---|
| `CHROMA_DB_PATH` | ตำแหน่งจัดเก็บฐานข้อมูล ChromaDB |
| `CHROMA_COLLECTION` | ชื่อ Collection ที่ใช้ค้นคืนข้อมูล |
| `FRONTEND_ORIGINS` | รายการ Origin ที่อนุญาตให้เรียก Backend |
| `MAX_UPLOAD_MB` | ขนาดไฟล์ PDF สูงสุดที่อนุญาตให้อัปโหลด หน่วย MB |

ค่าเริ่มต้นของขนาดไฟล์ PDF คือ 250 MB สามารถเปลี่ยนแปลงได้ผ่าน `MAX_UPLOAD_MB` และต้อง Restart Backend เพื่อให้โหลดค่าใหม่

เมื่อ Frontend ถูกเสิร์ฟจาก FastAPI ใน Origin เดียวกัน การกำหนด `FRONTEND_ORIGINS` สำหรับ Frontend ที่แยก Server ออกจาก Backend จะจำเป็นเฉพาะกรณีที่ใช้งานแยก Origin เท่านั้น

## API Endpoints

Base API Prefix:

```text
/api/v3
```

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | ตรวจสอบสถานะ Backend |
| POST | `/api/v3/analyze-with-pdf-rag` | วิเคราะห์โจทย์ด้วย PDF-based RAG |
| POST | `/api/v3/index-pdf` | อัปโหลดและจัดทำดัชนีเอกสาร PDF |
| POST | `/api/v3/survey` | บันทึกผลประเมินจากผู้ใช้ |
| GET | `/api/v3/survey/summary` | ดึงข้อมูลสรุปผลประเมิน |

### Analyze with PDF RAG

Endpoint:

```http
POST /api/v3/analyze-with-pdf-rag
```

Request:

```json
{
  "question": "โจทย์วิทยาศาสตร์ที่ต้องการให้ช่วยอธิบาย"
}
```

Response Structure:

```json
{
  "status": "success",
  "answer": "คำอธิบาย",
  "vars": [
    {
      "name": "V",
      "val": "12 โวลต์"
    }
  ],
  "socraticCards": [
    {
      "question": "โจทย์นี้ต้องใช้หลักการใด?",
      "hint": "พิจารณาความสัมพันธ์ของตัวแปร",
      "checkpoint": "สามารถอธิบายเหตุผลได้หรือไม่?"
    }
  ],
  "steps": [
    {
      "title": "ขั้นที่ 1",
      "detail": "ระบุข้อมูลที่โจทย์กำหนด"
    }
  ],
  "pdfRef": "หน้า 12",
  "citations": [
    {
      "source_file": "textbook.pdf",
      "page": 12
    }
  ]
}
```

ตัวอย่างข้างต้นเป็นตัวอย่างโครงสร้าง ไม่ใช่ผลลัพธ์จากการเรียก API จริง

### Response Contract

โมเดลสร้างผลลัพธ์ตาม Response Contract ซึ่งประกอบด้วย 5 ฟิลด์หลัก:

| Field | Type |
|---|---|
| `answer` | String |
| `vars` | Array of `{name, val}` |
| `socraticCards` | Array of `{question, hint, checkpoint}` |
| `steps` | Array of `{title, detail}` |
| `pdfRef` | String |

ส่วน API Response จะเพิ่ม `status` และ `citations` เข้ามาอีก 2 ฟิลด์

Array แต่ละรายการสามารถเป็น `[]` ได้เมื่อไม่มีข้อมูลที่จำเป็นต้องแสดง

### PDF Indexing

Endpoint:

```http
POST /api/v3/index-pdf
```

ใช้ `multipart/form-data` โดยส่งไฟล์ PDF ผ่านช่อง `file`

Endpoint นี้เป็น Backend API สำหรับงานจัดการเอกสารและการพัฒนาระบบ ไม่ใช่ฟังก์ชันอัปโหลด PDF บนหน้าเว็บสำหรับผู้ใช้ทั่วไป ทั้งนี้ Endpoint ยังไม่มีระบบ Authentication หรือ Authorization ในตัว จึงต้องจำกัดการเข้าถึงด้วยมาตรการระดับเครือข่าย

ระบบตรวจสอบนามสกุลไฟล์ รูปแบบไฟล์ และขนาดไฟล์ก่อนดำเนินการจัดทำดัชนี

### Survey

บันทึกคะแนน 3 รายการ:

- `rating_ocr`
- `rating_socratic`
- `rating_overall`

แต่ละรายการต้องมีค่าตั้งแต่ 1 ถึง 5

## PDF Processing and Retrieval-Augmented Generation

### PDF Upload

ระบบรองรับการอัปโหลดเอกสาร PDF ผ่าน Backend API สำหรับผู้ดูแลระบบ โดยมีรายละเอียดดังนี้:

- รองรับไฟล์ PDF สูงสุด 250 MB โดยค่าเริ่มต้น
- สามารถกำหนดขนาดสูงสุดผ่าน `MAX_UPLOAD_MB`
- อ่านไฟล์เป็นส่วนขนาด 1 MB ระหว่างการบันทึก
- ตรวจสอบลายเซ็นไฟล์ PDF ก่อนนำไปประมวลผล
- จัดทำดัชนีเอกสารและจัดเก็บข้อมูลลง ChromaDB

การจัดทำดัชนีเอกสารขนาดใหญ่ยังต้องใช้เวลา หน่วยความจำ และพื้นที่ดิสก์ตามปริมาณข้อมูล

### Retrieval Process

ระบบใช้ Sentence Transformers รุ่น:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

สำหรับสร้าง Query Embedding และใช้ ChromaDB ในการค้นคืนข้อมูล

ค่าเริ่มต้นของการค้นคืนคือ 4 รายการ (`top_k=4`)

ข้อมูลที่ค้นคืนประกอบด้วย:

- ข้อความจากเอกสาร (`text`)
- ชื่อไฟล์ต้นทาง (`source_file`)
- เลขหน้า (`page`)
- Distance Score (`distance`)

### Answer Generation

ระบบส่งคำถามและบริบทจากเอกสารที่ค้นคืนได้จาก ChromaDB ผ่าน Backend ไปยัง LoRA Inference Server ที่ทำงานบน `127.0.0.1:8001`

โมเดลหลักที่ใช้คือ:

```text
Base Model: Qwen/Qwen3-4B
Fine-tuned Adapter: LoRA Adapter
```

LoRA Server ทำงานใน Environment แยกที่ `D:\SciTutor-Training` ส่วน Backend ติดต่อผ่าน `backend/services/lora_service.py`

ผลลัพธ์จากโมเดลจะถูกตรวจสอบรูปแบบ JSON ด้วย Pydantic ตาม Response Contract ก่อนส่งกลับไปยัง API

Ollama `qwen3:4b` ไม่ได้ถูกเรียกใช้ในเส้นทางคำขอหลัก และไม่มี Automatic Fallback

### Source Citations

รายการอ้างอิงถูกสร้างจาก Metadata ของเอกสารที่ค้นคืนได้ โดยใช้ชื่อไฟล์และเลขหน้า และตัดรายการที่ซ้ำกันออก

ฟิลด์ `citations` เก็บชื่อไฟล์และเลขหน้า ส่วน `pdfRef` ถูกสร้างจากเลขหน้าของรายการอ้างอิง หากไม่พบข้อมูลอ้างอิง ระบบจะกำหนด `pdfRef` เป็น `ไม่พบแหล่งอ้างอิง`

## Network Deployment

SciLearn & Practice สามารถเปิดใช้งานผ่านเครือข่าย Wi-Fi หรือ Mobile Hotspot เพื่อให้ผู้ใช้อุปกรณ์อื่นเข้าถึงเว็บแอปพลิเคชันผ่านเครื่องที่รัน Backend ได้

### Start with PowerShell Launcher

เปิด PowerShell ด้วยสิทธิ์ Administrator และไปยังโฟลเดอร์โปรเจกต์ จากนั้นรัน:

```powershell
.\start_scitutor.ps1
```

Launcher จะดำเนินการดังนี้:

1. ตรวจสอบ Python Virtual Environment และไฟล์หลักที่จำเป็น
2. ตรวจสอบสถานะ Wi-Fi และ IPv4 Address ปัจจุบัน
3. คำนวณ Subnet จาก Prefix Length ของเครือข่าย
4. ตรวจสอบ Windows Firewall และ Network Profile
5. สร้างหรือปรับปรุง Firewall Rule เฉพาะสำหรับ SciTutor
6. เริ่ม FastAPI บน Wi-Fi IP ปัจจุบันที่ Port 8000

### Access from Other Devices

1. เชื่อมต่อคอมพิวเตอร์ที่รัน Backend เข้ากับ Wi-Fi หรือ Hotspot ที่ต้องการใช้
2. เปิด PowerShell แบบ Administrator
3. รัน `start_scitutor.ps1`
4. ตรวจสอบ URL ที่ Launcher แสดง
5. ให้อุปกรณ์อื่นเชื่อมต่อ Wi-Fi หรือ Hotspot เครือข่ายเดียวกัน
6. เปิด URL ที่ Launcher แสดงใน Browser

ตัวอย่างรูปแบบ URL:

```text
http://<CURRENT-WIFI-IP>:8000/
```

### Important Notes

- IP Address อาจเปลี่ยนแปลงตามเครือข่ายที่เชื่อมต่อ
- ต้องรัน Launcher ใหม่เมื่อเปลี่ยนเครือข่ายหรือ IP Address
- เครื่องที่รัน Backend ต้องเปิดอยู่ตลอดเวลาที่อุปกรณ์อื่นใช้งาน
- LoRA Inference Server ต้องทำงานบนเครื่องเดียวกับ Backend และต้องเปิดไว้ที่ `127.0.0.1:8001`
- Launcher ต้องใช้ PowerShell แบบ Administrator
- Launcher ตรวจสอบเงื่อนไขของ Wi-Fi และ Network Profile แต่ไม่ได้ตรวจสอบโดยตรงว่าเครือข่ายนั้นเป็น Mobile Hotspot จริงหรือไม่

## Compatibility and API Security Notes

### Python Compatibility and Dependency Check

- Python 3.14.7 is the development and testing version used for this project.
- The current virtual environment was checked using `pip check`, and no broken requirements were found.
- Compatibility with other Python versions has not been verified.
- The dependency check result applies to the current environment and does not guarantee that a fresh installation will work identically.

### PDF Indexing API Security

The `/api/v3/index-pdf` endpoint accepts PDF uploads through the backend API for document indexing. It is not presented as a general user-facing upload feature.

The endpoint currently does not implement authentication or authorization checks. Deploy it only in a trusted environment and restrict network access appropriately.

When running the application on a Wi-Fi hotspot, devices that can reach the backend on port 8000 may also be able to access this endpoint. Use the application only on a trusted network.

## Documentation

เอกสารเพิ่มเติมอยู่ในโฟลเดอร์ `docs/`:

- `docs/api-guide.md` — รายละเอียด API และข้อจำกัดการอัปโหลด PDF
- `docs/architecture.md` — ภาพรวมสถาปัตยกรรมระบบ
- `docs/migration-notes.md` — บันทึกการเปลี่ยนแปลงระหว่างการพัฒนา

### Team Member and Role
- 6752300232 นางสาวกรกมล โตโส — Frontend/UI
- 6752300810 นางสาวกนกณัฐ กึ่งพุทธพงศ์ — ???
- 6752300828 นายณธกร จินดาจิรภัทร — ???
- 6752300895 นางสาวนพวรรณ อังคตรีรัตน์ —
- 6752301115 นางสาวศศิธร ปาโส — ???
- 6752301361 นางสาวอโนชา สาดสะดี — ???
