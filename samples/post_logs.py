#!/usr/bin/env python3
#
# สคริปต์ส่งไฟล์ JSON ตัวอย่างไปยัง Endpoint /ingest
#
# การใช้งาน:
#   python3 post_logs.py <tenant_id> <file1.json> [file2.json ...]
#
# ตัวอย่าง:
#   python3 post_logs.py demoA samples/crowdstrike.json samples/windows_ad.json
#   python3 post_logs.py demoB samples/aws_cloudtrail.json samples/m365_audit.json

import requests
import json
import sys
import os

URL = "http://localhost:8080/ingest"

def send_log_file(tenant_id, filepath):
    if not os.path.exists(filepath):
        print(f"Error: File not found '{filepath}'")
        return

    print(f"Sending '{filepath}' to tenant '{tenant_id}'...")
    
    with open(filepath, 'r') as f:
        try:
            payload = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filepath}: {e}")
            return
            
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": tenant_id # ส่ง Tenant ID ผ่าน Header
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload)
        
        if response.status_code == 202:
            print(f"Success (202): {response.json().get('message')}")
        else:
            print(f"Failed ({response.status_code}): {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"Error: Connection refused. Is Ingestor running at {URL}?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 post_logs.py <tenant_id> <file1.json> [file2.json ...]")
        sys.exit(1)
        
    tenant = sys.argv[1]
    files = sys.argv[2:]
    
    for f in files:
        send_log_file(tenant, f)