-- Tabla de secretos por compañía para validar firma de webhooks
-- Idempotente

CREATE TABLE IF NOT EXISTS compania_secrets (
  compania_id INT NOT NULL PRIMARY KEY,
  ar_webhook_secret VARCHAR(128) NOT NULL,
  actualizado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_cs_compania FOREIGN KEY (compania_id) REFERENCES companias(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed opcional para TUSAM (cambiar el secreto en prod)
INSERT INTO compania_secrets (compania_id, ar_webhook_secret)
VALUES (1, 'TUSAM_SECRET_DEMO_32+CHARS')
ON DUPLICATE KEY UPDATE ar_webhook_secret = VALUES(ar_webhook_secret);


