#!/bin/bash
#
# สคริปต์ส่ง Test Syslog ไปยัง Port 514
#
# $1: ข้อความ (ถ้าไม่ระบุ จะใช้ข้อความตัวอย่าง)

HOST="localhost"
PORT=514

# [cite_start]ข้อความตัวอย่างจากโจทย์ [cite: 45]
MESSAGE=${1:-"<134>Aug 20 12:44:56 fw01 vendor demo product ngfw action=deny src=10.0.1.10 dst=8.8.8.8 spt=5353 dpt=53 proto=udp msg=DNS blocked policy Block-DNS"}

echo "Sending Syslog to $HOST:$PORT..."
# ใช้ nc (netcat) เพื่อส่งข้อความเป็น UDP (-u)
# -w 1 คือรอ 1 วินาที
echo $MESSAGE | nc -u -w 1 $HOST $PORT

echo "Done."