#!/usr/bin/env python3
"""
Script para generar mensajes de prueba automáticamente
Se ejecuta cada vez que se acaban los mensajes en cola
"""

import mysql.connector
import time
import logging
from datetime import datetime
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/mgcomputacion/logs/generador_mensajes.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración de base de datos
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'mg',
    'password': 'MgPass123!',
    'database': 'mgapp',
    'port': 3306
}

def conectar_db():
    """Conectar a la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        return None

def contar_mensajes_queued(conn):
    """Contar mensajes en estado 'queued' para la empresa 1"""
    try:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM outbox_messages WHERE company_id = 1 AND status = 'queued'"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except mysql.connector.Error as e:
        logger.error(f"Error contando mensajes: {e}")
        return 0

def generar_mensaje_prueba(conn, numero_mensaje):
    """Generar un mensaje de prueba"""
    try:
        cursor = conn.cursor()
        
        mensaje = f"MENSAJE AUTOMÁTICO #{numero_mensaje}: Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Sistema funcionando correctamente"
        
        query = """
        INSERT INTO outbox_messages (company_id, telefono, mensaje, priority, status, created_at)
        VALUES (1, '584247810736', %s, 1, 'queued', NOW())
        """
        
        cursor.execute(query, (mensaje,))
        conn.commit()
        cursor.close()
        
        logger.info(f"Mensaje de prueba #{numero_mensaje} generado exitosamente")
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"Error generando mensaje de prueba: {e}")
        return False

def generar_lote_mensajes(conn, cantidad=10):
    """Generar un lote de mensajes de prueba con números de teléfono incrementales"""
    try:
        cursor = conn.cursor()
        
        # Obtener el siguiente número de mensaje
        query_count = "SELECT MAX(id) FROM outbox_messages WHERE company_id = 1"
        cursor.execute(query_count)
        max_id = cursor.fetchone()[0] or 0
        siguiente_numero = max_id + 1
        
        # Obtener el último dígito usado en teléfonos
        query_telefono = "SELECT telefono FROM outbox_messages WHERE company_id = 1 ORDER BY id DESC LIMIT 1"
        cursor.execute(query_telefono)
        ultimo_telefono = cursor.fetchone()
        
        if ultimo_telefono:
            # Extraer el último dígito del teléfono
            ultimo_digito = int(ultimo_telefono[0][-1])
        else:
            ultimo_digito = 0
        
        mensajes_generados = 0
        
        for i in range(cantidad):
            # Incrementar el último dígito del teléfono
            nuevo_digito = (ultimo_digito + i + 1) % 10  # Cicla del 0 al 9
            telefono = f"58424781073{nuevo_digito}"
            
            mensaje = f"MENSAJE AUTOMÁTICO #{siguiente_numero + i}: Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Teléfono: {telefono} - Sistema funcionando correctamente"
            
            query = """
            INSERT INTO outbox_messages (company_id, telefono, mensaje, priority, status, created_at)
            VALUES (1, %s, %s, 1, 'queued', NOW())
            """
            
            cursor.execute(query, (telefono, mensaje))
            mensajes_generados += 1
            logger.info(f"Mensaje #{siguiente_numero + i} generado para teléfono {telefono}")
        
        conn.commit()
        cursor.close()
        
        logger.info(f"Lote de {mensajes_generados} mensajes de prueba generado exitosamente")
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"Error generando lote de mensajes: {e}")
        return False

def verificar_y_generar():
    """Verificar si hay mensajes en cola y generar si es necesario"""
    conn = conectar_db()
    if not conn:
        return False
    
    try:
        # Contar mensajes en cola
        mensajes_queued = contar_mensajes_queued(conn)
        logger.info(f"Mensajes en cola: {mensajes_queued}")
        
        # Si hay menos de 2 mensajes, generar un lote
        if mensajes_queued < 2:
            logger.info("Generando lote de mensajes de prueba...")
            if generar_lote_mensajes(conn, 10):
                logger.info("✅ Lote de mensajes generado exitosamente")
                return True
            else:
                logger.error("❌ Error generando lote de mensajes")
                return False
        else:
            logger.info("✅ Suficientes mensajes en cola, no se necesita generar más")
            return True
            
    except Exception as e:
        logger.error(f"Error en verificación: {e}")
        return False
    finally:
        conn.close()

def main():
    """Función principal"""
    logger.info("🤖 Iniciando generador de mensajes de prueba...")
    
    # Crear directorio de logs si no existe
    Path('/var/www/mgcomputacion/logs').mkdir(exist_ok=True)
    
    if verificar_y_generar():
        logger.info("✅ Proceso completado exitosamente")
    else:
        logger.error("❌ Proceso falló")
        exit(1)

if __name__ == "__main__":
    main()
