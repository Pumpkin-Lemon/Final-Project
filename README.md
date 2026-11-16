# SciTutor-Workbench

AI Science Tutor สำหรับวิทยาศาสตร์ระดับชั้นมัธยมศึกษาปีที่ 3 โดยใช้แนวทาง **Retrieval-Augmented Generation (RAG)** เพื่อค้นหาเนื้อหาจากเอกสารประกอบการเรียน แล้วนำบริบทที่ค้นพบมาใช้สร้างคำอธิบายสำหรับผู้เรียน

โปรเจกต์นี้พัฒนาด้วย Python, FastAPI, ChromaDB และ Ollama โดยแยก Frontend และ Backend ออกจากกัน

> **สถานะโครงการ:** ระบบอยู่ระหว่างการพัฒนาและทดสอบ ยังไม่ควรถือว่าคำตอบจาก AI ถูกต้องเสมอหรือพร้อมใช้งานในระบบการเรียนการสอนจริง

---

## 1. Project Overview

SciTutor-Workbench มีเป้าหมายเพื่อช่วยผู้เรียนทำความเข้าใจโจทย์วิทยาศาสตร์ โดยใช้ข้อมูลจากเอกสารที่ทีมจัดเตรียมไว้เป็นแหล่งอ้างอิง

ลำดับการทำงานโดยสรุป:

1. ผู้เรียนส่งคำถามผ่านหน้าเว็บ
2. Backend รับคำถามผ่าน FastAPI
3. ระบบค้นหาข้อความที่เกี่ยวข้องจาก ChromaDB
4. นำ Context ที่ค้นพบส่งให้ Ollama
5. Ollama สร้างคำอธิบายตามรูปแบบ Response Contract
6. Backend ส่งคำตอบและ Citation กลับไปยัง Frontend

## 2. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| Vector Database | ChromaDB |
| Embedding | sentence-transformers |
| Embedding Model | paraphrase-multilingual-MiniLM-L12-v2 |
| LLM Runtime | Ollama |
| Current LLM | qwen3:4b |
| PDF Processing | PyMuPDF |
| API Validation | Pydantic |

## 3. System Architecture

```text
             Student
                |
                v
        Frontend (Browser)
                |
                v
          FastAPI Backend
                |
                v
       ChromaDB Retrieval
                |
                v
        Retrieved Context
                |
                v
          Ollama (LLM)
                |
                v
       Structured JSON Response
                |
                v
        Frontend Rendering
```

**Important:** PDF หนังสือเรียนเป็นข้อมูลที่ผู้ดูแลระบบเตรียมและนำเข้า Knowledge Base ไม่ใช่ไฟล์ที่ผู้เรียนต้องอัปโหลดทุกครั้งที่ถามคำถาม

## 4. Repository Structure

