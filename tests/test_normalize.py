import sys
import os
import pytest
from datetime import datetime, timezone

# --- Path Hack ---
# นี่คือ "ท่า" มาตรฐานของ Python เพื่อ "อนุญาต" ให้ไฟล์ test นี้
# "มองเห็น" และ "import" โค้ดที่อยู่ในโฟลเดอร์ 'backend' ได้
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
# -----------------

# (ตอนนี้เราสามารถ import จาก backend ได้แล้ว)
from normalize import normalize_log
from models import Log # (จำเป็นต้อง import เพื่อให้ normalize_log ทำงานได้)

# --- Test Case 1: ทดสอบ HTTP JSON (จากโจทย์ [cite: 48-57]) ---
def test_normalize_http_json():
    raw_log = {
        "tenant": "demo",
        "source": "api",
        "event_type": "app_login_failed",
        "user": "alice",
        "@timestamp": "2025-08-20T07:20:00Z"
    }
    log_obj = normalize_log(raw_log, default_tenant="default", default_source="http")
    
    # ตรวจสอบว่าแปลงค่าหลักๆ ถูกต้อง
    assert log_obj is not None
    assert log_obj.tenant == "demo"
    assert log_obj.source == "api"
    assert log_obj.event_type == "app_login_failed"
    assert log_obj.user == "alice"
    assert log_obj.timestamp == datetime(2025, 8, 20, 7, 20, 0, tzinfo=timezone.utc)
    
    # ตรวจสอบว่า 'raw' ถูกเพิ่มเข้าไปใน 'data' (JSONB)
    assert 'raw' in log_obj.data

# --- Test Case 2: ทดสอบ Syslog (จากโจทย์ [cite: 44-45]) ---
def test_normalize_syslog_firewall():
    raw_log = "<134>Aug 20 12:44:56 fw01 vendor demo product ngfw action=deny src=10.0.1.10 dst=8.8.8.8"
    log_obj = normalize_log(raw_log, default_tenant="default_syslog", default_source="syslog")
    
    # ตรวจสอบว่าแปลงค่าหลักๆ ถูกต้อง
    assert log_obj is not None
    assert log_obj.tenant == "default_syslog"
    assert log_obj.source == "syslog"
    assert log_obj.action == "deny"
    assert log_obj.src_ip == "10.0.1.10"
    assert log_obj.dst_ip == "8.8.8.8"
    
    # ตรวจสอบว่า 'data' (JSONB) ถูกดึงค่า KVP (Key-Value Pair) มา
    assert log_obj.data['host'] == "fw01"
    assert log_obj.data['vendor'] == "demo"
    assert log_obj.data['product'] == "ngfw"

# --- Test Case 3: ทดสอบ Syslog (อีกรูปแบบ [cite: 46-47]) ---
def test_normalize_syslog_router():
    raw_log = "<190>Aug 20 13:01:02 r1 if ge-0/0/1 event link-down"
    log_obj = normalize_log(raw_log, default_tenant="default_syslog", default_source="syslog")
    
    assert log_obj is not None
    assert log_obj.tenant == "default_syslog"
    assert log_obj.data['host'] == "r1"
    assert log_obj.data['raw'] == "if ge-0/0/1 event link-down"