# backend/normalize.py (เวอร์ชันแก้บั๊กแล้ว)
import re
from datetime import datetime, timezone
from models import Log

# Regex สำหรับ Syslog (แบบ RFC3164 ที่เจาะจง 'เวลา' มากขึ้น)
SYSLOG_REGEX = re.compile(r"^\<\d+\>(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}) ([\w\.-]+) (.*)")
# Regex สำหรับ Key=Value ใน Syslog
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
        # ลองแบบ RFC3339 / ISO 8601
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            # ลองแบบ Syslog (Aug 20 12:44:56)
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
            # ถ้าตรง
            data['@timestamp'] = match.group(1) # "Aug 20 12:44:56"
            data['host'] = match.group(2) # "fw01"
            message = match.group(3)      # "vendor demo product ngfw action=deny..."
            data['raw'] = message
            
            # --- (⭐️ นี่คือ Logic ใหม่ที่แก้บั๊กแล้ว ⭐️) ---
            
            # 1. ก่อนอื่น, หา 'key=value' ทั้งหมด (เช่น action=deny)
            kv_pairs = {}
            try:
                kv_pairs = dict(KVP_REGEX.findall(message))
                kv_pairs = {k: v.strip('"$') for k, v in kv_pairs.items()}
                data.update(kv_pairs)
            except Exception:
                pass # ไม่เจอ KVP ก็ไม่เป็นไร
            
            # 2. ต่อไป, หา "ส่วนที่เหลือ" (ที่ไม่มี '=')
            
            # (ค้นหาว่า 'key=value' ตัวแรก เริ่มที่ index ไหน)
            first_kvp_match = KVP_REGEX.search(message)
            
            if first_kvp_match:
                # ถ้าเจอ KVP, ให้เอา "ข้อความ" (string) ที่อยู่ "ก่อนหน้า"
                space_part = message[:first_kvp_match.start()].strip()
            else:
                # (ถ้าไม่เจอ KVP เลย, ให้เอา "ทั้ง message")
                space_part = message.strip()

            # 3. "หั่น" (Parse) "ส่วนที่เหลือ" (เช่น "vendor demo product ngfw")
            words = space_part.split()
            # วนลูปทีละ "คู่" (key, value)
            i = 0
            while i + 1 < len(words):
                key = words[i]
                value = words[i+1]
                # เพิ่มลง data (ถ้าไม่ใช่ field หลัก)
                if key not in PRIMARY_FIELDS:
                    data[key] = value
                i += 2 # ข้ามไปคู่ถัดไป
            # --- (⭐️ จบ Logic ใหม่ ⭐️) ---
        
        data.setdefault('source', default_source)
        data.setdefault('tenant', default_tenant)

    elif isinstance(raw_data, dict):
        # --- 2. ถ้าเป็น Dict (จาก HTTP JSON) ---
        data = raw_data.copy()
        data.setdefault('source', default_source)
        data.setdefault('tenant', data.get('tenant', default_tenant))
        if 'raw' not in data:
            data['raw'] = str(raw_data)

    else:
        return None # ไม่รองรับ

    # --- 3. ทำ Normalization ลง Schema กลาง ---
    
    log_model_data = {}
    jsonb_data = {}

    ts_str = data.get("@timestamp", "")
    log_model_data["timestamp"] = parse_timestamp(ts_str)

    log_model_data["tenant"] = data.get("tenant", default_tenant)
    log_model_data["source"] = data.get("source", default_source)
    log_model_data["event_type"] = data.get("event_type", data.get("eventName"))
    log_model_data["severity"] = data.get("severity")
    log_model_data["action"] = data.get("action")
    log_model_data["src_ip"] = data.get("src_ip", data.get("src"))
    log_model_data["dst_ip"] = data.get("dst_ip", data.get("dst"))
    log_model_data["user"] = data.get("user")

    for key, value in data.items():
        if key not in PRIMARY_FIELDS:
            jsonb_data[key] = value

    log_model_data["data"] = jsonb_data
    
    return Log(**log_model_data)