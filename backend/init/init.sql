-- backend/init/init.sql (เวอร์ชัน simplified)

-- เปิด Extension (เผื่อต้องใช้)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- สร้างตาราง 'logs' แบบธรรมดา (ไม่แบ่งพาร์ติชั่น)
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- คอลัมน์หลักสำหรับกรอง
    "@timestamp" TIMESTAMPTZ NOT NULL,
    tenant VARCHAR(255) NOT NULL,
    source VARCHAR(255),
    event_type VARCHAR(255),
    severity SMALLINT,
    action VARCHAR(50),
    src_ip INET,
    dst_ip INET,
    "user" VARCHAR(255),

    -- คอลัมน์ JSONB เก็บฟิลด์ที่เหลือทั้งหมด
    data JSONB
);

-- สร้าง Indexes
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs ("@timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_logs_tenant ON logs (tenant);
CREATE INDEX IF NOT EXISTS idx_logs_source ON logs (source);
CREATE INDEX IF NOT EXISTS idx_logs_event_type ON logs (event_type);

-- สร้าง GIN Index สำหรับค้นหาใน JSONB
CREATE INDEX IF NOT EXISTS idx_logs_data_gin ON logs USING GIN (data);

-- (เราลบส่วน Partitioned ทั้งหมดออกไป)