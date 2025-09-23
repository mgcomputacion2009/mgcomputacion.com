#!/usr/bin/env python3
"""
Script para crear estructura mínima de carpetas con README placeholders
Solo crea directorios y archivos README básicos
"""

import os
from pathlib import Path

def crear_directorio_con_readme(ruta, descripcion):
    """Crea directorio y README.md con descripción de una línea"""
    try:
        # Crear directorio
        Path(ruta).mkdir(parents=True, exist_ok=True)
        print(f"✅ Creado: {ruta}/")
        
        # Crear README.md si no existe
        readme_path = Path(ruta) / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# {Path(ruta).name}\n\n")
                f.write(f"{descripcion}\n")
            print(f"  📄 README.md creado")
        
        return True
    except Exception as e:
        print(f"❌ Error creando {ruta}: {e}")
        return False

def main():
    print("🏗️  CREADOR DE ESTRUCTURA MÍNIMA")
    print("="*50)
    
    # Definir estructura de carpetas
    estructura = {
        # Backend
        "backend": "Backend principal de la aplicación",
        "backend/api": "API REST endpoints y controladores",
        "backend/webhooks": "Webhooks para integraciones externas",
        "backend/orquestador_llm": "Orquestador de llamadas a LLM",
        "backend/modulos": "Módulos de negocio del sistema",
        "backend/modulos/precios": "Gestión de precios y cotizaciones",
        "backend/modulos/financiamiento": "Cálculos de financiamiento y crédito",
        "backend/modulos/sesiones": "Gestión de sesiones de usuario",
        "backend/modulos/clientes": "CRUD y gestión de clientes",
        "backend/modulos/pedidos": "Gestión de pedidos y órdenes",
        
        # Frontend
        "frontend": "Frontend principal de la aplicación",
        "frontend/panel_sesiones": "Panel de administración de sesiones",
        "frontend/config": "Configuración del frontend",
        
        # Infraestructura
        "infra": "Configuraciones de infraestructura",
        "infra/nginx": "Configuraciones de Nginx",
        "infra/systemd": "Servicios systemd",
        "infra/deploy": "Scripts de despliegue",
        
        # Documentación
        "docs": "Documentación del proyecto",
        "docs/arquitectura": "Diagramas y documentación de arquitectura",
        "docs/decisiones": "Registro de decisiones técnicas (ADRs)",
        "docs/prompts": "Documentación de prompts y templates",
        
        # Prompts
        "prompts": "Prompts y templates del sistema",
        "prompts/sistema": "Prompts del sistema principal",
        "prompts/intent_detection": "Prompts para detección de intenciones",
        "prompts/tool_calls": "Prompts para llamadas a herramientas",
        "prompts/plantillas_respuesta": "Plantillas de respuestas estandarizadas",
        
        # Scripts
        "scripts": "Scripts de utilidad y automatización",
        "scripts/auditoria": "Scripts de auditoría y monitoreo",
        "scripts/bitacoras": "Scripts de gestión de bitácoras",
        "scripts/utilidades": "Scripts de utilidad general",
        
        # Tests
        "tests": "Tests del sistema"
    }
    
    # Crear todas las carpetas
    rutas_creadas = []
    for ruta, descripcion in estructura.items():
        if crear_directorio_con_readme(ruta, descripcion):
            rutas_creadas.append(ruta)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE ESTRUCTURA CREADA")
    print("="*60)
    
    print(f"📁 Total de carpetas: {len(rutas_creadas)}")
    print(f"📄 READMEs creados: {len(rutas_creadas)}")
    
    print("\n📋 Lista de rutas creadas:")
    for ruta in sorted(rutas_creadas):
        print(f"  ✅ {ruta}/")
    
    print("\n🎯 Estructura organizada por categorías:")
    
    # Agrupar por categoría
    categorias = {
        "Backend": [r for r in rutas_creadas if r.startswith("backend")],
        "Frontend": [r for r in rutas_creadas if r.startswith("frontend")],
        "Infraestructura": [r for r in rutas_creadas if r.startswith("infra")],
        "Documentación": [r for r in rutas_creadas if r.startswith("docs")],
        "Prompts": [r for r in rutas_creadas if r.startswith("prompts")],
        "Scripts": [r for r in rutas_creadas if r.startswith("scripts")],
        "Tests": [r for r in rutas_creadas if r.startswith("tests")]
    }
    
    for categoria, rutas in categorias.items():
        if rutas:
            print(f"\n  📂 {categoria}:")
            for ruta in sorted(rutas):
                print(f"    - {ruta}/")
    
    print("\n✅ Estructura mínima creada exitosamente!")
    print("📝 Cada carpeta contiene un README.md con descripción básica")

if __name__ == "__main__":
    main()
