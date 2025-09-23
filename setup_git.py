#!/usr/bin/env python3
"""
Script para configurar repositorio Git desde cero
Inicializa repo, configura ramas, .gitignore y primer commit
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

def cargar_env():
    """Carga variables de entorno desde .env si existe"""
    env_vars = {}
    env_file = Path(".env")
    
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for linea in linea.strip():
                    if '=' in linea and not linea.startswith('#'):
                        key, value = linea.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️  Error leyendo .env: {e}")
    
    return env_vars

def verificar_git_instalado():
    """Verifica que Git esté instalado"""
    exit_code, stdout, stderr = ejecutar_comando("git --version")
    if exit_code != 0:
        print("❌ Git no está instalado. Instálalo con: sudo apt install git")
        return False
    
    print(f"✅ Git instalado: {stdout}")
    return True

def inicializar_repo():
    """Inicializa repositorio Git si no existe"""
    exit_code, _, _ = ejecutar_comando("git rev-parse --git-dir")
    if exit_code == 0:
        print("✅ Repositorio Git ya existe")
        return True
    
    print("🔧 Inicializando repositorio Git...")
    exit_code, stdout, stderr = ejecutar_comando("git init")
    if exit_code != 0:
        print(f"❌ Error inicializando Git: {stderr}")
        return False
    
    print("✅ Repositorio Git inicializado")
    return True

def configurar_usuario():
    """Configura usuario Git si no está configurado"""
    exit_code, nombre, _ = ejecutar_comando("git config user.name")
    if exit_code != 0 or not nombre:
        print("🔧 Configurando usuario Git...")
        ejecutar_comando('git config user.name "MGComputacion"')
        ejecutar_comando('git config user.email "dev@mgcomputacion.com"')
        print("✅ Usuario Git configurado")
    else:
        print(f"✅ Usuario Git ya configurado: {nombre}")

def obtener_remoto():
    """Obtiene URL del remoto desde .env o input del usuario"""
    env_vars = cargar_env()
    remoto = env_vars.get('REMOTO_GIT', '').strip()
    
    if not remoto:
        print("\n📡 Configuración del remoto Git:")
        print("Ejemplos:")
        print("  - HTTPS: https://github.com/usuario/repo.git")
        print("  - SSH: git@github.com:usuario/repo.git")
        remoto = input("URL del remoto: ").strip()
    
    if not remoto:
        print("⚠️  No se configuró remoto. Puedes agregarlo después con:")
        print("   git remote add origin <URL>")
        return None
    
    return remoto

def configurar_remoto(remoto):
    """Configura remoto origin"""
    if not remoto:
        return True
    
    # Verificar si ya existe
    exit_code, stdout, stderr = ejecutar_comando("git remote get-url origin")
    if exit_code == 0:
        if stdout == remoto:
            print(f"✅ Remoto origin ya configurado: {remoto}")
            return True
        else:
            print(f"🔄 Actualizando remoto origin: {stdout} → {remoto}")
            ejecutar_comando(f"git remote set-url origin {remoto}")
    else:
        print(f"🔧 Agregando remoto origin: {remoto}")
        ejecutar_comando(f"git remote add origin {remoto}")
    
    print("✅ Remoto configurado")
    return True

def crear_ramas():
    """Crea ramas main y dev, establece dev como rama de trabajo"""
    # Verificar rama actual
    exit_code, rama_actual, _ = ejecutar_comando("git rev-parse --abbrev-ref HEAD")
    if exit_code != 0:
        print("❌ Error obteniendo rama actual")
        return False
    
    print(f"📍 Rama actual: {rama_actual}")
    
    # Crear/verificar rama main
    exit_code, _, _ = ejecutar_comando("git show-ref --verify --quiet refs/heads/main")
    if exit_code != 0:
        print("🔧 Creando rama main...")
        ejecutar_comando("git checkout -b main")
    else:
        print("✅ Rama main ya existe")
    
    # Crear/verificar rama dev
    exit_code, _, _ = ejecutar_comando("git show-ref --verify --quiet refs/heads/dev")
    if exit_code != 0:
        print("🔧 Creando rama dev...")
        ejecutar_comando("git checkout -b dev")
    else:
        print("✅ Rama dev ya existe")
        ejecutar_comando("git checkout dev")
    
    print("✅ Cambiado a rama dev (rama de trabajo)")
    return True

def crear_gitignore():
    """Crea .gitignore básico"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity

