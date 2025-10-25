# backend/syslog_server.py
import asyncio
import logging
from database import AsyncSessionLocal
from normalize import normalize_log

logger = logging.getLogger("ingestor.syslog")

class SyslogProtocol(asyncio.DatagramProtocol):
    """
    Protocol ที่ asyncio จะใช้เมื่อมีข้อมูล UDP เข้ามา
    """
    def connection_made(self, transport):
        logger.info("Syslog UDP connection established.")
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple):
        """
        นี่คือฟังก์ชันที่จะทำงาน "ทุกครั้ง" ที่มี log 1 บรรทัดยิงเข้ามา
        """
        try:
            message = data.decode('utf-8').strip()
            # addr[0] คือ IP ของเครื่องที่ส่งมา
            logger.debug(f"Received syslog from {addr[0]}: {message}")
            
            # เราต้องสร้าง task ใหม่เพื่อทำงานกับ DB
            # เพราะเราไม่สามารถ 'await' ในฟังก์ชันนี้ได้
            asyncio.create_task(self.process_and_save(message, addr[0]))

        except UnicodeDecodeError:
            logger.warning(f"Failed to decode syslog message from {addr}: {data}")
        except Exception as e:
            logger.error(f"Error processing datagram: {e}")

    async def process_and_save(self, message: str, ip: str):
        """
        ฟังก์ชัน Async สำหรับ Normalize และบันทึกลง DB
        """
        # สมมติ tenant 'default' และ source 'syslog'
        # ในระบบจริง อาจจะต้อง map IP 'ip' นี้กับ tenant
        log_obj = normalize_log(message, default_tenant="default_syslog", default_source="syslog")
        
        if log_obj:
            # เราต้องสร้าง DB Session ใหม่ทุกครั้ง
            # เพราะนี่คือ background task ไม่ใช่ HTTP request
            async with AsyncSessionLocal() as session:
                try:
                    session.add(log_obj)
                    await session.commit()
                    logger.debug(f"Saved syslog from {ip}")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Failed to save syslog: {e}")

    def connection_lost(self, exc):
        logger.warning("Syslog UDP connection lost.")


async def start_syslog_server(host="0.0.0.0", port=514):
    """
    ฟังก์ชันสำหรับเริ่ม Syslog Server
    """
    loop = asyncio.get_running_loop()
    try:
        await loop.create_datagram_endpoint(
            lambda: SyslogProtocol(),
            local_addr=(host, port)
        )
        logger.info(f"Syslog UDP Server started on {host}:{port}")
    except PermissionError:
        logger.error(f"Permission denied for binding to port {port}. "
                     "Try running with sudo or using a port > 1024.")
    except Exception as e:
        logger.error(f"Failed to start Syslog server: {e}")