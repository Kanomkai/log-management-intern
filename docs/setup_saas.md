# /docs/setup_saas.md
# คู่มือการติดตั้ง (SaaS/Cloud Mode) - (เวอร์ชัน Ngrok Tunnel)

คู่มือนี้อธิบายการติดตั้งในโหมด SaaS (Software as a Service) หรือการทำให้ระบบทดสอบได้จากภายนอก โดยใช้วิธีที่รวดเร็วที่สุดคือ **Ngrok (Tunneling)**

วิธีนี้จะสร้าง "อุโมงค์" (Tunnel) ที่ปลอดภัยจากเครื่องของคุณ (`localhost`) ออกไปยังอินเทอร์เน็ต และสร้าง URL สาธารณะ (เช่น `tonja-unexuded-noncriminally.ngrok-free.dev`) ให้กรรมการสามารถเข้าถึงระบบของคุณ (ที่รันบนเครื่องคุณ) ได้จากภายนอก

## 1. ข้อกำหนดขั้นต่ำ (Prerequisites)

* **ระบบ Appliance ต้องรันอยู่:** คุณต้องรันโหมด Appliance (`docker compose up -d`) บนเครื่องของคุณจนสำเร็จก่อน
* **โปรแกรม Ngrok:** ดาวน์โหลด `ngrok` (เวอร์ชันฟรี) ได้ที่ [https://ngrok.com/download](https://ngrok.com/download)
* **(แนะนำ) บัญชี Ngrok (ฟรี):** การสมัครบัญชีฟรีจะทำให้คุณสามารถเปิด "อุโมงค์" (Tunnel) ได้ 2 ช่องพร้อมกัน (ช่องหนึ่งสำหรับ Grafana, อีกช่องสำหรับ API Ingestor)

## 2. ขั้นตอนการติดตั้ง (Installation)

### ขั้นตอนที่ 1: รันระบบ Appliance (บนเครื่อง)

ตรวจสอบให้แน่ใจว่าระบบหลักของคุณทำงานอยู่:

```bash
# (รันใน Terminal ที่ 1)
docker compose up -d