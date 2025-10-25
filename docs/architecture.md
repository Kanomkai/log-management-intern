# /docs/architecture.md
# สถาปัตยกรรมระบบ Demo Log Management

## 1. แผนภาพสถาปัตยกรรม (Appliance Mode)

(Log Sources: Syslog, HTTP JSON) 
    --> (Ingestor API: FastAPI) 
    --> (Storage: PostgreSQL) 
    <-- (UI/Alerting: Grafana)

## 2. ส่วนประกอบหลัก (Components)

ระบบนี้ประกอบด้วย 3 บริการหลัก (Services) ที่รันบน Docker Compose

### 1. Ingestor (FastAPI - Custom Code)
* [cite_start]**หน้าที่:** รับข้อมูล (Ingestion), แปลงข้อมูล (Normalization) [cite: 20]
* **Ingestion:**
    * [cite_start]เปิด **UDP Port 514** เพื่อรับ Syslog (เช่น จาก Firewall) [cite: 12]
    * [cite_start]เปิด **HTTP Port 8080** (Endpoint `/ingest`) เพื่อรับ JSON Logs [cite: 13]
* **Normalization:** โค้ด Python จะแปลงข้อมูลทุกแหล่งให้อยู่ใน "Schema กลาง" ก่อนบันทึก
* **Storage:** ส่งข้อมูลที่แปลงแล้วไปยัง PostgreSQL

### 2. PostgreSQL (Storage)
* [cite_start]**หน้าที่:** จัดเก็บ Log ที่ผ่านการ Normalization แล้ว [cite: 20]
* [cite_start]**Schema:** ใช้ตาราง `logs` แบบ Partitioned แบ่งตาม `@timestamp` และใช้ `JSONB` กับ GIN Index เพื่อการค้นหาที่รวดเร็ว [cite: 20]
* [cite_start]**Retention:** ออกแบบตารางให้รองรับการลบข้อมูลเก่า (Partition) ตามข้อกำหนด 7 วัน [cite: 27]

### 3. Grafana (UI / Dashboard / Alerting)
* **หน้าที่:** เป็น Frontend ทั้งหมด (Dashboard, Alert, AuthN)
* [cite_start]**Dashboard:** เชื่อมต่อ PostgreSQL แสดงผล Top N, Timeline, และ Filter [cite: 20]
* [cite_start]**Alerting:** ใช้ระบบ Alert ของ Grafana สร้างกฎ (เช่น Login ล้มเหลว) [cite: 21]
* [cite_start]**Security (AuthN/AuthZ):** ใช้ระบบผู้ใช้ของ Grafana สร้าง `admin` และ `viewer` [cite: 23] และจำกัดสิทธิ์ของ Viewer

## 3. โมเดล Tenant
* ข้อมูลทุกแถวในตาราง `logs` จะมีคอลัมน์ `tenant`
* [cite_start]การแยกข้อมูล Tenant [cite: 23] จะถูกควบคุมที่ระดับ Dashboard ใน Grafana โดยใช้ตัวแปร (Variable) `$tenant` ในการคิวรีข้อมูล