```text
SciTutor-Workbench/
│
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── utils/
│   ├── __init__.py
│   ├── main.py
│   └── init_db_from_pdf.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
│
├── data/
│   ├── evaluation/
│   ├── ipst_pdfs/
│   ├── processed/
│   └── uploads/
│
├── docs/
│   ├── api-guide.md
│   ├── architecture.md
│   └── migration-notes.md
│
├── tests/
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

หมายเหตุ:

- `vector_db/` เป็นฐานข้อมูล ChromaDB เฉพาะเครื่อง จึงไม่ควร Commit
- `data/uploads/` ใช้เก็บ PDF ในเครื่อง ไม่ส่งไฟล์ PDF จริงขึ้น GitHub
- `data/processed/` เป็นข้อมูลที่สร้างขึ้นระหว่างประมวลผล
- `data/evaluation/` เป็นชุดข้อมูลทดสอบที่ต้องตรวจสอบก่อนเผยแพร่
- โครงสร้างย่อยอาจแตกต่างจากตัวอย่างตามไฟล์จริงในแต่ละเวอร์ชัน

## 5. Requirements

ก่อนเริ่มติดตั้ง ควรเตรียม:

- Python 3.14.7 (มาตรฐานชั่วคราวของทีม ซึ่งผ่านการทดสอบ Fresh Clone บน Windows เมื่อ 16 พฤศจิกายน 2026)
- Git
- Ollama
- พื้นที่ดิสก์สำหรับ Model Cache และ ChromaDB
- PDF หนังสือเรียนที่ทีมมีสิทธิ์ใช้งาน

Dependency หลักอยู่ใน `requirements.txt`

**ผลการทดสอบ Dependency:** `requirements.txt` มี `sentence-transformers` อยู่แล้ว และการติดตั้ง Dependency ทั้งหมดผ่านในการทดสอบ Fresh Clone ด้วย Python 3.14.7 โดย `pip check` ไม่พบ Dependency ที่ขัดแย้งกัน

## 6. Local Development Setup

สมาชิกแต่ละคนสามารถ Clone Repository และรันระบบบนเครื่องของตัวเองได้

### 6.1 Clone Repository

```bash
git clone <REPOSITORY_URL>
cd SciTutor-Workbench
```

แทนที่ `<REPOSITORY_URL>` ด้วย URL จริงของ Repository ทีม

### 6.2 Create Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 6.3 Install Dependencies

```bash
python -m pip install -r requirements.txt
python -m pip check
```

**ผลการทดสอบ:** คำสั่งติดตั้ง Dependency และ `pip check` ผ่านในการทดสอบ Fresh Clone ด้วย Python 3.14.7 บน Windows เมื่อ 16 พฤศจิกายน 2026 ทั้งนี้ยังไม่ได้ยืนยันความเข้ากันได้กับ Python เวอร์ชันอื่นหรือระบบปฏิบัติการอื่น

### 6.4 Configure Environment

สร้าง `.env` จาก `.env.example`

Windows:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

ตรวจสอบค่าใน `.env` ให้ตรงกับเครื่องที่ใช้งาน โดยเฉพาะ:

- `CHROMA_DB_PATH`
- `CHROMA_COLLECTION`
- `FRONTEND_ORIGINS`
- `MAX_UPLOAD_MB`

ห้าม Commit `.env` หรือส่งค่าความลับผ่าน GitHub

### 6.5 Prepare Ollama

ติดตั้ง Ollama และเตรียมโมเดลที่ Backend ใช้งาน

โมเดลปัจจุบันที่ใช้ทดสอบคือ:

```bash
ollama pull qwen3:4b
```

ตรวจสอบโมเดลที่ติดตั้ง:

```bash
ollama list
```

ต้องแน่ใจว่า Ollama ทำงานอยู่ก่อนส่งคำถามจาก Frontend

### 6.6 Prepare Embedding Model

Embedding Model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

โมเดลนี้จะถูกดาวน์โหลดและเก็บใน Model Cache ของแต่ละเครื่องเมื่อมีการโหลดใช้งาน

สมาชิกไม่จำเป็นต้องนำ Model Weights เข้า Git Repository

### 6.7 Prepare Knowledge Base

Knowledge Base ประกอบด้วย PDF และข้อมูล Embeddings ใน ChromaDB

**ข้อสำคัญ:** ห้ามรัน `rebuild_multilingual_db.py` หรือสคริปต์สร้างฐานข้อมูลอื่นโดยไม่ตรวจสอบก่อนว่าสคริปต์ใช้ PDF ชุดใด, ChromaDB path ใด และ Collection ชื่อใด

สคริปต์ `rebuild_multilingual_db.py` ที่ตรวจพบใน Repository กำหนด Collection ชื่อ `grade9_science_textbooks_multilingual` ไว้ภายใน ขณะที่ฐานข้อมูลที่ระบบปัจจุบันใช้งานคือ `grade9_science_textbooks_combined`

ดังนั้นควรใช้ Knowledge Base ที่ผู้ดูแลจัดเตรียมและยืนยันแล้ว จนกว่าจะมีขั้นตอนสร้างฐานข้อมูลฉบับมาตรฐานของทีม

ห้ามนำ ChromaDB ของสมาชิกคนหนึ่งไปเขียนทับฐานข้อมูลของสมาชิกอีกคนหรือเครื่อง Demo โดยไม่มีกระบวนการสำรองและตรวจสอบ

## 7. Run the Application

เปิด Terminal แยกกัน 2 หน้าต่าง

### Terminal 1: Backend

เปิด Virtual Environment แล้วรัน:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

ตรวจสอบ Health:

```text
http://127.0.0.1:8000/health
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### Terminal 2: Frontend

```bash
python -m http.server 5500 --directory frontend
```

เปิด Browser:

```text
http://127.0.0.1:5500
```

