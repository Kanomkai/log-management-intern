# Backend (Ingestor) README

ไดเรกทอรีนี้ chứa (contains) โค้ดสำหรับบริการ "Ingestor" (ตัวรับข้อมูล) หลักของโปรเจกต์ Log Management

## 1. Tech Stack

* **Framework:** FastAPI (Python)
* **Database Connection:** SQLAlchemy (Async)
* **Syslog Server:** Custom `asyncio` UDP Server

## 2. หน้าที่หลัก (Responsibilities)

นี่คือหัวใจหลักของ Data Pipeline ทำหน้าที่ 3 อย่าง:

1.  **HTTP API Ingestor:**
    * รัน Web Server (uvicorn) บนพอร์ต `8080`
    * [cite_start]เปิด Endpoint `POST /ingest` เพื่อรับ Log แบบ JSON (เช่น จาก Apps, AWS, M365) [cite: 13, 20]

2.  **Syslog Server:**
    * รัน UDP Server บนพอร์ต `514`
    * [cite_start]รับข้อความ Syslog (เช่น จาก Firewalls, Routers) [cite: 12]

3.  **Normalization & Storage:**
    * "แปลง" (Normalize) Log ทุกชนิด (ทั้ง JSON และ Syslog) ให้เข้ากับ Schema กลาง (ที่กำหนดใน `models.py`)
    * "บันทึก" (Save) Log ที่แปลงแล้วลงในฐานข้อมูล PostgreSQL

## 3. การรัน (Running)

บริการนี้ถูกออกแบบมาให้รันเป็น Container (ชื่อ `ingestor`) ภายใน `docker-compose.yml` ไม่แนะนำให้รันโดยตรง (Manual)