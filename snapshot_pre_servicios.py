#!/usr/bin/env python3
"""
Script para crear snapshot pre-servicios
Genera bitácora, hace commit y prepara bloque para ChatGPT
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

def leer_diagnostico():
    """Lee el diagnóstico del sistema desde /tmp/estado_sistema.txt"""
    try:
        with open('/tmp/estado_sistema.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Diagnóstico no disponible - ejecutar diagnostico_sistema.py primero"
    except Exception as e:
        return f"Error leyendo diagnóstico: {e}"

def obtener_estado_git():
    """Obtiene estado actual del repositorio Git"""
    try:
        # Verificar si es repo git
        exit_code, _, _ = ejecutar_comando("git rev-parse --git-dir")
        if exit_code != 0:
            return "No es un repositorio Git"
        
        # Obtener información
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

def crear_entrada_bitacora(fecha, diagnostico, acciones_previstas, pendientes):
    """Crea entrada de bitácora con formato estándar"""
    entrada = f"""## {fecha['legible']} - {fecha['hora']}

### Resumen del diagnóstico
- **Estado del sistema**: Pre-servicios (Gunicorn, Nginx, SSL, UFW)
- **Servicios activos**: Nginx, MySQL, UFW
- **Servicios pendientes**: Gunicorn, Fail2ban
- **Puertos web**: 80, 443, 5000, 8080 detectados
- **SSL**: Let's Encrypt configurado (sin certificados)
- **Git**: Repo configurado con cambios pendientes

### Acciones previstas
{chr(10).join([f"- {accion}" for accion in acciones_previstas])}

### Pendientes inmediatos
{chr(10).join([f"- {pendiente}" for pendiente in pendientes])}

### Diagnóstico completo
```
{diagnostico}
```

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
    
    print(f"✓ Actualizado: {archivo}")