หากเกิด CORS Error ให้ตรวจสอบ `FRONTEND_ORIGINS` ใน `.env` ให้ตรงกับ URL ที่เปิด Frontend

## 8. API Endpoints

Endpoint หลักที่ใช้ในระบบ:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | ตรวจสอบสถานะ Backend |
| POST | `/api/v3/analyze-with-pdf-rag` | วิเคราะห์โจทย์ด้วย RAG |
| POST | `/api/v3/index-pdf` | จัดทำดัชนี PDF |
| POST | `/api/v3/survey` | บันทึก Feedback |
| GET | `/api/v3/survey/summary` | ดูสรุป Feedback |

รายละเอียด Request และ Response ให้ยึด `docs/api-guide.md` และ Schema ใน Backend เป็นหลัก

## 9. Response Contract

ผลลัพธ์หลักจาก AI ต้องมีโครงสร้าง:

| Field | Type | Description |
|---|---|---|
| `answer` | string | คำอธิบายคำตอบ |
| `vars` | array | ตัวแปรและค่าที่เกี่ยวข้อง |
| `socraticCards` | array | คำถามชวนคิด คำใบ้ และจุดตรวจความเข้าใจ |
| `steps` | array | ลำดับขั้นตอนการแก้โจทย์ |
| `pdfRef` | string | ข้อมูลอ้างอิง PDF |

API Response เพิ่ม:

- `status`
- `citations`

โดย `citations` ต้องมาจากข้อมูล Retrieval ของ Backend ไม่ใช่ให้ LLM สร้างขึ้นเอง

## 10. Central Demo Deployment

เครื่อง Central Demo เป็นสภาพแวดล้อมแยกจาก Local Development

สิ่งที่เครื่องกลางต้องมี:

- Source Code จาก Branch `main` หรือ Release ที่ทีมอนุมัติ
- Python Environment ของเครื่องกลาง
- Ollama และ LLM Model
- Embedding Model Cache
- ChromaDB ของเครื่องกลาง
- PDF ที่ทีมมีสิทธิ์ใช้
- `.env` สำหรับเครื่องกลางโดยเฉพาะ

**ข้อกำหนดสำคัญ**

1. เครื่อง Demo ต้องมี `.env` ของตัวเอง
2. ห้ามใช้ ChromaDB ร่วมกับเครื่องสมาชิกผ่านการคัดลอกไฟล์ฐานข้อมูลไปมา
3. ห้ามให้เครื่อง Demo ดึง Feature Branch ที่ยังไม่ผ่าน Review
4. การอัปเดต Demo ต้องผ่านการตรวจสอบและอนุมัติจากทีม
5. ก่อนอัปเดตระบบควรสำรองฐานข้อมูลและตรวจสอบเวอร์ชัน
6. ไม่ควรเปิด API สำหรับ Index PDF ให้ผู้ใช้งานทั่วไปเข้าถึง

### สถานะการรองรับผู้ใช้ผ่านเครือข่าย LAN

**สถานะปัจจุบัน: ยังไม่พร้อมสำหรับการใช้งานหลายเครื่องผ่าน LAN โดยอัตโนมัติ**

- Frontend ใน `frontend/js/config.js` กำหนด API Base URL เป็น `http://127.0.0.1:8000`
- คำสั่ง Backend ในขั้นตอน Local Development ใช้ `127.0.0.1` ซึ่งรับการเชื่อมต่อเฉพาะเครื่องที่รัน Backend
- เมื่อผู้เรียนเปิด Frontend จากคอมพิวเตอร์ของตนเอง `127.0.0.1` จะหมายถึงคอมพิวเตอร์ของผู้เรียน ไม่ใช่เครื่อง Central Demo

การรองรับ LAN ต้องปรับการตั้งค่า Backend ให้รับการเชื่อมต่อจากเครือข่าย ปรับวิธีระบุ API URL ของ Frontend และกำหนด CORS ให้ครอบคลุม Origin ของ Frontend ที่ใช้งานจริง รวมถึงตั้งค่า Firewall ให้เหมาะสมและปลอดภัย

**อย่าถือว่าระบบรองรับ LAN แล้ว** จนกว่าจะมีการปรับปรุงและทดสอบการเชื่อมต่อจากเครื่องผู้เรียนหลายเครื่องจริง

