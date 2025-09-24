#!/usr/bin/env python3
"""
Archivo principal para ejecutar la aplicación MGComputacion con Gunicorn
"""

from backend.main import app

# Agregar ruta de salud para verificar que la aplicación funciona
@app.route('/')
def health_check():
    return {"status": "ok", "app": "MGComputacion API", "version": "1.0"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "MGComputacion"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
