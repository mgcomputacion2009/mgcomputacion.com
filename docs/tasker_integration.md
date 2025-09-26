# Integración con Tasker - Sistema de Cola de Mensajes

## Descripción

Tasker puede consultar periódicamente al servidor web mediante POST para extraer de la base de datos cualquier mensaje que esté en cola para salida. Esta integración permite que cuando la página principal necesite enviar una notificación, mensaje de sesión u otro tipo de aviso al cliente, el sistema pueda recuperar directamente el número y el mensaje.

## Endpoints Disponibles

### 1. Obtener Mensajes Pendientes (Lease)

**Endpoint**: `POST /v1/wa/outbox/lease`

**Headers requeridos**:
```
X-AR-Device: TUSAM_MAIN
X-AR-Token: DEV_TUSAM_MAIN
Content-Type: application/json
```

**Query Parameters**:
- `limit`: Número máximo de mensajes a obtener (default: 10)

**Ejemplo de uso**:
```bash
curl -X POST "https://mgcomputacion.com/v1/wa/outbox/lease?limit=5" \
  -H "Content-Type: application/json" \
  -H "X-AR-Device: TUSAM_MAIN" \
  -H "X-AR-Token: DEV_TUSAM_MAIN"
```

**Respuesta exitosa**:
```json
{
  "ok": true,
  "company_id": 1,
  "device": "TUSAM_MAIN",
  "messages": [
    {
      "id": 2,
      "company_id": 1,
      "telefono": "584247810736",
      "mensaje": "Recordatorio: Su cita está programada para mañana a las 10:00 AM.",
      "priority": 2,
      "status": "queued",
      "created_at": "2025-09-24T01:04:56"
    }
  ],
  "count": 1
}
```

### 2. Confirmar Envío Exitoso (Acknowledge)

**Endpoint**: `POST /v1/wa/outbox/ack`

**Headers requeridos**:
```
X-AR-Device: TUSAM_MAIN
X-AR-Token: DEV_TUSAM_MAIN
Content-Type: application/json
```

**Body**:
```json
{
  "message_id": 123,
  "success": true
}
```

**Ejemplo de uso**:
```bash
curl -X POST https://mgcomputacion.com/v1/wa/outbox/ack \
  -H "Content-Type: application/json" \
  -H "X-AR-Device: TUSAM_MAIN" \
  -H "X-AR-Token: DEV_TUSAM_MAIN" \
  -d '{"message_id": 2, "success": true}'
```

**Respuesta exitosa**:
```json
{
  "ok": true,
  "message_id": 2,
  "success": true
}
```

### 3. Reportar Fallo en Envío (Fail)

**Endpoint**: `POST /v1/wa/outbox/fail`

**Headers requeridos**:
```
X-AR-Device: TUSAM_MAIN
X-AR-Token: DEV_TUSAM_MAIN
Content-Type: application/json
```

**Body**:
```json
{
  "message_id": 123,
  "error_message": "Error de conexión"
}
```

**Ejemplo de uso**:
```bash
curl -X POST https://mgcomputacion.com/v1/wa/outbox/fail \
  -H "Content-Type: application/json" \
  -H "X-AR-Device: TUSAM_MAIN" \
  -H "X-AR-Token: DEV_TUSAM_MAIN" \
  -d '{"message_id": 1, "error_message": "Error de conexión"}'
```

**Respuesta exitosa**:
```json
{
  "ok": true,
  "message_id": 1,
  "failed": true,
  "error_message": "Error de conexión"
}
```

### 4. Estado de la Cola (Status)

**Endpoint**: `GET /v1/wa/outbox/status`

**Headers requeridos**:
```
X-AR-Device: TUSAM_MAIN
X-AR-Token: DEV_TUSAM_MAIN
```

**Ejemplo de uso**:
```bash
curl -X GET https://mgcomputacion.com/v1/wa/outbox/status \
  -H "X-AR-Device: TUSAM_MAIN" \
  -H "X-AR-Token: DEV_TUSAM_MAIN"
```

**Respuesta exitosa**:
```json
{
  "ok": true,
  "company_id": 1,
  "device": "TUSAM_MAIN",
  "queue_status": {
    "queued": 0,
    "reserved": 2,
    "sent": 1,
    "failed": 0,
    "total": 3
  }
}
```

