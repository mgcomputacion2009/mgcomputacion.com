#!/usr/bin/env python3
"""
Script para crear estructura de carpetas del proyecto MGComputacion
Crea directorios y README placeholders con descripciones básicas
"""

import os
from pathlib import Path

def crear_directorio(ruta, descripcion=""):
    """Crea directorio y README.md con descripción"""
    try:
        # Crear directorio
        Path(ruta).mkdir(parents=True, exist_ok=True)
        print(f"✅ Creado: {ruta}/")
        
        # Crear README.md si no existe
        readme_path = Path(ruta) / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# {Path(ruta).name}\n\n")
                f.write(f"{descripcion}\n\n")
                f.write("*Placeholder - Documentar funcionalidad específica*\n")
            print(f"  📄 README.md creado")
        
    except Exception as e:
        print(f"❌ Error creando {ruta}: {e}")

def crear_estructura_backend():
    """Crea estructura del backend"""
    print("\n🔧 Creando estructura BACKEND...")
    
    estructura = {
        "backend": "Backend principal de la aplicación",
        "backend/api": "API REST endpoints y controladores",
        "backend/webhooks": "Webhooks para integraciones externas",
        "backend/orquestador_llm": "Orquestador de llamadas a LLM",
        "backend/modulos": "Módulos de negocio del sistema",
        "backend/modulos/precios": "Gestión de precios y cotizaciones",
        "backend/modulos/financiamiento": "Cálculos de financiamiento y crédito",
        "backend/modulos/sesiones": "Gestión de sesiones de usuario",
        "backend/modulos/clientes": "CRUD y gestión de clientes",
        "backend/modulos/pedidos": "Gestión de pedidos y órdenes"
    }
    
    for ruta, descripcion in estructura.items():
        crear_directorio(ruta, descripcion)

def crear_estructura_frontend():
    """Crea estructura del frontend"""
    print("\n🔧 Creando estructura FRONTEND...")
    
    estructura = {
        "frontend": "Frontend principal de la aplicación",
        "frontend/react_panel": "Panel de administración en React",
        "frontend/react_panel/sesiones_en_vivo": "Vista de sesiones en tiempo real",
        "frontend/react_panel/config": "Configuración del panel de admin",
        "frontend/static": "Archivos estáticos (CSS, JS, imágenes)",
        "frontend/templates": "Templates HTML base"
    }
    
    for ruta, descripcion in estructura.items():
        crear_directorio(ruta, descripcion)

def crear_estructura_infra():
    """Crea estructura de infraestructura"""
    print("\n🔧 Creando estructura INFRA...")
    
    estructura = {
        "infra": "Configuraciones de infraestructura",
        "infra/nginx_conf": "Configuraciones de Nginx",
        "infra/systemd": "Servicios systemd",
        "infra/despliegue": "Scripts de despliegue y CI/CD",
        "infra/docker": "Configuraciones Docker",
        "infra/ssl": "Certificados y configuraciones SSL"
    }
    
    for ruta, descripcion in estructura.items():
        crear_directorio(ruta, descripcion)

def crear_estructura_docs():
    """Crea estructura de documentación"""
    print("\n🔧 Creando estructura DOCS...")
    
    estructura = {
        "docs": "Documentación del proyecto",
        "docs/arquitectura": "Diagramas y documentación de arquitectura",
        "docs/decisiones": "Registro de decisiones técnicas (ADRs)",
        "docs/prompts": "Documentación de prompts y templates",
        "docs/api": "Documentación de API",
        "docs/despliegue": "Guías de despliegue y configuración"
    }
    
    for ruta, descripcion in estructura.items():
        crear_directorio(ruta, descripcion)

def crear_estructura_prompts():
    """Crea estructura de prompts"""
    print("\n🔧 Creando estructura PROMPTS...")
    
    estructura = {
        "prompts": "Prompts y templates del sistema",
        "prompts/sistema": "Prompts del sistema principal",
        "prompts/intent_detection": "Prompts para detección de intenciones",
        "prompts/tool_calls": "Prompts para llamadas a herramientas",
        "prompts/plantillas_respuesta": "Plantillas de respuestas estandarizadas",
        "prompts/contexto": "Prompts de contexto y memoria"
    }
    
    for ruta, descripcion in estructura.items():
        crear_directorio(ruta, descripcion)