## 11. Team Git Workflow

แนะนำให้ใช้ Branch แยกตามงาน:

```text
main
 |
 +-- feature/frontend
 |
 +-- feature/backend
 |
 +-- feature/rag
 |
 +-- fix/bug-description
```

แนวทางการทำงาน:

1. สมาชิกสร้าง Feature Branch จาก `main`
2. พัฒนาและทดสอบในเครื่องตัวเอง
3. Commit เฉพาะ Source Code และไฟล์ที่ทีมอนุมัติให้แชร์
4. Push Branch ขึ้น GitHub
5. เปิด Pull Request
6. สมาชิกในทีม Review
7. Merge เมื่อผ่านการตรวจสอบ
8. เครื่อง Demo อัปเดตจาก `main` หรือ Release ที่อนุมัติแล้วเท่านั้น

## 12. Data and Security Policy

**ห้าม Commit ไฟล์ต่อไปนี้**

- `.env` และข้อมูลลับ
- PDF หนังสือเรียนที่ไม่ได้รับอนุญาตให้เผยแพร่
- ChromaDB และฐานข้อมูลจริง
- Model Weights
- Model Cache
- `.venv/`
- Log หรือข้อมูล Feedback ที่มีข้อมูลส่วนบุคคล
- Backup ที่อาจมีข้อมูลเดิมหรือข้อมูลลับ

ก่อน Commit ทุกครั้งควรตรวจสอบ:

```bash
git status --short
git diff --cached --stat
```

หากพบไฟล์ที่ไม่ควรเผยแพร่ ให้หยุดและตรวจสอบก่อน Commit

## 13. Troubleshooting

### Backend ไม่เริ่มทำงาน

- ตรวจสอบว่าเปิด Virtual Environment แล้ว
- ตรวจสอบ Dependency
- ตรวจสอบ Port 8000
- ตรวจสอบ Error ใน Terminal

### Frontend เรียก Backend ไม่ได้

- ตรวจสอบ Backend Health
- ตรวจสอบ URL และ Port
- ตรวจสอบ `FRONTEND_ORIGINS`
- ตรวจสอบ Browser Console

### Ollama ไม่ตอบคำถาม

- ตรวจสอบว่า Ollama ทำงานอยู่
- ตรวจสอบผล `ollama list`
- ตรวจสอบว่าโมเดลที่ Backend เรียกใช้งานติดตั้งแล้ว
- ตรวจสอบ Log ของ Backend

### Retrieval ไม่พบข้อมูล

- ตรวจสอบ `CHROMA_DB_PATH`
- ตรวจสอบ `CHROMA_COLLECTION`
- ตรวจสอบว่ามี Knowledge Base อยู่จริง
- ตรวจสอบว่า Embedding Model โหลดได้
- อย่าเพิ่งสร้างฐานข้อมูลใหม่ก่อนตรวจสอบ Collection เดิม

## 14. Current Limitations

ระบบยังอยู่ในขั้นตอนพัฒนาและตรวจสอบคุณภาพ

ประเด็นที่ต้องทดสอบเพิ่มเติม:

- ความถูกต้องของคำตอบเมื่อ Retrieval พบหลายหัวข้อ
- ความสัมพันธ์ระหว่าง Context และ Citation
- ความถูกต้องของหน้า PDF ที่อ้างอิง
- ความเสถียรของการโหลด Embedding Model
- การทำงานพร้อมกันของผู้ใช้หลายคน
- การจัดการ Knowledge Base สำหรับ Local และ Central Demo

การที่ API ส่ง JSON ถูก Schema หรือแสดง Citation ได้ ไม่ได้หมายความว่าคำตอบด้านเนื้อหาถูกต้องเสมอไป

---

## 15. Team Documentation

เอกสารประกอบที่ควรอ่านเพิ่มเติม:

- `docs/api-guide.md` — API Endpoints
- `docs/architecture.md` — System Architecture
- `docs/migration-notes.md` — ประวัติการเปลี่ยนแปลงระบบ

เอกสารสำหรับการติดตั้งและดูแล Central Demo ควรจัดทำแยกจาก README เมื่อทีมกำหนดขั้นตอน Deployment และ Knowledge Base ที่เป็นมาตรฐานแล้ว

---

**SciTutor-Workbench — Local Development and Central Demo**