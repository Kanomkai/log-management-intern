# backend/Dockerfile

# 1. Base Image เป็น Python
FROM python:3.11-slim

# 2. ตั้งค่า Working Directory
WORKDIR /app

# 3. คัดลอกไฟล์ requirements.txt เข้ามาก่อน
COPY requirements.txt .

# 4. ติดตั้ง Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. คัดลอกโค้ดทั้งหมดใน backend/ เข้าไปใน /app
COPY . .

# 6. คำสั่งที่จะรันเมื่อ Container เริ่มทำงาน
#    uvicorn.run("main:app") หมายถึง รันตัวแปร app ที่อยู่ในไฟล์ main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]