def crear_estructura_scripts():
    """Crea estructura de scripts"""
    print("\n🔧 Creando estructura SCRIPTS...")
    
    estructura = {
        "scripts": "Scripts de utilidad y automatización",
        "scripts/auditoria": "Scripts de auditoría y monitoreo",
        "scripts/bitacoras": "Scripts de gestión de bitácoras",
        "scripts/utilidades": "Scripts de utilidad general",
        "scripts/backup": "Scripts de respaldo y recuperación",
        "scripts/monitoreo": "Scripts de monitoreo del sistema"
    }
    
    for ruta, descripcion in estructura.items():
        crear_directorio(ruta, descripcion)

def crear_estructura_tests():
    """Crea estructura de tests"""
    print("\n🔧 Creando estructura TESTS...")
    
    estructura = {
        "tests": "Tests del sistema",
        "tests/unitarios": "Tests unitarios",
        "tests/integracion": "Tests de integración",
        "tests/e2e": "Tests end-to-end",
        "tests/fixtures": "Datos de prueba y fixtures"
    }
    
    for ruta, descripcion in estructura.items():
        crear_directorio(ruta, descripcion)

def crear_readme_principal():
    """Crea README.md principal del proyecto"""
    print("\n🔧 Creando README.md principal...")
    
    readme_content = """# MGComputacion - Sistema de Mensajería Inteligente

Sistema integral de mensajería empresarial con integración de LLM para automatización y atención al cliente.

## Propósito

- **Automatización de respuestas**: Sistema inteligente de respuestas automáticas usando LLM
- **Gestión de clientes**: CRM integrado para seguimiento y gestión de clientes
- **Financiamiento**: Cálculo automático de planes de financiamiento
- **Sesiones en vivo**: Panel de administración para monitoreo en tiempo real
- **Integración multi-canal**: Soporte para múltiples canales de comunicación
- **Escalabilidad**: Arquitectura modular para crecimiento horizontal

## Estructura del Proyecto

```
├── backend/           # API y lógica de negocio
├── frontend/          # Interfaz de usuario React
├── infra/             # Configuraciones de infraestructura
├── docs/              # Documentación del proyecto
├── prompts/           # Prompts y templates del sistema
├── scripts/           # Scripts de utilidad y automatización
└── tests/             # Suite de pruebas
```

## Tecnologías

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: React, TypeScript, Tailwind CSS
- **Base de datos**: MySQL/PostgreSQL
- **Infraestructura**: Nginx, Docker, systemd
- **LLM**: OpenAI GPT, Claude, o modelos locales

## Inicio Rápido

1. Clonar el repositorio
2. Configurar variables de entorno
3. Instalar dependencias
4. Ejecutar migraciones de base de datos
5. Iniciar servicios

Ver `docs/despliegue/` para instrucciones detalladas.

## Contribución

Ver `docs/` para guías de contribución y estándares de código.

---
*Sistema desarrollado para MGComputacion - 2025*
"""
    
    try:
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ README.md principal creado")
    except Exception as e:
        print(f"❌ Error creando README.md: {e}")

def mostrar_resumen():
    """Muestra resumen de la estructura creada"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE ESTRUCTURA CREADA")
    print("="*60)
    
    # Contar directorios creados
    total_dirs = 0
    for root, dirs, files in os.walk("."):
        # Filtrar directorios ocultos y .git
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        total_dirs += len(dirs)
    
    print(f"📁 Total de directorios: {total_dirs}")
    print(f"📄 READMEs creados: {len([f for f in os.listdir('.') if f == 'README.md'])}")
    
    print("\n📋 Estructura principal:")
    estructura_principal = [
        "backend/",
        "frontend/",
        "infra/",
        "docs/",
        "prompts/",
        "scripts/",
        "tests/"
    ]
    
    for item in estructura_principal:
        if os.path.exists(item):
            print(f"  ✅ {item}")
        else:
            print(f"  ❌ {item}")
    
    print("\n🎯 Próximos pasos:")
    print("  1. Revisar estructura creada")
    print("  2. Configurar .gitignore si no existe")
    print("  3. Hacer commit inicial")
    print("  4. Comenzar desarrollo en backend/modulos/")
    print("="*60)

def main():
    print("🏗️  CREADOR DE ESTRUCTURA MGCOMPUTACION")
    print("="*50)
    
    # Crear todas las estructuras
    crear_estructura_backend()
    crear_estructura_frontend()
    crear_estructura_infra()
    crear_estructura_docs()
    crear_estructura_prompts()
    crear_estructura_scripts()
    crear_estructura_tests()
    crear_readme_principal()
    
    # Mostrar resumen
    mostrar_resumen()
    
    print("\n✅ Estructura del proyecto creada exitosamente!")

if __name__ == "__main__":
    main()
