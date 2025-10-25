# /docs/setup_saas.md
# คู่มือการติดตั้ง (SaaS/Cloud Mode)

โหมด SaaS มีขั้นตอนการติดตั้งพื้นฐานเหมือนกับ Appliance Mode (ใช้ `docker-compose`) แต่มีข้อแตกต่างสำคัญคือ **การเปิดใช้งาน HTTPS (TLS)**

## 1. ข้อกำหนด (Prerequisites)
* ทุกอย่างเหมือน Appliance Mode
* **Cloud VM** (เช่น AWS EC2, DigitalOcean) ที่มี Public IP
* **Domain Name** (เช่น `logs.your-company.com`) ที่ชี้ A Record มายัง Public IP ของ VM

## 2. ขั้นตอนการติดตั้ง

1.  SSH เข้าไปยัง Cloud VM
2.  ติดตั้ง `git`, `docker`, `docker-compose`
3.  Clone repository และรัน `docker-compose up -d` (เหมือน Appliance)

## [cite_start]3. การตั้งค่า HTTPS (TLS) 

เราจะไม่เปิดพอร์ต 3000 (Grafana) และ 8080 (Ingestor) สู่สาธารณะโดยตรง แต่จะใช้ **Reverse Proxy** (เช่น Nginx หรือ Caddy) เพื่อ:
1.  รับการเชื่อมต่อที่ Port 443 (HTTPS)
2.  จัดการ SSL Certificate (แนะนำ Let's Encrypt)
3.  ส่งต่อ (proxy) traffic ไปยัง Service ภายใน

### ตัวอย่าง: ใช้ Nginx เป็น Reverse Proxy

1.  ติดตั้ง Nginx บน VM: `sudo apt install nginx`
2.  ติดตั้ง Certbot (สำหรับ Let's Encrypt): `sudo apt install certbot python3-certbot-nginx`
3.  ขอ Certificate: `sudo certbot --nginx -d logs.your-company.com`
4.  Certbot จะแก้ไข Config Nginx ให้อัตโนมัติ เราเพียงแค่เพิ่มส่วน `location`

**ตัวอย่าง Nginx Config (`/etc/nginx/sites-available/default`):**
```nginx
server {
    server_name logs.your-company.com;

    # UI/Dashboard (Grafana)
    location / {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API Ingestor
    location /ingest {
        proxy_pass http://localhost:8080/ingest;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # (Certbot จะเพิ่มส่วน SSL ด้านล่างนี้ให้)
    listen 443 ssl; 
    ssl_certificate /etc/letsencrypt/live/[logs.your-company.com/fullchain.pem](https://logs.your-company.com/fullchain.pem);
    ssl_certificate_key /etc/letsencrypt/live/[logs.your-company.com/privkey.pem](https://logs.your-company.com/privkey.pem);
    # ...
}