"""
Outbox Repository - Manejo de cola de mensajes de salida para Tasker
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class OutboxRepository:
    """Repositorio para operaciones de cola de mensajes de salida"""
    
    def __init__(self):
        """Inicializa el repositorio con conexión a MySQL"""
        self.db_url = os.getenv("DB_URL", "mysql+pymysql://user:password@localhost/mgcomputacion")
        self.engine = None
        self.Session = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Configura la conexión a la base de datos"""
        try:
            self.engine = create_engine(
                self.db_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Conexión a base de datos configurada correctamente para OutboxRepository")
        except Exception as e:
            logger.error(f"Error configurando conexión a BD en OutboxRepository: {str(e)}")
            raise
    
    def lease_messages(self, company_id: int, limit: int = 10, reserved_by: str = "tasker") -> List[Dict[str, Any]]:
        """
        Obtiene mensajes pendientes de envío (lease)
        
        Args:
            company_id: ID de la compañía
            limit: Número máximo de mensajes a obtener
            reserved_by: Identificador de quien está tomando los mensajes
            
        Returns:
            Lista de mensajes para enviar
        """
        try:
            with self.engine.connect() as conn:
                # Obtener mensajes pendientes ordenados por prioridad y fecha
                query = text("""
                    SELECT id, company_id, telefono, mensaje, priority, status, created_at
                    FROM outbox_messages 
                    WHERE company_id = :company_id 
                    AND status = 'queued'
                    ORDER BY priority ASC, created_at ASC
                    LIMIT :limit
                """)
                
                result = conn.execute(query, {
                    "company_id": company_id,
                    "limit": limit
                })
                
                messages = []
                message_ids = []
                
                for row in result:
                    message = {
                        "id": row.id,
                        "company_id": row.company_id,
                        "telefono": row.telefono,
                        "mensaje": row.mensaje,
                        "priority": row.priority,
                        "status": row.status,
                        "created_at": row.created_at.isoformat() if row.created_at else None
                    }
                    messages.append(message)
                    message_ids.append(row.id)
                
                # Marcar mensajes como reservados
                if message_ids:
                    update_query = text("""
                        UPDATE outbox_messages 
                        SET status = 'reserved',
                            reserved_by = :reserved_by,
                            reserved_at = NOW()
                        WHERE id IN :message_ids
                    """)
                    
                    conn.execute(update_query, {
                        "reserved_by": reserved_by,
                        "message_ids": tuple(message_ids)
                    })
                    conn.commit()
                
                logger.info(f"Leased {len(messages)} messages for company {company_id}")
                return messages
                
        except SQLAlchemyError as e:
            logger.error(f"Error leasing messages: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado leasing messages: {str(e)}")
            return []
    
    def acknowledge_message(self, message_id: int, success: bool = True, error_message: str = None) -> bool:
        """
        Confirma el envío de un mensaje (ack)
        
        Args:
            message_id: ID del mensaje
            success: True si se envió exitosamente, False si falló
            error_message: Mensaje de error si falló
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            with self.engine.connect() as conn:
                if success:
                    # Marcar como enviado
                    query = text("""
                        UPDATE outbox_messages 
                        SET status = 'sent',
                            sent_at = NOW()
                        WHERE id = :message_id AND status = 'reserved'
                    """)
                    conn.execute(query, {"message_id": message_id})
                else:
                    # Marcar como fallido
                    query = text("""
                        UPDATE outbox_messages 
                        SET status = 'failed',
                            failed_at = NOW(),
                            last_error = :error_message,
                            send_attempts = send_attempts + 1
                        WHERE id = :message_id AND status = 'reserved'
                    """)
                    conn.execute(query, {
                        "message_id": message_id,
                        "error_message": error_message or "Unknown error"
                    })
                
                conn.commit()
                logger.info(f"Message {message_id} acknowledged: success={success}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error acknowledging message {message_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado acknowledging message {message_id}: {str(e)}")
            return False
    
    def add_message(self, company_id: int, telefono: str, mensaje: str, priority: int = 5) -> bool:
        """
        Agrega un nuevo mensaje a la cola de salida
        
        Args:
            company_id: ID de la compañía
            telefono: Número de teléfono destino
            mensaje: Contenido del mensaje
            priority: Prioridad del mensaje (1=alta, 5=media, 10=baja)
            
        Returns:
            True si se agregó correctamente
        """
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO outbox_messages (company_id, telefono, mensaje, priority, status)
                    VALUES (:company_id, :telefono, :mensaje, :priority, 'queued')
                """)
                
                conn.execute(query, {
                    "company_id": company_id,
                    "telefono": telefono,
                    "mensaje": mensaje,
                    "priority": priority
                })
                conn.commit()
                
                logger.info(f"Message added to outbox for company {company_id}, phone {telefono}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error adding message to outbox: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado adding message to outbox: {str(e)}")
            return False
    
    def get_queue_status(self, company_id: int) -> Dict[str, Any]:
        """
        Obtiene el estado de la cola de mensajes para una compañía
        
        Args:
            company_id: ID de la compañía
            
        Returns:
            Diccionario con estadísticas de la cola
        """
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT 
                        status,
                        COUNT(*) as count,
                        MIN(created_at) as oldest_message,
                        MAX(created_at) as newest_message
                    FROM outbox_messages 
                    WHERE company_id = :company_id
                    GROUP BY status
                """)
                
                result = conn.execute(query, {"company_id": company_id})
                
                stats = {
                    "queued": 0,
                    "reserved": 0,
                    "sent": 0,
                    "failed": 0,
                    "total": 0,
                    "oldest_message": None,
                    "newest_message": None
                }
                
                for row in result:
                    status = row.status
                    count = row.count
                    stats[status] = count
                    stats["total"] += count
                    
                    if row.oldest_message:
                        oldest_iso = row.oldest_message.isoformat()
                        if not stats["oldest_message"] or oldest_iso < stats["oldest_message"]:
                            stats["oldest_message"] = oldest_iso
                    if row.newest_message:
                        newest_iso = row.newest_message.isoformat()
                        if not stats["newest_message"] or newest_iso > stats["newest_message"]:
                            stats["newest_message"] = newest_iso
                
                return stats
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting queue status: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error inesperado getting queue status: {str(e)}")
            return {}

# Instancia global
outbox_repo = OutboxRepository()
