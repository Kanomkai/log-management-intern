# backend/normalize.py
import re
from datetime import datetime, timezone
from models import Log

# Regex สำหรับ Syslog ง่ายๆ (ตามตัวอย่าง [cite: 45])
# <134>Aug 20 12:44:56 fw01 vendor demo product ngfw action=deny...
SYSLOG_REGEX = re.compile(r"^\<\d+\>([\w\s:]+) ([\w\.-]+) (.*)")
# Regex สำหรับ Key=Value ใน Syslog [cite: 45]
KVP_REGEX = re.compile(r"(\w+)=([^$\s]+|\"[^\"]+\")")

# ฟิลด์หลักที่เราจะดึงออกมาใส่คอลัมน์โดยเฉพาะ
PRIMARY_FIELDS = [
    "@timestamp", "tenant", "source", "event_type", 
    "severity", "action", "src_ip", "dst_ip", "user"
]

def parse_timestamp(ts_str: str) -> datetime:
    """พยายามแปลง String เวลา ให้เป็น datetime object ที่มี Timezone"""
    if not ts_str:
        return datetime.now(timezone.utc)
    try:
        # ลองแบบ RFC3339 / ISO 8601 (เช่น 2025-08-20T07:20:00Z [cite: 57])
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            # ลองแบบ Syslog (Aug 20 12:44:56)
            # ต้องเพิ่มปีปัจจุบันและ Timezone (สมมติว่าเป็น UTC)
            dt = datetime.strptime(ts_str, "%b %d %H:%M:%S")
            dt = dt.replace(year=datetime.now().year, tzinfo=timezone.utc)
            return dt
        except Exception:
            # ถ้าพลาดหมด ใช้เวลาปัจจุบัน
            return datetime.now(timezone.utc)

def normalize_log(raw_data: dict | str, default_tenant: str, default_source: str) -> Log | None:
    """
    หัวใจหลัก: แปลง log ดิบ (dict หรือ str) ให้เป็น Log object
    """
    data = {}
    
    if isinstance(raw_data, str):
        # --- 1. ถ้าเป็น String (สันนิษฐานว่าเป็น Syslog) ---
        match = SYSLOG_REGEX.match(raw_data)
        if not match:
            # ถ้าไม่ตรง pattern เลย ให้เก็บเป็น raw
            data['raw'] = raw_data
            data['source'] = default_source
            data['host'] = "unknown"
        else:
            # ถ้าตรง [cite: 45, 47]
            data['@timestamp'] = match.group(1) # "Aug 20 12:44:56"
            data['host'] = match.group(2) # "fw01"
            message = match.group(3)
            data['raw'] = message
            
            # ลองแยก Key=Value [cite: 45]
            try:
                kv_pairs = dict(KVP_REGEX.findall(message))
                # เอา $ หรือ " ออกจาก value
                kv_pairs = {k: v.strip('"$') for k, v in kv_pairs.items()}
                data.update(kv_pairs)
            except Exception:
                pass # ถ้าแยก KVP ไม่ได้ ก็ไม่เป็นไร
        
        data.setdefault('source', default_source)
        data.setdefault('tenant', default_tenant)

    elif isinstance(raw_data, dict):
        # --- 2. ถ้าเป็น Dict (จาก HTTP JSON) ---
        data = raw_data.copy()
        data.setdefault('source', default_source)
        # ถ้าใน JSON มี tenant, ให้ใช้ค่านั้น [cite: 51, 61, 72, 81, 93]
        data.setdefault('tenant', data.get('tenant', default_tenant))
        # เก็บ log ดิบ (ถ้าใน JSON ไม่มี)
        if 'raw' not in data:
            data['raw'] = str(raw_data) # เก็บ JSON string

    else:
        return None # ไม่รองรับ

    # --- 3. ทำ Normalization ลง Schema กลาง  ---
    
    # สร้าง dict สำหรับคอลัมน์หลัก
    log_model_data = {}
    # สร้าง dict สำหรับ data (JSONB)
    jsonb_data = {}

    # แปลง Timestamp
    ts_str = data.get("@timestamp", "")
    log_model_data["timestamp"] = parse_timestamp(ts_str)

    # แมปปิงข้อมูล
    log_model_data["tenant"] = data.get("tenant", default_tenant)
    log_model_data["source"] = data.get("source", default_source)
    log_model_data["event_type"] = data.get("event_type", data.get("eventName")) # สำหรับ AWS [cite: 78]
    log_model_data["severity"] = data.get("severity")
    log_model_data["action"] = data.get("action")
    log_model_data["src_ip"] = data.get("src_ip", data.get("src"))
    log_model_data["dst_ip"] = data.get("dst_ip", data.get("dst"))
    log_model_data["user"] = data.get("user")

    # เอาฟิลด์ที่เหลือทั้งหมด ยัดใส่ data (JSONB)
    for key, value in data.items():
        if key not in PRIMARY_FIELDS:
            jsonb_data[key] = value

    log_model_data["data"] = jsonb_data
    
    # สร้าง Log object
    return Log(**log_model_data)