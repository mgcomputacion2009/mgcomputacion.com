#!/usr/bin/env python3
"""
Script de migración TUSAM usando SQLAlchemy
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def main():
    # Configurar conexión
    db_url = os.getenv('DB_URL', 'mysql+pymysql://miguel:Mg645418037%24%24@127.0.0.1:3306/mgcomputacion')
    
    try:
        engine = create_engine(db_url, echo=True)
        
        with engine.connect() as conn:
            print('=== Configurando TUSAM (compania_id=1) ===')
            
            # 1) Verificar/crear compañía TUSAM
            print('\n1. Verificando compañía TUSAM...')
            result = conn.execute(text('SELECT id, nombre FROM companias WHERE id=1'))
            row = result.fetchone()
            if row:
                print(f'   Compañía encontrada: {row[0]} - {row[1]}')
            else:
                print('   Compañía no encontrada, creando...')
                conn.execute(text('''
                    INSERT INTO companias(id, nombre, estado, creado_en) 
                    VALUES (1, 'TUSAM VENEZUELA', 1, NOW())
                    ON DUPLICATE KEY UPDATE 
                        nombre=VALUES(nombre),
                        estado=VALUES(estado),
                        creado_en=VALUES(creado_en)
                '''))
                conn.commit()
                print('   ✅ Compañía TUSAM creada')
            
            # 2) Asegurar dispositivo principal TUSAM
            print('\n2. Configurando dispositivo principal TUSAM...')
            result = conn.execute(text('''
                SELECT id, compania_id, device_alias, phone_wa, token, estado 
                FROM ar_dispositivos 
                WHERE compania_id=1 AND device_alias='TUSAM_MAIN'
            '''))
            row = result.fetchone()
            if row:
                print(f'   Dispositivo encontrado: {row[2]} - {row[4]}')
            else:
                print('   Dispositivo no encontrado, creando...')
                conn.execute(text('''
                    INSERT INTO ar_dispositivos(compania_id, device_alias, phone_wa, token, estado)
                    VALUES (1, 'TUSAM_MAIN', '58421234567', 'TOKEN_TUSAM_MAIN', 1)
                    ON DUPLICATE KEY UPDATE 
                        token=VALUES(token),
                        estado=VALUES(estado),
                        phone_wa=VALUES(phone_wa)
                '''))
                conn.commit()
                print('   ✅ Dispositivo TUSAM creado')
            
            # 3) Crear mapeo cliente->compañía
            print('\n3. Configurando mapeo cliente TUSAM...')
            result = conn.execute(text('''
                SELECT phone_cliente, compania_id 
                FROM wa_clientes_compania 
                WHERE compania_id=1 AND phone_cliente='584247810736'
            '''))
            row = result.fetchone()
            if row:
                print(f'   Mapeo encontrado: {row[0]} -> {row[1]}')
            else:
                print('   Mapeo no encontrado, creando...')
                conn.execute(text('''
                    INSERT INTO wa_clientes_compania(phone_cliente, compania_id)
                    VALUES ('584247810736', 1)
                    ON DUPLICATE KEY UPDATE compania_id=VALUES(compania_id)
                '''))
                conn.commit()
                print('   ✅ Mapeo cliente TUSAM creado')
            
            # 4) Verificación final
            print('\n=== VERIFICACIÓN FINAL ===')
            
            # Compañía
            result = conn.execute(text('SELECT id, nombre, estado FROM companias WHERE id=1'))
            row = result.fetchone()
            print(f'Compañía: {row[0]} - {row[1]} (estado: {row[2]})')
            
            # Dispositivo
            result = conn.execute(text('''
                SELECT id, device_alias, phone_wa, token, estado 
                FROM ar_dispositivos 
                WHERE compania_id=1 AND device_alias='TUSAM_MAIN'
            '''))
            row = result.fetchone()
            print(f'Dispositivo: {row[1]} - {row[2]} - {row[3]} (estado: {row[4]})')
            
            # Cliente
            result = conn.execute(text('''
                SELECT phone_cliente, compania_id 
                FROM wa_clientes_compania 
                WHERE compania_id=1 AND phone_cliente='584247810736'
            '''))
            row = result.fetchone()
            print(f'Cliente: {row[0]} -> {row[1]}')
            
            print('\n✅ TUSAM configurado correctamente para resolución de tenant')
            
    except SQLAlchemyError as e:
        print(f'❌ Error de base de datos: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'❌ Error inesperado: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
