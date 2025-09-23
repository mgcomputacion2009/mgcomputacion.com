"""
Repositorio para persistir eventos de orquestador/webhooks
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class EventsRepository:
    def __init__(self) -> None:
        self.db_url = os.getenv("DB_URL", "mysql+pymysql://user:password@localhost/mgcomputacion")
        self.engine = create_engine(self.db_url, pool_pre_ping=True, pool_recycle=3600, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def log_event(self, compania_id: Optional[int], session_id: Optional[str], tipo: str, payload: Dict[str, Any]) -> None:
        session = None
        try:
            session = self.Session()
            query = text(
                """
                INSERT INTO eventos (compania_id, session_id, tipo, payload)
                VALUES (:compania_id, :session_id, :tipo, :payload)
                """
            )
            payload_json = json.dumps(payload, ensure_ascii=False)
            session.execute(query, {
                "compania_id": compania_id,
                "session_id": session_id,
                "tipo": tipo,
                "payload": payload_json
            })
            session.commit()
            logger.info(f"Evento registrado: {tipo} (compania_id={compania_id})")
        except SQLAlchemyError as e:
            logger.error(f"Error insertando evento: {e}")
            if session:
                session.rollback()
        except Exception as e:
            logger.error(f"Error inesperado insertando evento: {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()

    def list_events(self, compania_id: Optional[int], limit: int = 50) -> List[Dict[str, Any]]:
        session = None
        try:
            session = self.Session()
            if compania_id is not None:
                query = text(
                    """
                    SELECT id, ts, compania_id, session_id, tipo, payload
                    FROM eventos
                    WHERE compania_id = :compania_id
                    ORDER BY ts DESC
                    LIMIT :limit
                    """
                )
                rows = session.execute(query, {"compania_id": compania_id, "limit": limit}).fetchall()
            else:
                query = text(
                    """
                    SELECT id, ts, compania_id, session_id, tipo, payload
                    FROM eventos
                    ORDER BY ts DESC
                    LIMIT :limit
                    """
                )
                rows = session.execute(query, {"limit": limit}).fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                out.append({
                    "id": int(r[0]),
                    "ts": str(r[1]),
                    "compania_id": int(r[2]) if r[2] is not None else None,
                    "session_id": r[3],
                    "tipo": r[4],
                    "payload": json.loads(r[5]) if r[5] else None,
                })
            return out
        except SQLAlchemyError as e:
            logger.error(f"Error listando eventos: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado listando eventos: {e}")
            return []
        finally:
            if session:
                session.close()


events_repo = EventsRepository()


