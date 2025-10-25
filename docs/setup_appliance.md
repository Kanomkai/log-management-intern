# /docs/setup_appliance.md
# คู่มือการติดตั้ง (Appliance Mode)

คู่มือนี้อธิบายการติดตั้ง Demo Log Management บนเครื่องเดียว (VM/Bare-metal) โดยใช้ Docker Compose

## 1. ข้อกำหนดขั้นต่ำ (Prerequisites)
* [cite_start]OS: Ubuntu 22.04+ (หรือ OS อื่นที่รัน Docker ได้) [cite: 104]
* [cite_start]Hardware: 4 vCPU, 8 GB RAM, 40 GB Disk [cite: 104]
* Software:
    * `git`
    * `docker`
    * `docker-compose`

## 2. ขั้นตอนการติดตั้ง (Installation)

1.  **Clone Repository:**
    ```bash
    git clone [Your Git Repository URL]
    cd log-management-intern
    ```

2.  **สร้างไฟล์ Environment:**
    คัดลอกไฟล์ `.env.example` มาเป็น `.env` (สามารถแก้ไขค่า admin password ได้ที่นี่)
    ```bash
    cp .env.example .env
    ```

3.  **รันระบบ (One Command):**
    ```bash
    docker-compose up -d
    ```

## 3. การตรวจสอบระบบ (Verification)

1.  **ตรวจสอบสถานะ Container:**
    ```bash
    docker ps
    ```
    คุณควรเห็น 3 services รันอยู่: `logmgmt_db` (postgres), `logmgmt_ingestor` (fastapi), `logmgmt_ui` (grafana)

2.  **เข้าใช้งาน UI (Grafana):**
    * เปิด Web Browser ไปที่ `http://<Your-Server-IP>:3000`
    * Login ด้วย:
        * **User:** `admin` (หรือค่าใน `.env`)
        * **Pass:** `admin` (หรือค่าใน `.env`)

3.  **ตรวจสอบ Endpoint (Ingestor):**
    * เปิด `http://<Your-Server-IP>:8080/`
    * คุณควรเห็น: `{"status":"ok","message":"Ingestor service is running"}`

## [cite_start]4. การตั้งค่า Security (RBAC/Viewer) [cite: 126]

[cite_start]ระบบนี้ใช้ Grafana ในการจัดการผู้ใช้ (Viewer/Admin) [cite: 23]

1.  Login ด้วย `admin`
2.  ไปที่เมนู 'Server Admin' (รูปโล่) > 'Users'
3.  คลิก 'New user'
4.  สร้างผู้ใช้ใหม่ เช่น:
    * Name: `Demo Viewer`
    * Login: `viewer`
    * Password: `viewer`
5.  ไปที่เมนู 'Dashboards' (รูปสี่เหลี่ยม 4 ช่อง)
6.  ค้นหาโฟลเดอร์ 'Log Management' คลิก 'Permissions'
7.  เพิ่ม `viewer` และให้สิทธิ์ 'View'
8.  Logout และลอง Login ด้วย `viewer` จะพบว่าสามารถดู Dashboard ได้อย่างเดียว แต่แก้ไขไม่ได้