#!/usr/bin/env python3
"""
Script para configurar servicio systemd de Gunicorn
Verifica entorno, genera servicio y lo habilita
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

def verificar_venv(venv_dir):
    """Verifica si existe el entorno virtual"""
    venv_path = Path(venv_dir)
    if not venv_path.exists():
        return False, f"Directorio no existe: {venv_dir}"
    
    # Verificar archivos típicos de venv
    archivos_venv = ['pyvenv.cfg', 'bin/activate', 'bin/python']
    for archivo in archivos_venv:
        if not (venv_path / archivo).exists():
            return False, f"Archivo faltante: {archivo}"
    
    return True, "Entorno virtual válido"

def verificar_app(app_dir, app_module):
    """Verifica si existe la aplicación"""
    app_path = Path(app_dir)
    if not app_path.exists():
        return False, f"Directorio no existe: {app_dir}"
    
    # Extraer archivo y función del módulo
    if ':' in app_module:
        archivo, funcion = app_module.split(':', 1)
    else:
        archivo = app_module
        funcion = 'app'
    
    archivo_py = archivo + '.py'
    archivo_path = app_path / archivo_py
    
    if not archivo_path.exists():
        return False, f"Archivo no existe: {archivo_py}"
    
    return True, f"Aplicación encontrada: {archivo_py}"

def generar_servicio_systemd(app_dir, venv_dir, app_module, usuario="www-data", grupo="www-data"):
    """Genera archivo de servicio systemd para Gunicorn"""
    
    # Ruta del ejecutable de Gunicorn en el venv
    gunicorn_path = f"{venv_dir}/bin/gunicorn"
    
    # Comando de ejecución
    comando = f"{gunicorn_path} --bind 127.0.0.1:8000 --workers 3 --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 {app_module}"
    
    servicio_content = f"""[Unit]
Description=Gunicorn instance to serve MGComputacion API
After=network.target

[Service]
Type=notify
User={usuario}
Group={grupo}
WorkingDirectory={app_dir}
Environment="PATH={venv_dir}/bin"
Environment="PYTHONPATH={app_dir}"
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

def habilitar_servicio():
    """Habilita el servicio Gunicorn"""
    print("🔧 Habilitando servicio gunicorn...")
    exit_code, stdout, stderr = ejecutar_comando("systemctl enable gunicorn.service")
    if exit_code != 0:
        print(f"❌ Error habilitando servicio: {stderr}")
        return False
    
    print("✅ Servicio habilitado")
    return True

def iniciar_servicio():
    """Inicia el servicio Gunicorn"""
    print("🚀 Iniciando servicio gunicorn...")
    exit_code, stdout, stderr = ejecutar_comando("systemctl start gunicorn.service")
    if exit_code != 0:
        print(f"❌ Error iniciando servicio: {stderr}")
        return False
    
    print("✅ Servicio iniciado")
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

def obtener_pid_servicio():
    """Obtiene PID del proceso Gunicorn"""
    exit_code, stdout, stderr = ejecutar_comando("pgrep -f gunicorn")
    if exit_code == 0:
        pids = stdout.strip().split('\n')
        return pids
    else:
        return []

def verificar_puerto_8000():
    """Verifica si el puerto 8000 está en uso"""
    exit_code, stdout, stderr = ejecutar_comando("ss -tuln | grep :8000")
    if exit_code == 0:
        return True, stdout
    else:
        return False, "Puerto 8000 no está en uso"

def main():
    print("🔧 CONFIGURADOR DE GUNICORN SYSTEMD")
    print("="*50)
    
    # Cargar variables de entorno
    print("📋 Cargando variables de entorno...")
    env_vars = cargar_variables_env()
    
    # Obtener variables con valores por defecto
    app_dir = env_vars.get('APP_DIR', '/var/www/mgcomputacion')
    venv_dir = env_vars.get('VENV_DIR', '/var/www/mgcomputacion/venv')
    app_module = env_vars.get('APP_MODULE', 'app:app')
    usuario = env_vars.get('GUNICORN_USER', 'www-data')
    grupo = env_vars.get('GUNICORN_GROUP', 'www-data')
    
    print(f"📁 APP_DIR: {app_dir}")
    print(f"🐍 VENV_DIR: {venv_dir}")
    print(f"📦 APP_MODULE: {app_module}")
    print(f"👤 Usuario: {usuario}")
    print(f"👥 Grupo: {grupo}")
    
    # Verificar entorno virtual
    print("\n🔍 Verificando entorno virtual...")
    venv_ok, venv_msg = verificar_venv(venv_dir)
    print(f"{'✅' if venv_ok else '❌'} {venv_msg}")
    
    if not venv_ok:
        print("❌ No se puede continuar sin entorno virtual válido")
        sys.exit(1)
    
    # Verificar aplicación
    print("\n🔍 Verificando aplicación...")
    app_ok, app_msg = verificar_app(app_dir, app_module)
    print(f"{'✅' if app_ok else '❌'} {app_msg}")
    
    if not app_ok:
        print("❌ No se puede continuar sin aplicación válida")
        sys.exit(1)
    
    # Generar servicio systemd
    print("\n📝 Generando servicio systemd...")
    servicio_content = generar_servicio_systemd(app_dir, venv_dir, app_module, usuario, grupo)
    
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
    
    # Habilitar servicio
    if not habilitar_servicio():
        sys.exit(1)
    
    # Iniciar servicio
    if not iniciar_servicio():
        sys.exit(1)
    
    # Esperar un momento para que el servicio se inicie
    print("\n⏳ Esperando que el servicio se inicie...")
    import time
    time.sleep(3)
    
    # Obtener resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DEL SERVICIO")
    print("="*60)
    
    # Estado del servicio
    print("\n🔍 Estado del servicio:")
    estado = obtener_estado_servicio()
    print(estado)
    
    # Journal tail
    print("\n📋 Últimas 20 líneas del journal:")
    journal = obtener_journal_tail()
    print(journal)
    
    # PID del proceso
    print("\n🆔 PIDs en ejecución:")
    pids = obtener_pid_servicio()
    if pids:
        for pid in pids:
            print(f"  - PID: {pid}")
    else:
        print("  - No se encontraron PIDs de Gunicorn")
    
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
