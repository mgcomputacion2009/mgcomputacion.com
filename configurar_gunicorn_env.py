#!/usr/bin/env python3
"""
Script para configurar servicio systemd de Gunicorn con variables de entorno
Genera servicio, habilita y arranca con configuración desde .env
"""

import subprocess
import os
import sys
from pathlib import Path

def ejecutar_comando(cmd, shell=True, cwd=None):
    """Ejecuta comando y retorna (exit_code, stdout, stderr)"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=30, cwd=cwd)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def cargar_variables_env():
    """Carga variables de entorno desde .env"""
    env_vars = {}
    env_file = Path("/var/www/mgcomputacion/.env")
    
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if '=' in linea and not linea.startswith('#'):
                        key, value = linea.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️  Error leyendo .env: {e}")
    
    return env_vars

def verificar_variables_requeridas(env_vars):
    """Verifica que existan las variables requeridas"""
    variables_requeridas = ['APP_DIR', 'VENV_DIR', 'APP_MODULE']
    variables_faltantes = []
    
    for var in variables_requeridas:
        if var not in env_vars or not env_vars[var]:
            variables_faltantes.append(var)
    
    if variables_faltantes:
        print(f"❌ Variables de entorno faltantes: {', '.join(variables_faltantes)}")
        print("   Agrega las siguientes variables a /var/www/mgcomputacion/.env:")
        for var in variables_faltantes:
            if var == 'APP_DIR':
                print(f"   {var}=/var/www/mgcomputacion")
            elif var == 'VENV_DIR':
                print(f"   {var}=/var/www/mgcomputacion/venv")
            elif var == 'APP_MODULE':
                print(f"   {var}=app:app")
        return False
    
    return True

def verificar_rutas(env_vars):
    """Verifica que las rutas existan"""
    app_dir = env_vars['APP_DIR']
    venv_dir = env_vars['VENV_DIR']
    app_module = env_vars['APP_MODULE']
    
    # Verificar APP_DIR
    if not Path(app_dir).exists():
        print(f"❌ APP_DIR no existe: {app_dir}")
        return False
    
    # Verificar VENV_DIR
    if not Path(venv_dir).exists():
        print(f"❌ VENV_DIR no existe: {venv_dir}")
        return False
    
    # Verificar archivo de aplicación
    if ':' in app_module:
        archivo, funcion = app_module.split(':', 1)
    else:
        archivo = app_module
        funcion = 'app'
    
    archivo_py = archivo + '.py'
    archivo_path = Path(app_dir) / archivo_py
    
    if not archivo_path.exists():
        print(f"❌ Archivo de aplicación no existe: {archivo_path}")
        return False
    
    # Verificar .env
    env_file = Path(app_dir) / '.env'
    if not env_file.exists():
        print(f"❌ Archivo .env no existe: {env_file}")
        return False
    
    return True

def generar_servicio_systemd(env_vars):
    """Genera archivo de servicio systemd para Gunicorn"""
    app_dir = env_vars['APP_DIR']
    venv_dir = env_vars['VENV_DIR']
    app_module = env_vars['APP_MODULE']
    
    # Ruta del ejecutable de Gunicorn en el venv
    gunicorn_path = f"{venv_dir}/bin/gunicorn"
    
    # Comando de ejecución
    comando = f"{gunicorn_path} -w 2 -b 127.0.0.1:8000 {app_module}"
    
    servicio_content = f"""[Unit]
Description=Gunicorn instance to serve MGComputacion API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory={app_dir}
EnvironmentFile={app_dir}/.env
ExecStart={comando}
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gunicorn

