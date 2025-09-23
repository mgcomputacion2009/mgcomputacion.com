#!/usr/bin/env python3
"""
Script de diagnóstico del sistema para Ubuntu
Verifica versiones, servicios, puertos, certificados y estado de Git
"""

import subprocess
import os
import sys
from pathlib import Path

def ejecutar_comando(cmd, shell=True):
    """Ejecuta comando y retorna (exit_code, stdout, stderr)"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def verificar_version(comando, nombre):
    """Verifica versión de un comando"""
    exit_code, stdout, stderr = ejecutar_comando(f"{comando} --version")
    if exit_code == 0:
        # Extraer solo la primera línea y limpiar
        version = stdout.split('\n')[0].strip()
        return f"✓ {nombre}: {version}"
    else:
        return f"✗ {nombre}: No encontrado"

def verificar_servicio(servicio):
    """Verifica si un servicio está activo"""
    exit_code, stdout, stderr = ejecutar_comando(f"systemctl is-active {servicio}")
    if exit_code == 0 and stdout.strip() == "active":
        return f"✓ {servicio}: Activo"
    else:
        return f"✗ {servicio}: Inactivo"

def verificar_puertos():
    """Verifica puertos abiertos y procesos que escuchan"""
    exit_code, stdout, stderr = ejecutar_comando("ss -tuln")
    if exit_code == 0:
        lineas = stdout.split('\n')[1:]  # Saltar header
        puertos = []
        for linea in lineas:
            if linea.strip():
                partes = linea.split()
                if len(partes) >= 5:
                    puerto = partes[4].split(':')[-1]
                    puertos.append(puerto)
        return f"✓ Puertos abiertos: {', '.join(sorted(set(puertos)))}"
    else:
        return "✗ No se pudo obtener puertos"

def verificar_procesos_escuchando():
    """Verifica procesos que están escuchando en puertos"""
    exit_code, stdout, stderr = ejecutar_comando("ss -tulnp")
    if exit_code == 0:
        lineas = stdout.split('\n')[1:]
        procesos = []
        for linea in lineas:
            if 'LISTEN' in linea and 'pid=' in linea:
                # Extraer nombre del proceso
                if 'nginx' in linea.lower():
                    procesos.append('nginx')
                elif 'gunicorn' in linea.lower():
                    procesos.append('gunicorn')
                elif 'mysql' in linea.lower() or 'mariadb' in linea.lower():
                    procesos.append('mysql/mariadb')
                elif 'apache' in linea.lower():
                    procesos.append('apache')
        return f"✓ Procesos escuchando: {', '.join(set(procesos))}" if procesos else "✓ Sin procesos web detectados"
    else:
        return "✗ No se pudo obtener procesos"

def verificar_certificados_ssl():
    """Verifica certificados Let's Encrypt"""
    letsencrypt_path = Path("/etc/letsencrypt")
    if letsencrypt_path.exists():
        exit_code, stdout, stderr = ejecutar_comando("find /etc/letsencrypt/live -name '*.pem' 2>/dev/null | head -5")
        if exit_code == 0 and stdout:
            certificados = stdout.split('\n')
            return f"✓ Certificados SSL encontrados: {len(certificados)} archivos .pem"
        else:
            return "✓ Directorio Let's Encrypt existe pero sin certificados"
    else:
        return "✗ Let's Encrypt no configurado"

def verificar_git():
    """Verifica estado de Git en directorio actual"""
    try:
        # Verificar si es repo git
        exit_code, stdout, stderr = ejecutar_comando("git rev-parse --git-dir")
        if exit_code != 0:
            return "✗ No es un repositorio Git"
        
        # Obtener información del repo
        _, ruta, _ = ejecutar_comando("pwd")
        _, branch, _ = ejecutar_comando("git rev-parse --abbrev-ref HEAD")
        _, remoto, _ = ejecutar_comando("git remote get-url origin")
        _, estado, _ = ejecutar_comando("git status --porcelain")
        
        cambios = len(estado.split('\n')) if estado else 0
        
        info = f"✓ Git: {ruta} | Branch: {branch} | Remoto: {remoto}"
        if cambios > 0:
            info += f" | Cambios pendientes: {cambios}"
        
        return info
    except Exception as e:
        return f"✗ Error verificando Git: {e}"