## Flujo de Trabajo Recomendado para Tasker

### 1. Configuración Inicial
```bash
# Variables de configuración
DEVICE_ID="TUSAM_MAIN"
DEVICE_TOKEN="DEV_TUSAM_MAIN"
BASE_URL="https://mgcomputacion.com/v1/wa"
POLL_INTERVAL=30  # segundos
```

### 2. Script de Polling (Ejemplo en Bash)
```bash
#!/bin/bash

while true; do
    echo "Consultando mensajes pendientes..."
    
    # 1. Obtener mensajes pendientes
    RESPONSE=$(curl -s -X POST "${BASE_URL}/outbox/lease?limit=10" \
        -H "Content-Type: application/json" \
        -H "X-AR-Device: ${DEVICE_ID}" \
        -H "X-AR-Token: ${DEVICE_TOKEN}")
    
    # 2. Procesar cada mensaje
    echo "$RESPONSE" | jq -r '.messages[] | @base64' | while read message; do
        if [ "$message" != "null" ]; then
            # Decodificar mensaje
            MSG_DATA=$(echo "$message" | base64 -d)
            MSG_ID=$(echo "$MSG_DATA" | jq -r '.id')
            PHONE=$(echo "$MSG_DATA" | jq -r '.telefono')
            TEXT=$(echo "$MSG_DATA" | jq -r '.mensaje')
            
            echo "Enviando mensaje ID $MSG_ID a $PHONE: $TEXT"
            
            # 3. Enviar mensaje (aquí iría la lógica de envío real)
            if send_whatsapp_message "$PHONE" "$TEXT"; then
                # 4. Confirmar envío exitoso
                curl -s -X POST "${BASE_URL}/outbox/ack" \
                    -H "Content-Type: application/json" \
                    -H "X-AR-Device: ${DEVICE_ID}" \
                    -H "X-AR-Token: ${DEVICE_TOKEN}" \
                    -d "{\"message_id\": $MSG_ID, \"success\": true}"
                echo "Mensaje $MSG_ID enviado exitosamente"
            else
                # 5. Reportar fallo
                curl -s -X POST "${BASE_URL}/outbox/fail" \
                    -H "Content-Type: application/json" \
                    -H "X-AR-Device: ${DEVICE_ID}" \
                    -H "X-AR-Token: ${DEVICE_TOKEN}" \
                    -d "{\"message_id\": $MSG_ID, \"error_message\": \"Error de envío\"}"
                echo "Error enviando mensaje $MSG_ID"
            fi
        fi
    done
    
    # 6. Esperar antes de la siguiente consulta
    sleep $POLL_INTERVAL
done
```

### 3. Función de Envío (Ejemplo)
```bash
send_whatsapp_message() {
    local phone="$1"
    local message="$2"
    
    # Aquí iría la lógica real de envío de WhatsApp
    # Por ejemplo, usando la API de WhatsApp Business
    # o cualquier otro método de envío
    
    echo "Enviando a $phone: $message"
    
    # Simular envío (reemplazar con lógica real)
    if [ $((RANDOM % 10)) -gt 2 ]; then
        return 0  # Éxito
    else
        return 1  # Fallo
    fi
}
```

## Estados de Mensajes

- **queued**: Mensaje pendiente de envío
- **reserved**: Mensaje tomado por Tasker (en proceso)
- **sent**: Mensaje enviado exitosamente
- **failed**: Mensaje falló en el envío

## Prioridades

- **1-2**: Alta prioridad (notificaciones urgentes)
- **3-5**: Prioridad media (notificaciones normales)
- **6-10**: Baja prioridad (promociones, etc.)

## Consideraciones Importantes

1. **Autenticación**: Siempre incluir los headers `X-AR-Device` y `X-AR-Token`
2. **Rate Limiting**: No hacer polling muy frecuente (recomendado: cada 30-60 segundos)
3. **Manejo de Errores**: Siempre confirmar o reportar fallos para evitar mensajes perdidos
4. **Reintentos**: El sistema maneja automáticamente los reintentos
5. **Logs**: Monitorear los logs del servidor para detectar problemas

## Monitoreo

Para monitorear el estado de la cola, usar el endpoint `/outbox/status` que proporciona estadísticas en tiempo real del número de mensajes en cada estado.

