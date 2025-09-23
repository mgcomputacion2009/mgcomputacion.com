#!/usr/bin/env python3
"""
Script para actualizar bitácora con avance de infraestructura
Genera entrada en BITACORA.md y archivo diario
"""

import subprocess
import os
import sys
from datetime import datetime
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

def obtener_fecha_actual():
    """Obtiene fecha actual en formato legible"""
    now = datetime.now()
    return {
        'iso': now.strftime('%Y-%m-%d'),
        'legible': now.strftime('%d de %B de %Y'),
        'hora': now.strftime('%H:%M:%S')
    }

def obtener_estado_git():
    """Obtiene estado actual del repositorio Git"""
    try:
        # Verificar si es repo git
        exit_code, _, _ = ejecutar_comando("git rev-parse --git-dir")
        if exit_code != 0:
            return "No es un repositorio Git"
        
        # Obtener información
        _, ruta, _ = ejecutar_comando("pwd")
        _, branch, _ = ejecutar_comando("git rev-parse --abbrev-ref HEAD")
        _, remoto, _ = ejecutar_comando("git remote get-url origin")
        _, estado, _ = ejecutar_comando("git status --porcelain")
        _, ultimo_commit, _ = ejecutar_comando("git log --oneline -n 1")
        
        cambios = len([l for l in estado.split('\n') if l.strip()]) if estado else 0
        
        info = f"Rama: {branch} | Remoto: {remoto.split('/')[-1].replace('.git', '')}"
        if cambios > 0:
            info += f" | Cambios pendientes: {cambios}"
        if ultimo_commit:
            info += f" | Último: {ultimo_commit[:50]}..."
        
        return info
    except Exception as e:
        return f"Error: {e}"

def obtener_servicios_activos():
    """Obtiene lista de servicios activos relevantes"""
    servicios = ['nginx', 'gunicorn', 'mysql', 'fail2ban', 'ufw']
    activos = []
    
    for servicio in servicios:
        exit_code, stdout, stderr = ejecutar_comando(f"systemctl is-active {servicio}")
        if exit_code == 0 and stdout.strip() == "active":
            activos.append(servicio)
    
    return activos

def obtener_puertos_web():
    """Obtiene puertos web activos"""
    exit_code, stdout, stderr = ejecutar_comando("ss -tuln | grep -E ':(80|443|8000|5000|8080)'")
    if exit_code == 0 and stdout:
        puertos = []
        for linea in stdout.split('\n'):
            if linea.strip():
                puerto = linea.split(':')[-1].split()[0]
                puertos.append(puerto)
        return sorted(set(puertos))
    return []

def crear_entrada_bitacora(fecha, avance, pendientes, riesgos, siguiente_checkpoint):
    """Crea entrada de bitácora con formato estándar"""
    entrada = f"""## {fecha['legible']} - {fecha['hora']}

### Avance
{avance}

### Pendientes inmediatos
{chr(10).join([f"- {pendiente}" for pendiente in pendientes])}

### Riesgos
{chr(10).join([f"- {riesgo}" for riesgo in riesgos])}

### Siguiente checkpoint
{siguiente_checkpoint}

---
"""
    return entrada

def actualizar_bitacora_principal(entrada):
    """Actualiza BITACORA.md agregando entrada al inicio"""
    archivo = "BITACORA.md"
    
    # Leer contenido existente
    contenido_existente = ""
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido_existente = f.read()
    
    # Crear header si no existe
    if not contenido_existente.startswith("# BITÁCORA DEL PROYECTO"):
        header = """# BITÁCORA DEL PROYECTO

Registro de avances y decisiones del proyecto MGComputacion.

---
"""
        contenido_existente = header + contenido_existente
    
    # Agregar nueva entrada al inicio (después del header)
    lineas = contenido_existente.split('\n')
    header_end = 0
    for i, linea in enumerate(lineas):
        if linea.strip() == "---" and i > 3:  # Después del header
            header_end = i + 1
            break
    
    if header_end > 0:
        nuevo_contenido = '\n'.join(lineas[:header_end]) + '\n' + entrada + '\n'.join(lineas[header_end:])
    else:
        nuevo_contenido = contenido_existente + '\n' + entrada
    
    # Escribir archivo
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(nuevo_contenido)
    
    print(f"✅ Actualizado: {archivo}")

