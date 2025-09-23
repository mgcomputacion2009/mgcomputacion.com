# Checkpoint: AutoResponder conectado

- Fecha: 2025-09-23 10:10:50Z
- Endpoint: POST /v1/wa/autoresponder
- Formato respuesta: {"replies":[{"message":"..."}]}
- Auth: X-AR-Device/X-AR-Token (Bearer opcional vía Nginx)
- Proxy: Nginx con Authorization passthrough y log ar_log
- Estado: OK (200)

Logs breves:
- Últimos accesos y códigos en /var/log/nginx/mgcomputacion.com_access.log
- App (gunicorn): journalctl -u gunicorn -f
