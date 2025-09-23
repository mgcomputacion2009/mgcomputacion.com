"""
Tenant Repository - Acceso a datos multi-tenant
"""

import os
import re
import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class TenantRepository:
    """Repositorio para operaciones multi-tenant"""
    
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
                echo=False  # No imprimir SQL en logs
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Conexión a base de datos configurada correctamente")
        except Exception as e:
            logger.error(f"Error configurando conexión a BD: {str(e)}")
            raise
    
    def normalize_phone(self, phone: str) -> str:
        """
        Normaliza número de teléfono (solo dígitos, quitar +, espacios)
        
        Args:
            phone: Número de teléfono a normalizar
            
        Returns:
            Número normalizado
        """
        if not phone:
            return ""
        
        # Quitar +, espacios, guiones, paréntesis
        normalized = re.sub(r'[+\s\-\(\)]', '', phone)
        
        # Solo dígitos
        normalized = re.sub(r'[^\d]', '', normalized)
        
        return normalized
    
    def get_secret(self, compania_id: int) -> Optional[str]:
        """
        Obtiene el secreto de webhook de una compañía
        """
        if not compania_id:
            logger.warning("compania_id vacío para get_secret")
            return None
        session = None
        try:
            session = self.Session()
            query = text("""
                SELECT ar_webhook_secret
                FROM compania_secrets
                WHERE compania_id = :compania_id
                LIMIT 1
            """)
            result = session.execute(query, {"compania_id": compania_id}).fetchone()
            if result and result[0]:
                logger.info(f"Secreto encontrado para compañía: {compania_id}")
                return str(result[0])
            logger.warning(f"Secreto no configurado para compañía: {compania_id}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error consultando secreto: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado consultando secreto: {str(e)}")
            return None
        finally:
            if session:
                session.close()

    def get_compania_id_by_device(self, device_alias: str, token: str) -> Optional[int]:
        """
        Obtiene el ID de compañía por dispositivo y token
        
        Args:
            device_alias: Alias del dispositivo
            token: Token de autenticación
            
        Returns:
            ID de la compañía o None si no se encuentra
        """
        if not device_alias or not token:
            logger.warning("device_alias o token vacíos")
            return None
        
        session = None
        try:
            session = self.Session()
            query = text("""
                SELECT compania_id 
                FROM ar_dispositivos 
                WHERE device_alias = :device_alias 
                AND token = :token 
                AND estado = 1
                LIMIT 1
            """)
            
            result = session.execute(query, {
                "device_alias": device_alias,
                "token": token
            }).fetchone()
            
            if result:
                compania_id = int(result[0])
                logger.info(f"Compañía encontrada por dispositivo: {compania_id}")
                return compania_id
            else:
                logger.warning(f"Dispositivo no encontrado: {device_alias}")
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Error consultando dispositivo: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado consultando dispositivo: {str(e)}")
            return None
        finally:
            if session:
                session.close()
    
    def get_compania_id_by_cliente(self, phone_cliente: str) -> Optional[int]:
        """
        Obtiene el ID de compañía por teléfono de cliente
        
        Args:
            phone_cliente: Número de teléfono del cliente
            
        Returns:
            ID de la compañía o None si no se encuentra
        """
        if not phone_cliente:
            logger.warning("phone_cliente vacío")
            return None
        
        # Normalizar número de teléfono
        normalized_phone = self.normalize_phone(phone_cliente)
        if not normalized_phone:
            logger.warning(f"No se pudo normalizar teléfono: {phone_cliente}")
            return None
        
        session = None
        try:
            session = self.Session()
            query = text("""
                SELECT compania_id 
                FROM wa_clientes_compania 
                WHERE phone_cliente = :phone_cliente
                LIMIT 1
            """)
            
            result = session.execute(query, {
                "phone_cliente": normalized_phone
            }).fetchone()
            
            if result:
                compania_id = int(result[0])
                logger.info(f"Compañía encontrada por cliente: {compania_id}")
                return compania_id
            else:
                logger.warning(f"Cliente no encontrado: {normalized_phone}")
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Error consultando cliente: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado consultando cliente: {str(e)}")
            return None
        finally:
            if session:
                session.close()
    
    def upsert_cliente_compania(self, phone_cliente: str, compania_id: int) -> None:
        """
        Inserta o actualiza la relación cliente-compañía
        
        Args:
            phone_cliente: Número de teléfono del cliente
            compania_id: ID de la compañía
        """
        if not phone_cliente or not compania_id:
            logger.warning("phone_cliente o compania_id vacíos")
            return
        
        # Normalizar número de teléfono
        normalized_phone = self.normalize_phone(phone_cliente)
        if not normalized_phone:
            logger.warning(f"No se pudo normalizar teléfono: {phone_cliente}")
            return
        
        session = None
        try:
            session = self.Session()
            query = text("""
                INSERT INTO wa_clientes_compania (phone_cliente, compania_id)
                VALUES (:phone_cliente, :compania_id)
                ON DUPLICATE KEY UPDATE compania_id = VALUES(compania_id)
            """)
            
            session.execute(query, {
                "phone_cliente": normalized_phone,
                "compania_id": compania_id
            })
            session.commit()
            
            logger.info(f"Cliente {normalized_phone} asociado a compañía {compania_id}")
            
        except SQLAlchemyError as e:
            logger.error(f"Error upserting cliente-compañía: {str(e)}")
            if session:
                session.rollback()
        except Exception as e:
            logger.error(f"Error inesperado upserting cliente-compañía: {str(e)}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
    
    def get_compania_info(self, compania_id: int) -> Optional[dict]:
        """
        Obtiene información de una compañía
        
        Args:
            compania_id: ID de la compañía
            
        Returns:
            Diccionario con información de la compañía o None
        """
        if not compania_id:
            logger.warning("compania_id vacío")
            return None
        
        session = None
        try:
            session = self.Session()
            query = text("""
                SELECT id, nombre, estado, creado_en 
                FROM companias 
                WHERE id = :compania_id
            """)
            
            result = session.execute(query, {
                "compania_id": compania_id
            }).fetchone()
            
            if result:
                return {
                    "id": int(result[0]),
                    "nombre": result[1],
                    "estado": int(result[2]),
                    "creado_en": result[3]
                }
            else:
                logger.warning(f"Compañía no encontrada: {compania_id}")
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Error consultando compañía: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado consultando compañía: {str(e)}")
            return None
        finally:
            if session:
                session.close()
    
    def get_company_config(self, compania_id: int) -> dict:
        """
        Carga configuración de la compañía.
        Si falta, retorna defaults globales.
        """
        defaults = {
            "prompts_version": "v1",
            "menu_productos": True,
            "cierre_venta": True,
            "envio_datos_pago": True,
            "panel_activo": True,
            "idioma": "es",
        }
        if not compania_id:
            logger.warning("compania_id vacío para get_company_config")
            return defaults
        session = None
        try:
            session = self.Session()
            query = text(
                """
                SELECT prompts_version, menu_productos, cierre_venta, envio_datos_pago, panel_activo, idioma
                FROM compania_config
                WHERE compania_id = :compania_id
                LIMIT 1
                """
            )
            result = session.execute(query, {"compania_id": compania_id}).fetchone()
            if result:
                cfg = {
                    "prompts_version": result[0] or defaults["prompts_version"],
                    "menu_productos": bool(result[1]),
                    "cierre_venta": bool(result[2]),
                    "envio_datos_pago": bool(result[3]),
                    "panel_activo": bool(result[4]),
                    "idioma": result[5] or defaults["idioma"],
                }
                logger.info(f"Config cargada para compañía {compania_id}: {cfg}")
                return cfg
            logger.warning(f"Config no encontrada para compañía: {compania_id}, usando defaults")
            return defaults
        except SQLAlchemyError as e:
            logger.error(f"Error consultando config: {str(e)}")
            return defaults
        except Exception as e:
            logger.error(f"Error inesperado consultando config: {str(e)}")
            return defaults
        finally:
            if session:
                session.close()
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión a la base de datos
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        session = None
        try:
            session = self.Session()
            session.execute(text("SELECT 1"))
            logger.info("Conexión a BD exitosa")
            return True
        except Exception as e:
            logger.error(f"Error probando conexión: {str(e)}")
            return False
        finally:
            if session:
                session.close()

# Instancia global del repositorio
tenant_repo = TenantRepository()
