-- Eventos por compañía/sesión para panel de sesiones
-- Idempotente

CREATE TABLE IF NOT EXISTS eventos (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  compania_id INT NULL,
  session_id VARCHAR(64) NULL,
  tipo VARCHAR(32) NOT NULL,
  payload JSON NULL,
  INDEX idx_compania_ts (compania_id, ts DESC),
  CONSTRAINT fk_ev_compania FOREIGN KEY (compania_id)
    REFERENCES companias(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