[Install]
WantedBy=multi-user.target
"""
    
    return servicio_content

def escribir_servicio_systemd(contenido):
    """Escribe el archivo de servicio systemd"""
    servicio_path = "/etc/systemd/system/gunicorn.service"
    
    try:
        with open(servicio_path, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"✅ Servicio escrito: {servicio_path}")
        return True
    except PermissionError:
        print(f"❌ Error: Sin permisos para escribir en {servicio_path}")
        print("   Ejecuta con sudo o como root")
        return False
    except Exception as e:
        print(f"❌ Error escribiendo servicio: {e}")
        return False

def recargar_systemd():
    """Recarga la configuración de systemd"""
    print("🔄 Recargando systemd...")
    exit_code, stdout, stderr = ejecutar_comando("systemctl daemon-reload")
    if exit_code != 0:
        print(f"❌ Error recargando systemd: {stderr}")
        return False
    
    print("✅ Systemd recargado")
    return True

def habilitar_y_arrancar_servicio():
    """Habilita y arranca el servicio Gunicorn"""
    print("🔧 Habilitando y arrancando servicio gunicorn...")
    exit_code, stdout, stderr = ejecutar_comando("systemctl enable --now gunicorn")
    if exit_code != 0:
        print(f"❌ Error habilitando/arrancando servicio: {stderr}")
        return False
    
    print("✅ Servicio habilitado y arrancado")
    return True

def obtener_estado_servicio():
    """Obtiene estado del servicio"""
    exit_code, stdout, stderr = ejecutar_comando("systemctl status gunicorn.service --no-pager")
    if exit_code == 0:
        return stdout
    else:
        return f"Error obteniendo estado: {stderr}"

def obtener_journal_tail():
    """Obtiene las últimas 20 líneas del journal"""
    exit_code, stdout, stderr = ejecutar_comando("journalctl -u gunicorn.service -n 20 --no-pager")
    if exit_code == 0:
        return stdout
    else:
        return f"Error obteniendo journal: {stderr}"

def verificar_puerto_8000():
    """Verifica si el puerto 8000 está en uso"""
    exit_code, stdout, stderr = ejecutar_comando("ss -tuln | grep :8000")
    if exit_code == 0:
        return True, stdout
    else:
        return False, "Puerto 8000 no está en uso"

def main():
    print("🔧 CONFIGURADOR DE GUNICORN CON VARIABLES DE ENTORNO")
    print("="*60)
    
    # Cargar variables de entorno
    print("📋 Cargando variables de entorno...")
    env_vars = cargar_variables_env()
    
    # Mostrar variables cargadas (sin valores sensibles)
    print("📄 Variables cargadas:")
    for key in ['APP_DIR', 'VENV_DIR', 'APP_MODULE']:
        if key in env_vars:
            print(f"  ✅ {key}: {env_vars[key]}")
        else:
            print(f"  ❌ {key}: No definida")
    
    # Verificar variables requeridas
    print("\n🔍 Verificando variables requeridas...")
    if not verificar_variables_requeridas(env_vars):
        sys.exit(1)
    
    # Verificar rutas
    print("\n🔍 Verificando rutas...")
    if not verificar_rutas(env_vars):
        sys.exit(1)
    
    # Generar servicio systemd
    print("\n📝 Generando servicio systemd...")
    servicio_content = generar_servicio_systemd(env_vars)
    
    # Mostrar contenido del servicio (sin credenciales)
    print("📄 Contenido del servicio:")
    print("-" * 40)
    print(servicio_content)
    print("-" * 40)
    
    # Escribir servicio
    print("\n💾 Escribiendo servicio systemd...")
    if not escribir_servicio_systemd(servicio_content):
        sys.exit(1)
    
    # Recargar systemd
    if not recargar_systemd():
        sys.exit(1)
    
    # Habilitar y arrancar servicio
    if not habilitar_y_arrancar_servicio():
        sys.exit(1)
    
    # Esperar un momento para que el servicio se inicie
    print("\n⏳ Esperando que el servicio se inicie...")
    import time
    time.sleep(3)
    
    # Obtener resumen
    print("\n" + "="*60)
    print("📊 ESTADO DEL SERVICIO")
    print("="*60)
    
    # Estado del servicio
    print("\n🔍 Estado del servicio:")
    estado = obtener_estado_servicio()
    print(estado)
    
    # Journal tail
    print("\n📋 Últimas 20 líneas del journal:")
    journal = obtener_journal_tail()
    print(journal)
    
    # Verificar puerto
    print("\n🌐 Verificación de puerto 8000:")
    puerto_ok, puerto_info = verificar_puerto_8000()
    if puerto_ok:
        print(f"✅ Puerto 8000 en uso: {puerto_info}")
    else:
        print(f"❌ {puerto_info}")
    
    print("\n✅ Configuración de Gunicorn completada!")
    print("🔗 El servicio está disponible en: http://127.0.0.1:8000")

if __name__ == "__main__":
    main()
