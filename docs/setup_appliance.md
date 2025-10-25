# Demo ระบบ Log Management (Full-Stack Intern Assignment)

โปรเจกต์นี้คือระบบ Log Management ที่พัฒนาขึ้นสำหรับข้อสอบภาคปฏิบัติ Full-Stack Developer (Intern)

## 1. สถาปัตยกรรม (Architecture)

ระบบนี้ใช้สถาปัตยกรรมที่ประกอบด้วย 3 ส่วนหลัก:
1.  **Ingestor (FastAPI - Python):** รับ Log (Syslog, HTTP JSON) และทำการ Normalize
2.  **Storage (PostgreSQL):** จัดเก็บ Log ที่ผ่านการ Normalization แล้ว
3.  **UI/Dashboard (Grafana):** แสดงผล Dashboard, Query และจัดการ Alert

(ดูแผนภาพและคำอธิบาย data flow ฉบับเต็มได้ที่: `/docs/architecture.md`)

## 2. Tech Stack

-   **Backend (Ingestor):** Python (FastAPI)
-   **Database:** PostgreSQL
-   **UI/Dashboard:** Grafana
-   **Deployment:** Docker Compose

## 3. วิธีการรัน (Appliance Mode)

**Prerequisites:**
-   Docker
-   Docker Compose (v2)

**ขั้นตอน:**
1.  Clone repository นี้
2.  สร้างไฟล์ `.env` จาก `.env.example`:
    ```bash
    cp .env.example .env
    ```
3.  รันระบบ:
    ```bash
    docker compose up -d
    ```

**การเข้าใช้งาน:**
-   **UI (Grafana):** `http://localhost:3000` (User: `admin`, Pass: `admin`)
-   **API (Ingestor):** `http://localhost:8080` (Health Check)

## 4. วิธีการทดสอบ (Testing)

ดูรายละเอียดการทดสอบ (ยิง Log) ได้ที่: `/samples/`

**A. ทดสอบ HTTP (JSON):**
(ต้องมี Python และ `requests` ติดตั้งในเครื่อง)
```bash
# (Windows)
python samples/post_logs.py demoA samples/crowdstrike.json samples/windows_ad.json
python samples/post_logs.py demoB samples/aws_cloudtrail.json samples/m365_audit.json