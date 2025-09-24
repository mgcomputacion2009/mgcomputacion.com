#!/bin/bash

# Script para actualizar el servicio gunicorn.service
# Uso: ./actualizar_gunicorn.sh

echo "🔄 Actualizando servicio gunicorn.service..."

# Verificar que el archivo editable existe
if [ ! -f "/var/www/mgcomputacion/gunicorn.service.editable" ]; then
    echo "❌ Error: No se encontró gunicorn.service.editable"
    exit 1
fi

# Hacer backup del archivo actual
echo "📋 Creando backup..."
sudo cp /etc/systemd/system/gunicorn.service /etc/systemd/system/gunicorn.service.backup.$(date +%Y%m%d_%H%M%S)

# Copiar el archivo editable al directorio del sistema
echo "📝 Aplicando cambios..."
sudo cp /var/www/mgcomputacion/gunicorn.service.editable /etc/systemd/system/gunicorn.service

# Recargar systemd
echo "🔄 Recargando systemd..."
sudo systemctl daemon-reload

# Reiniciar el servicio
echo "🔄 Reiniciando servicio gunicorn..."
sudo systemctl restart gunicorn

# Verificar estado
echo "✅ Verificando estado del servicio..."
sudo systemctl status gunicorn --no-pager -l

echo "🎉 ¡Servicio actualizado exitosamente!"
