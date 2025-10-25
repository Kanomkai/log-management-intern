# backend/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

# 1. โหลด Environment Variables
class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", 
                                  "postgresql+asyncpg://user:password@localhost:5432/logdb")

settings = Settings()

# 2. สร้าง "Engine" สำหรับเชื่อมต่อ
#    นี่คือจุดเชื่อมต่อหลักไปยัง PostgreSQL
engine = create_async_engine(settings.DATABASE_URL)

# 3. สร้าง "Session Factory"
#    เราจะใช้ตัวนี้เพื่อสร้าง Session (การเชื่อมต่อชั่วคราว)
#    สำหรับแต่ละ request หรือ background task
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 4. ฟังก์ชัน (Dependency) สำหรับ FastAPI
#    เพื่อขอ DB Session ใหม่ทุกครั้งที่มีการเรียก API
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()