def crear_bitacora_diaria(fecha, avance, pendientes, riesgos, siguiente_checkpoint):
    """Crea archivo diario en /bitacoras/"""
    # Crear directorio si no existe
    bitacoras_dir = Path("bitacoras")
    bitacoras_dir.mkdir(exist_ok=True)
    
    # Crear archivo diario
    archivo_diario = bitacoras_dir / f"{fecha['iso']}.md"
    
    contenido = f"""# Bitácora - {fecha['legible']}

## Estado del sistema
- **Git**: {obtener_estado_git()}
- **Servicios activos**: {', '.join(obtener_servicios_activos()) or 'Ninguno'}
- **Puertos web**: {', '.join(obtener_puertos_web()) or 'Ninguno detectado'}

## Avance
{avance}

## Pendientes inmediatos
{chr(10).join([f"- {pendiente}" for pendiente in pendientes])}

## Riesgos
{chr(10).join([f"- {riesgo}" for riesgo in riesgos])}

## Siguiente checkpoint
{siguiente_checkpoint}

---
*Generado automáticamente el {fecha['legible']} a las {fecha['hora']}*
"""
    
    with open(archivo_diario, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Creado: {archivo_diario}")

def generar_bloque_chatgpt(fecha, avance, pendientes, riesgos, siguiente_checkpoint):
    """Genera bloque listo para ChatGPT"""
    estado_git = obtener_estado_git()
    servicios = obtener_servicios_activos()
    puertos = obtener_puertos_web()
    
    bloque = f"""
## Estado actual del proyecto MGComputacion - {fecha['legible']}

**Git**: {estado_git}
**Servicios activos**: {', '.join(servicios) if servicios else 'Ninguno'}
**Puertos web**: {', '.join(puertos) if puertos else 'Ninguno detectado'}

**Avance reciente**:
{avance}

**Pendientes inmediatos**:
{chr(10).join([f"- {pendiente}" for pendiente in pendientes])}

**Riesgos identificados**:
{chr(10).join([f"- {riesgo}" for riesgo in riesgos])}

**Próximo checkpoint**: {siguiente_checkpoint}
"""
    
    return bloque

def main():
    print("📝 ACTUALIZADOR DE BITÁCORA - INFRAESTRUCTURA")
    print("="*60)
    
    # Obtener fecha actual
    fecha = obtener_fecha_actual()
    print(f"Fecha: {fecha['legible']} - {fecha['hora']}")
    
    # Obtener información del sistema
    print("Obteniendo estado del sistema...")
    estado_git = obtener_estado_git()
    servicios = obtener_servicios_activos()
    puertos = obtener_puertos_web()
    
    print(f"Git: {estado_git}")
    print(f"Servicios: {', '.join(servicios) if servicios else 'Ninguno'}")
    print(f"Puertos web: {', '.join(puertos) if puertos else 'Ninguno'}")
    
    # Definir contenido basado en el avance de infraestructura
    avance = """Infraestructura base establecida y funcionando correctamente:

- **Nginx**: Configurado como proxy reverso con SSL/TLS 1.3
- **Gunicorn**: Servicio systemd activo en puerto 8000
- **SSL**: Certificado Let's Encrypt válido para mgcomputacion.com
- **UFW**: Firewall configurado solo con puertos 22/80/443 abiertos
- **Estructura**: Carpetas del proyecto creadas con README placeholders
- **Git**: Repositorio configurado con rama dev activa

La infraestructura está lista para el desarrollo de la aplicación."""
    
    pendientes = [
        "Implementar API REST básica en backend/api/",
        "Configurar base de datos MySQL con esquema multi-tenant",
        "Desarrollar sistema de prompts y plantillas de respuesta"
    ]
    
    riesgos = [
        "Certificado SSL puede expirar si no se renueva automáticamente",
        "Gunicorn puede fallar si la aplicación no responde correctamente",
        "Firewall UFW puede bloquear conexiones necesarias para desarrollo"
    ]
    
    siguiente_checkpoint = "API REST básica implementada con endpoints de salud y datos"
    
    # Crear entradas
    print("\n📝 Generando bitácoras...")
    entrada = crear_entrada_bitacora(fecha, avance, pendientes, riesgos, siguiente_checkpoint)
    
    # Actualizar bitácora principal
    actualizar_bitacora_principal(entrada)
    
    # Crear bitácora diaria
    crear_bitacora_diaria(fecha, avance, pendientes, riesgos, siguiente_checkpoint)
    
    # Generar bloque para ChatGPT
    print("\n📋 BLOQUE PARA CHATGPT")
    print("="*60)
    bloque = generar_bloque_chatgpt(fecha, avance, pendientes, riesgos, siguiente_checkpoint)
    print(bloque)
    print("="*60)
    
    print("\n✅ Bitácora actualizada correctamente")
    print("📋 Copia el bloque de arriba para ChatGPT si lo necesitas")

if __name__ == "__main__":
    main()