def crear_bitacora_diaria(fecha, diagnostico, acciones_previstas, pendientes):
    """Crea archivo diario en /bitacoras/"""
    # Crear directorio si no existe
    bitacoras_dir = Path("bitacoras")
    bitacoras_dir.mkdir(exist_ok=True)
    
    # Crear archivo diario
    archivo_diario = bitacoras_dir / f"{fecha['iso']}.md"
    
    contenido = f"""# Bitácora - {fecha['legible']}

## Estado del sistema
- **Git**: {obtener_estado_git()}
- **Servicios activos**: Nginx, MySQL, UFW
- **Servicios pendientes**: Gunicorn, Fail2ban
- **Puertos web**: 80, 443, 5000, 8080 detectados
- **SSL**: Let's Encrypt configurado (sin certificados)

## Resumen del diagnóstico
- **Estado**: Pre-servicios (Gunicorn, Nginx, SSL, UFW)
- **Servicios críticos**: Parcialmente activos
- **Puertos web**: Detectados
- **SSL**: Let's Encrypt configurado

## Acciones previstas
{chr(10).join([f"- {accion}" for accion in acciones_previstas])}

## Pendientes inmediatos
{chr(10).join([f"- {pendiente}" for pendiente in pendientes])}

## Diagnóstico completo
```
{diagnostico}
```

---
*Generado automáticamente el {fecha['legible']} a las {fecha['hora']}*
"""
    
    with open(archivo_diario, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✓ Creado: {archivo_diario}")

def configurar_rama_dev():
    """Configura rama dev si no existe"""
    # Verificar si existe rama dev
    exit_code, _, _ = ejecutar_comando("git show-ref --verify --quiet refs/heads/dev")
    if exit_code != 0:
        print("🔧 Creando rama dev...")
        exit_code, stdout, stderr = ejecutar_comando("git checkout -b dev")
        if exit_code != 0:
            print(f"❌ Error creando rama dev: {stderr}")
            return False
        print("✅ Rama dev creada")
    else:
        print("🔧 Cambiando a rama dev...")
        exit_code, stdout, stderr = ejecutar_comando("git checkout dev")
        if exit_code != 0:
            print(f"❌ Error cambiando a rama dev: {stderr}")
            return False
        print("✅ Cambiado a rama dev")
    
    return True

def hacer_commit():
    """Hace commit de todos los cambios"""
    print("🔧 Agregando archivos...")
    exit_code, stdout, stderr = ejecutar_comando("git add .")
    if exit_code != 0:
        print(f"❌ Error agregando archivos: {stderr}")
        return None
    
    print("🔧 Haciendo commit...")
    mensaje = "chore: snapshot pre-servicios (gunicorn/nginx/ssl/ufw)"
    exit_code, stdout, stderr = ejecutar_comando(f'git commit -m "{mensaje}"')
    if exit_code != 0:
        print(f"❌ Error haciendo commit: {stderr}")
        return None
    
    # Obtener hash del commit
    exit_code, hash_commit, _ = ejecutar_comando("git rev-parse HEAD")
    if exit_code != 0:
        print("⚠️  No se pudo obtener hash del commit")
        hash_commit = "unknown"
    
    print(f"✅ Commit creado: {mensaje}")
    print(f"✅ Hash: {hash_commit}")
    
    return hash_commit

def generar_bloque_chatgpt(fecha, hash_commit, diagnostico, acciones_previstas, pendientes):
    """Genera bloque listo para ChatGPT"""
    estado_git = obtener_estado_git()
    
    bloque = f"""
## Estado actual del proyecto MGComputacion - {fecha['legible']}

**Git**: {estado_git}
**Commit**: {hash_commit}
**Rama**: dev

**Estado del sistema**:
- Servicios activos: Nginx, MySQL, UFW
- Servicios pendientes: Gunicorn, Fail2ban
- Puertos web: 80, 443, 5000, 8080 detectados
- SSL: Let's Encrypt configurado (sin certificados)

**Acciones previstas**:
{chr(10).join([f"- {accion}" for accion in acciones_previstas])}

**Pendientes inmediatos**:
{chr(10).join([f"- {pendiente}" for pendiente in pendientes])}

**Diagnóstico del sistema**:
```
{diagnostico}
```

**Próximo paso**: Configurar servicios (Gunicorn, Nginx, SSL, UFW)
"""
    
    return bloque

def main():
    print("🚀 SNAPSHOT PRE-SERVICIOS")
    print("="*50)
    
    # Obtener fecha actual
    fecha = obtener_fecha_actual()
    print(f"Fecha: {fecha['legible']} - {fecha['hora']}")
    
    # Leer diagnóstico
    print("📊 Leyendo diagnóstico...")
    diagnostico = leer_diagnostico()
    
    # Definir acciones previstas
    acciones_previstas = [
        "Configurar Gunicorn como servicio systemd",
        "Optimizar configuración de Nginx para proxy reverso",
        "Emitir certificados SSL con Certbot para mgcomputacion.com",
        "Configurar UFW con reglas específicas para puertos web",
        "Implementar Fail2ban para protección contra ataques",
        "Configurar monitoreo de servicios con systemd"
    ]
    
    # Definir pendientes
    pendientes = [
        "Verificar que Gunicorn funcione correctamente con la API",
        "Probar configuración de Nginx con certificados SSL",
        "Validar reglas de UFW y conectividad",
        "Configurar alertas de monitoreo para servicios críticos"
    ]
    
    # Crear entradas de bitácora
    print("\n📝 Generando bitácoras...")
    entrada = crear_entrada_bitacora(fecha, diagnostico, acciones_previstas, pendientes)
    
    # Actualizar bitácora principal
    actualizar_bitacora_principal(entrada)
    
    # Crear bitácora diaria
    crear_bitacora_diaria(fecha, diagnostico, acciones_previstas, pendientes)
    
    # Configurar rama dev
    print("\n🔧 Configurando rama dev...")
    if not configurar_rama_dev():
        print("❌ Error configurando rama dev")
        sys.exit(1)
    
    # Hacer commit
    print("\n💾 Haciendo commit...")
    hash_commit = hacer_commit()
    if not hash_commit:
        print("❌ Error haciendo commit")
        sys.exit(1)
    
    # Generar bloque para ChatGPT
    print("\n📋 BLOQUE PARA CHATGPT")
    print("="*60)
    bloque = generar_bloque_chatgpt(fecha, hash_commit, diagnostico, acciones_previstas, pendientes)
    print(bloque)
    print("="*60)
    
    print("\n✅ Snapshot completado exitosamente!")
    print("📋 Copia el bloque de arriba para ChatGPT si lo necesitas")

if __name__ == "__main__":
    main()
