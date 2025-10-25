# backend/models.py
from sqlalchemy import Column, String, DateTime, Index, text, SMALLINT
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# คลาสนี้ต้องตรงกับตารางใน init.sql
class Log(Base):
    __tablename__ = 'logs'
    
    # เรากำหนดคอลัมน์หลักตาม init.sql
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    
    # คอลัมน์หลักที่เราดึงออกมาเพื่อ Index
    timestamp = Column("@timestamp", DateTime(timezone=True), nullable=False)
    tenant = Column(String(255), nullable=False)
    source = Column(String(255))
    event_type = Column(String(255))
    severity = Column(SMALLINT)
    action = Column(String(50))
    src_ip = Column(INET)
    dst_ip = Column(INET)
    user = Column(String(255))
    
    # คอลัมน์ JSONB ที่เก็บทุกอย่างที่เหลือ
    data = Column(JSONB)

    # ระบุ Index (เพื่อให้ SQLAlchemy รู้จัก)
    __table_args__ = (
        Index('idx_logs_timestamp', timestamp.desc()),
        Index('idx_logs_tenant', tenant),
        Index('idx_logs_source', source),
        Index('idx_logs_event_type', event_type),
        Index('idx_logs_data_gin', data, postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<Log(tenant='{self.tenant}', source='{self.source}', ts='{self.timestamp}')>"