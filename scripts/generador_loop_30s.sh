#!/bin/bash
# Wrapper para ejecutar el generador cada 30 segundos
# Uso: ./generador_loop_30s.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOCK_FILE="$LOG_DIR/generador.lock"
GENERADOR_PY="$SCRIPT_DIR/generador_mensajes_prueba.py"
CRON_LOG="$LOG_DIR/generador_mensajes_cron.log"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Función para log con timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$CRON_LOG"
}

# Función para ejecutar el generador con candado
run_generador() {
    if /usr/bin/flock -n "$LOCK_FILE" -c "cd '$PROJECT_DIR' && /usr/bin/python3 '$GENERADOR_PY'"; then
        log "✅ Generador ejecutado exitosamente"
    else
        log "⚠️  Generador ya en ejecución o falló"
    fi
}

log "🔄 Iniciando loop de generador cada 30 segundos..."

# Loop principal
while true; do
    run_generador
    sleep 30
done




