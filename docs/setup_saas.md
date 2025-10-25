# /docs/setup_saas.md
# คู่มือการติดตั้ง (SaaS/Cloud Mode)

[cite_start]คู่มือนี้อธิบายการติดตั้ง Demo Log Management ในโหมด SaaS (Software as a Service) หรือ Cloud [cite: 2, 25] [cite_start]ซึ่งมีขั้นตอนพื้นฐานเหมือนกับ Appliance Mode (ใช้ `docker-compose`) แต่มีข้อแตกต่างสำคัญคือ **การเปิดใช้งาน HTTPS (TLS)** เพื่อให้ผู้ใช้เข้าถึงจากภายนอกได้อย่างปลอดภัย [cite: 26]

## 1. ข้อกำหนดขั้นต่ำ (Prerequisites)

* ทุกอย่างเหมือน `setup_appliance.md` (Docker, Docker Compose)
* **Cloud VM:** เครื่องเซิร์ฟเวอร์เสมือน (VM) บนคลาวด์สาธารณะ (เช่น AWS EC2, DigitalOcean, Vultr, Linode) ที่มี Public IP
* **Domain Name:** (เช่น `logs.your-company.com`) ที่ตั้งค่า DNS (A Record) ชี้มายัง Public IP ของ VM ของคุณ

## 2. ขั้นตอนการติดตั้ง (Installation)

1.  SSH เข้าไปยัง Cloud VM (เช่น `ssh root@<Your-Public-IP>`)
2.  ติดตั้ง `git`, `docker`, และ `docker-compose` (หรือ `docker compose`) บน VM
3.  Clone Repository นี้:
    ```bash
    git clone [Your Git Repository URL]
    cd log-management-intern
    ```
4.  สร้างไฟล์ `.env` จากตัวอย่าง:
    ```bash
    cp .env.example .env
    ```
5.  รันระบบทั้งหมดใน background:
    ```bash
    docker compose up -d
    ```
6.  **(สำคัญ!)** ตรวจสอบว่า Firewall (เช่น `ufw` หรือ Security Group ของ Cloud) เปิดพอร์ตที่จำเป็น:
    * `22` (สำหรับ SSH)
    * `80` (สำหรับ HTTP - ใช้ยืนยันตัวตน SSL)
    * `443` (สำหรับ HTTPS - การใช้งานจริง)

## 3. การตั้งค่า HTTPS (TLS) ด้วย Reverse Proxy

เราจะไม่เปิดพอร์ต `3000` (Grafana) และ `8080` (Ingestor) สู่สาธารณะโดยตรง แต่จะใช้ **Reverse Proxy** (เช่น Nginx หรือ Caddy) เพื่อ:

1.  รับการเชื่อมต่อที่ Port 443 (HTTPS)
2.  จัดการ SSL Certificate (แนะนำให้ใช้ **Let's Encrypt** เพื่อขอ Certificate ฟรี)
3.  ส่งต่อ (proxy) traffic ไปยัง Service ภายใน (Internal) ที่รันบน Docker (ports `3000` และ `8080`)

### ตัวอย่าง: การตั้งค่าด้วย Nginx และ Certbot (Let's Encrypt)

1.  **ติดตั้ง Nginx และ Certbot บน VM (Ubuntu):**
    ```bash
    sudo apt update
    sudo apt install nginx python3-certbot-nginx
    ```

2.  **สร้างไฟล์ Config Nginx:**
    สร้างไฟล์ config ใหม่ที่ `/etc/nginx/sites-available/logmgmt`
    ```bash
    sudo nano /etc/nginx/sites-available/logmgmt
    ```

3.  **วาง (Paste) Config นี้ลงไป:**
    (อย่าลืมเปลี่ยน `logs.your-company.com` เป็น Domain Name จริงของคุณ)

    ```nginx
    server {
        listen 80;
        server_name logs.your-company.com;

        # ส่วนนี้สำหรับให้ Certbot มายืนยันตัวตน
        location ~ /.well-known/acme-challenge/ {
            allow all;
            root /var/www/html;
        }

        # Redirect HTTP ทั้งหมดไป HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl;
        server_name logs.your-company.com;

        # (Certbot จะเพิ่ม path ของ SSL Certificate ที่นี่ในภายหลัง)
        # ssl_certificate /path/to/fullchain.pem;
        # ssl_certificate_key /path/to/privkey.pem;

        location / {
            # Proxy ไปยัง Grafana UI (Port 3000)
            proxy_pass http://localhost:3000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # (จำเป็นสำหรับ WebSocket ของ Grafana)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /ingest {
            # Proxy ไปยัง FastAPI Ingestor (Port 8080)
            proxy_pass http://localhost:8080/ingest;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    ```

4.  **เปิดใช้งาน Config:**
    ```bash
    sudo ln -s /etc/nginx/sites-available/logmgmt /etc/nginx/sites-enabled/
    sudo nginx -t # ตรวจสอบว่า config ไม่ผิด
    sudo systemctl restart nginx
    ```

5.  **ขอ Certificate (SSL):**
    ```bash
    sudo certbot --nginx -d logs.your-company.com
    ```
    (Certbot จะถามคำถาม 2-3 ข้อ และจะ "แก้ไข" ไฟล์ config (`/etc/nginx/sites-available/logmgmt`) ให้อัตโนมัติ โดยการเติม path ของ SSL Certificate ให้)

## 4. การทดสอบโหมด SaaS

* **ทดสอบ UI:** เปิด `https://logs.your-company.com` (ต้องเป็น HTTPS และมีรูปกุญแจ 🔒)
* **ทดสอบ Ingestor:** แก้ไขสคริปต์ `samples/post_logs.py` โดยเปลี่ยน `URL` (บรรทัดที่ 12) ให้เป็น:
    `URL = "https://logs.your-company.com/ingest"`
    ...แล้วลองรันสคริปต์ `post_logs.py` จากเครื่องของคุณ

[cite_start](หมายเหตุ: การใช้ Self-signed certificate ก็เป็นที่ยอมรับ [cite: 26] หากสามารถอธิบายขั้นตอนการสร้าง (เช่น ด้วย `openssl`) และการติดตั้งใน Nginx ได้อย่างชัดเจน)