#!/usr/bin/env python3
"""
Script para configurar Nginx con proxy reverso a Gunicorn
Configura sitio con SSL y redirección HTTP->HTTPS
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

def verificar_nginx_instalado():
    """Verifica si Nginx está instalado"""
    exit_code, stdout, stderr = ejecutar_comando("nginx -v")
    if exit_code != 0:
        return False, "Nginx no está instalado"
    
    return True, stdout

def verificar_nginx_config():
    """Verifica la configuración actual de Nginx"""
    exit_code, stdout, stderr = ejecutar_comando("nginx -t")
    if exit_code != 0:
        return False, f"Configuración inválida: {stderr}"
    
    return True, "Configuración válida"

def generar_configuracion_nginx(server_name, ssl_cert_path=None, ssl_key_path=None):
    """Genera configuración de Nginx para el sitio"""
    
    # Configuración base
    config = f"""server {{
    listen 80;
    server_name {server_name};
    
    # Redirección HTTP -> HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {server_name};
    
    # Configuración SSL
    ssl_certificate {ssl_cert_path or '/etc/letsencrypt/live/' + server_name + '/fullchain.pem'};
    ssl_certificate_key {ssl_key_path or '/etc/letsencrypt/live/' + server_name + '/privkey.pem'};
    
    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Headers de seguridad
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Headers para proxy
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Port $server_port;
    
    # Configuración de proxy
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    
    # Logs
    access_log /var/log/nginx/{server_name}_access.log;
    error_log /var/log/nginx/{server_name}_error.log;
    
    # Ubicación principal - proxy a Gunicorn
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_redirect off;
    }}
    
    # Health check endpoint
    location /health {{
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }}
    
    # Archivos estáticos (si los hay)
    location /static/ {{
        alias /var/www/mgcomputacion/frontend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Favicon
    location /favicon.ico {{
        alias /var/www/mgcomputacion/frontend/static/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}"""
    
    return config

def escribir_configuracion_nginx(config, server_name):
    """Escribe la configuración de Nginx"""
    config_path = f"/etc/nginx/sites-available/{server_name}"
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config)
        print(f"✅ Configuración escrita: {config_path}")
        return True
    except PermissionError:
        print(f"❌ Error: Sin permisos para escribir en {config_path}")
        print("   Ejecuta con sudo o como root")
        return False
    except Exception as e:
        print(f"❌ Error escribiendo configuración: {e}")
        return False

def habilitar_sitio(server_name):
    """Habilita el sitio en Nginx"""
    config_path = f"/etc/nginx/sites-available/{server_name}"
    enabled_path = f"/etc/nginx/sites-enabled/{server_name}"
    
    # Crear enlace simbólico
    try:
        if os.path.exists(enabled_path):
            os.unlink(enabled_path)
        os.symlink(config_path, enabled_path)
        print(f"✅ Sitio habilitado: {enabled_path}")
        return True
    except Exception as e:
        print(f"❌ Error habilitando sitio: {e}")
        return False

def deshabilitar_sitio_default():
    """Deshabilita el sitio por defecto de Nginx"""
    default_path = "/etc/nginx/sites-enabled/default"
    if os.path.exists(default_path):
        try:
            os.unlink(default_path)
            print("✅ Sitio por defecto deshabilitado")
            return True
        except Exception as e:
            print(f"⚠️  Error deshabilitando sitio por defecto: {e}")
            return False
    else:
        print("ℹ️  Sitio por defecto ya deshabilitado")
        return True

def probar_configuracion():
    """Prueba la configuración de Nginx"""
    print("🔍 Probando configuración de Nginx...")
    exit_code, stdout, stderr = ejecutar_comando("nginx -t")
    if exit_code != 0:
        print(f"❌ Error en configuración: {stderr}")
        return False
    
    print("✅ Configuración válida")
    return True

def recargar_nginx():
    """Recarga Nginx"""
    print("🔄 Recargando Nginx...")
    exit_code, stdout, stderr = ejecutar_comando("systemctl reload nginx")
    if exit_code != 0:
        print(f"❌ Error recargando Nginx: {stderr}")
        return False
    
    print("✅ Nginx recargado")
    return True

def obtener_estado_nginx():
    """Obtiene estado de Nginx"""
    exit_code, stdout, stderr = ejecutar_comando("systemctl status nginx --no-pager")
    if exit_code == 0:
        return stdout
    else:
        return f"Error obteniendo estado: {stderr}"

def verificar_puertos_nginx():
    """Verifica puertos de Nginx"""
    print("🌐 Verificando puertos de Nginx...")
    
    # Puerto 80
    exit_code, stdout, stderr = ejecutar_comando("ss -tuln | grep :80")
    if exit_code == 0:
        print("✅ Puerto 80: Activo")
    else:
        print("❌ Puerto 80: No activo")
    
    # Puerto 443
    exit_code, stdout, stderr = ejecutar_comando("ss -tuln | grep :443")
    if exit_code == 0:
        print("✅ Puerto 443: Activo")
    else:
        print("❌ Puerto 443: No activo")

def mostrar_guia_seguridad():
    """Muestra guía para cerrar puertos externamente"""
    print("\n" + "="*60)
    print("🔒 GUÍA DE SEGURIDAD - CERRAR PUERTOS EXTERNOS")
    print("="*60)
    
    print("""
Para cerrar los puertos 5000 y 8080 externamente (solo uso local):

1. CONFIGURAR UFW (Firewall):
   sudo ufw deny 5000
   sudo ufw deny 8080
   sudo ufw reload

2. VERIFICAR REGLAS:
   sudo ufw status numbered

3. CONFIGURAR NGINX (si es necesario):
   # En /etc/nginx/sites-available/tu-sitio
   location /api/ {
       proxy_pass http://127.0.0.1:5000;
       allow 127.0.0.1;
       deny all;
   }

4. CONFIGURAR SYSTEMD (para servicios):
   # En el archivo .service, agregar:
   IPAddressDeny=any
   IPAddressAllow=127.0.0.1
   IPAddressAllow=::1

5. VERIFICAR CONECTIVIDAD:
   # Desde el servidor (debe funcionar):
   curl http://127.0.0.1:5000
   curl http://127.0.0.1:8080
   
   # Desde externo (debe fallar):
   curl http://TU_IP:5000
   curl http://TU_IP:8080

6. MONITOREO:
   # Verificar conexiones:
   sudo netstat -tulpn | grep :5000
   sudo netstat -tulpn | grep :8080
   sudo ss -tulpn | grep :5000
   sudo ss -tulpn | grep :8080
""")

def main():
    print("🔧 CONFIGURADOR DE NGINX")
    print("="*50)
    
    # Cargar variables de entorno
    print("📋 Cargando variables de entorno...")
    env_vars = cargar_variables_env()
    
    # Obtener SERVER_NAME
    server_name = env_vars.get('SERVER_NAME', 'mgcomputacion.com')
    ssl_cert_path = env_vars.get('SSL_CERT_PATH')
    ssl_key_path = env_vars.get('SSL_KEY_PATH')
    
    print(f"🌐 SERVER_NAME: {server_name}")
    if ssl_cert_path:
        print(f"🔒 SSL_CERT_PATH: {ssl_cert_path}")
    if ssl_key_path:
        print(f"🔑 SSL_KEY_PATH: {ssl_key_path}")
    
    # Verificar Nginx
    print("\n🔍 Verificando Nginx...")
    nginx_ok, nginx_msg = verificar_nginx_instalado()
    print(f"{'✅' if nginx_ok else '❌'} {nginx_msg}")
    
    if not nginx_ok:
        print("❌ Nginx no está instalado. Instálalo con: sudo apt install nginx")
        sys.exit(1)
    
    # Generar configuración
    print("\n📝 Generando configuración de Nginx...")
    config = generar_configuracion_nginx(server_name, ssl_cert_path, ssl_key_path)
    
    # Mostrar configuración
    print("📄 Configuración generada:")
    print("-" * 40)
    print(config)
    print("-" * 40)
    
    # Escribir configuración
    print("\n💾 Escribiendo configuración...")
    if not escribir_configuracion_nginx(config, server_name):
        sys.exit(1)
    
    # Habilitar sitio
    print("\n🔗 Habilitando sitio...")
    if not habilitar_sitio(server_name):
        sys.exit(1)
    
    # Deshabilitar sitio por defecto
    print("\n🚫 Deshabilitando sitio por defecto...")
    deshabilitar_sitio_default()
    
    # Probar configuración
    if not probar_configuracion():
        sys.exit(1)
    
    # Recargar Nginx
    if not recargar_nginx():
        sys.exit(1)
    
    # Verificar puertos
    verificar_puertos_nginx()
    
    # Mostrar estado
    print("\n" + "="*60)
    print("📊 ESTADO DE NGINX")
    print("="*60)
    
    estado = obtener_estado_nginx()
    print(estado)
    
    # Mostrar guía de seguridad
    mostrar_guia_seguridad()
    
    print(f"\n✅ Configuración de Nginx completada!")
    print(f"🔗 Sitio disponible en: https://{server_name}")
    print(f"🔄 Redirección HTTP->HTTPS configurada")

if __name__ == "__main__":
    main()