# Logs
*.log
logs/
log/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Secrets and keys
*.key
*.pem
*.p12
*.pfx
secrets/
keys/

# Database
*.db
*.sqlite
*.sqlite3

# Backups
backup_*.tar.gz
*.backup
*.bak

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary files
tmp/
temp/
*.tmp
*.temp
"""
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        print("✅ .gitignore ya existe")
        return True
    
    print("🔧 Creando .gitignore...")
    try:
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ .gitignore creado")
        return True
    except Exception as e:
        print(f"❌ Error creando .gitignore: {e}")
        return False

def hacer_primer_commit():
    """Hace el primer commit con estructura básica"""
    print("🔧 Preparando primer commit...")
    
    # Agregar todos los archivos
    exit_code, stdout, stderr = ejecutar_comando("git add -A")
    if exit_code != 0:
        print(f"❌ Error agregando archivos: {stderr}")
        return False
    
    # Verificar si hay cambios para commitear
    exit_code, stdout, stderr = ejecutar_comando("git diff --cached --quiet")
    if exit_code == 0:
        print("ℹ️  No hay cambios para commitear")
        return True
    
    # Hacer commit
    mensaje = "chore: init estructura y bitácora"
    exit_code, stdout, stderr = ejecutar_comando(f'git commit -m "{mensaje}"')
    if exit_code != 0:
        print(f"❌ Error haciendo commit: {stderr}")
        return False
    
    print(f"✅ Commit creado: {mensaje}")
    return True

def mostrar_instrucciones_push(remoto):
    """Muestra instrucciones para hacer push"""
    print("\n" + "="*60)
    print("📋 INSTRUCCIONES PARA PUSH")
    print("="*60)
    
    if not remoto:
        print("1. Configura el remoto primero:")
        print("   git remote add origin <URL_DEL_REPO>")
        print()
    
    print("2. Para subir la rama dev (rama de trabajo):")
    print("   git push -u origin dev")
    print()
    
    print("3. Para subir la rama main:")
    print("   git checkout main")
    print("   git push -u origin main")
    print()
    
    print("4. Para configurar rama por defecto en GitHub:")
    print("   - Ve a Settings → General → Default branch")
    print("   - Cambia de 'main' a 'dev' si quieres")
    print()
    
    print("5. Para trabajo diario:")
    print("   git checkout dev")
    print("   # ... hacer cambios ...")
    print("   git add -A")
    print("   git commit -m 'feat: descripción del cambio'")
    print("   git push origin dev")
    print()
    
    print("6. Para mergear a main (cuando esté listo):")
    print("   git checkout main")
    print("   git merge dev")
    print("   git push origin main")
    print("="*60)

def main():
    print("🚀 CONFIGURADOR DE REPOSITORIO GIT")
    print("="*50)
    
    # Verificar Git instalado
    if not verificar_git_instalado():
        sys.exit(1)
    
    # Inicializar repo
    if not inicializar_repo():
        sys.exit(1)
    
    # Configurar usuario
    configurar_usuario()
    
    # Obtener y configurar remoto
    remoto = obtener_remoto()
    if remoto:
        configurar_remoto(remoto)
    
    # Crear ramas
    if not crear_ramas():
        sys.exit(1)
    
    # Crear .gitignore
    if not crear_gitignore():
        sys.exit(1)
    
    # Hacer primer commit
    if not hacer_primer_commit():
        sys.exit(1)
    
    # Mostrar estado final
    print("\n📊 ESTADO FINAL:")
    exit_code, stdout, stderr = ejecutar_comando("git status -sb")
    if exit_code == 0:
        print(stdout)
    
    exit_code, stdout, stderr = ejecutar_comando("git branch -v")
    if exit_code == 0:
        print("\nRamas:")
        print(stdout)
    
    if remoto:
        exit_code, stdout, stderr = ejecutar_comando("git remote -v")
        if exit_code == 0:
            print("\nRemotos:")
            print(stdout)
    
    # Mostrar instrucciones
    mostrar_instrucciones_push(remoto)
    
    print("\n✅ Configuración completada!")

if __name__ == "__main__":
    main()
