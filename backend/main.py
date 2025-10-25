# backend/main.py
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
# --- Import จากไฟล์ของเรา ---
from database import engine, get_db_session
from models import Log
from normalize import normalize_log
from syslog_server import start_syslog_server
# --- ตั้งค่า Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ingestor.http")

# --- FastAPI Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Ingestor Service...")
    
    # 1. ทดสอบการเชื่อมต่อ Database
    try:
        async with engine.connect() as conn:
            await conn.run_sync(lambda sync_conn: None) # Run a no-op
        logger.info("Database connection successful.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # อาจจะเลือกที่จะไม่ start ถ้า DB ต่อไม่ได้
        # raise e 
    
    # 2. เริ่มต้น Syslog Server ใน Background
    asyncio.create_task(start_syslog_server())
    
    yield
    
    # --- ส่วน Shutdown ---
    logger.info("Shutting Down Ingestor Service...")
    await engine.dispose() # ปิด DB connection pool

# --- สร้างแอป FastAPI ---
app = FastAPI(
    title="Log Management Ingestor",
    lifespan=lifespan
)

# --- Endpoint 1: Health Check ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Ingestor service is running"}

# --- Endpoint 2: HTTP Ingest (JSON) [cite: 13, 20] ---
@app.post("/ingest", status_code=202)
async def http_ingest(
    request: Request,
    payload: Dict[str, Any] | List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db_session)
):
    """
    รับ Log แบบ JSON ทั้งแบบเดี่ยว (dict) หรือแบบชุด (list)
    """
    # 1. ดึง Tenant จาก Header [cite: 23]
    #    นี่จะเป็น "default" หากใน payload ไม่มีระบุ
    tenant = request.headers.get("X-Tenant-ID", "default_http")
    
    if isinstance(payload, list):
        logs_data = payload
    else:
        logs_data = [payload] # ทำให้เป็น list เสมอ

    # 2. Normalize และเตรียมบันทึก
    log_objects = []
    for raw_log in logs_data:
        if not isinstance(raw_log, dict):
            logger.warning(f"Skipping invalid log item (not a dict): {raw_log}")
            continue
        
        # ส่ง tenant ที่ได้จาก header เป็นค่าเริ่มต้น
        log_obj = normalize_log(raw_log, default_tenant=tenant, default_source="http")
        if log_obj:
            log_objects.append(log_obj)

    # 3. บันทึกลง DB
    if not log_objects:
        raise HTTPException(status_code=400, detail="No valid log data found")
        
    try:
        db.add_all(log_objects)
        await db.commit()
        logger.info(f"Successfully ingested {len(log_objects)} logs for tenant '{tenant}'.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save HTTP logs: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {"message": f"Accepted {len(log_objects)} logs"}