def generar_resumen():
    """Genera resumen con conclusiones"""
    conclusiones = []
    
    # Verificar servicios críticos
    servicios_criticos = ['nginx', 'mysql', 'gunicorn']
    servicios_activos = 0
    
    for servicio in servicios_criticos:
        exit_code, stdout, stderr = ejecutar_comando(f"systemctl is-active {servicio}")
        if exit_code == 0 and stdout.strip() == "active":
            servicios_activos += 1
    
    if servicios_activos == len(servicios_criticos):
        conclusiones.append("✓ Servicios críticos: Todos activos")
    elif servicios_activos > 0:
        conclusiones.append("⚠ Servicios críticos: Parcialmente activos")
    else:
        conclusiones.append("✗ Servicios críticos: Ninguno activo")
    
    # Verificar puertos web
    exit_code, stdout, stderr = ejecutar_comando("ss -tuln | grep -E ':(80|443|8000|5000)'")
    if exit_code == 0 and stdout:
        conclusiones.append("✓ Puertos web: Detectados")
    else:
        conclusiones.append("⚠ Puertos web: No detectados")
    
    # Verificar certificados
    if Path("/etc/letsencrypt").exists():
        conclusiones.append("✓ SSL: Let's Encrypt configurado")
    else:
        conclusiones.append("⚠ SSL: No configurado")
    
    return conclusiones

def main():
    print("=== DIAGNÓSTICO DEL SISTEMA ===\n")
    
    # Verificar versiones
    print("--- VERSIONES ---")
    versiones = [
        verificar_version("python3", "Python3"),
        verificar_version("pip3", "Pip3"),
        verificar_version("node", "Node.js"),
        verificar_version("npm", "NPM"),
        verificar_version("nginx", "Nginx"),
        verificar_version("mysql", "MySQL"),
        verificar_version("mariadb", "MariaDB"),
        verificar_version("git", "Git"),
    ]
    for version in versiones:
        print(version)
    
    print("\n--- SERVICIOS ---")
    servicios = ['nginx', 'gunicorn', 'mysql', 'mariadb', 'fail2ban', 'ufw']
    for servicio in servicios:
        print(verificar_servicio(servicio))
    
    print("\n--- RED ---")
    print(verificar_puertos())
    print(verificar_procesos_escuchando())
    
    print("\n--- SEGURIDAD ---")
    print(verificar_certificados_ssl())
    
    print("\n--- GIT ---")
    print(verificar_git())
    
    # Generar archivo de resumen
    print("\n--- GENERANDO RESUMEN ---")
    resumen = []
    resumen.append("=== RESUMEN DEL SISTEMA ===")
    resumen.append(f"Fecha: {ejecutar_comando('date')[1]}")
    resumen.append(f"Hostname: {ejecutar_comando('hostname')[1]}")
    resumen.append(f"Uptime: {ejecutar_comando('uptime')[1]}")
    resumen.append("")
    resumen.append("VERSIONES:")
    resumen.extend(versiones)
    resumen.append("")
    resumen.append("SERVICIOS:")
    for servicio in servicios:
        resumen.append(verificar_servicio(servicio))
    resumen.append("")
    resumen.append("RED:")
    resumen.append(verificar_puertos())
    resumen.append(verificar_procesos_escuchando())
    resumen.append("")
    resumen.append("SEGURIDAD:")
    resumen.append(verificar_certificados_ssl())
    resumen.append("")
    resumen.append("GIT:")
    resumen.append(verificar_git())
    resumen.append("")
    resumen.append("CONCLUSIONES:")
    conclusiones = generar_resumen()
    resumen.extend(conclusiones)
    
    # Escribir archivo
    try:
        with open('/tmp/estado_sistema.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(resumen))
        print("✓ Archivo generado: /tmp/estado_sistema.txt")
    except Exception as e:
        print(f"✗ Error escribiendo archivo: {e}")
    
    # Mostrar conclusiones finales
    print("\n=== CONCLUSIONES FINALES ===")
    for conclusion in conclusiones:
        print(conclusion)
    
    print(f"\n✓ Diagnóstico completado. Ver /tmp/estado_sistema.txt para detalles.")

if __name__ == "__main__":
    main()
