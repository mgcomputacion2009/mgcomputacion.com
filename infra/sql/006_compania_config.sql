-- Configuración por compañía (flags y ajustes)
-- Idempotente

CREATE TABLE IF NOT EXISTS compania_config (
  compania_id INT NOT NULL PRIMARY KEY,
  prompts_version VARCHAR(8) NOT NULL DEFAULT 'v1',
  menu_productos TINYINT(1) NOT NULL DEFAULT 1,
  cierre_venta TINYINT(1) NOT NULL DEFAULT 1,
  envio_datos_pago TINYINT(1) NOT NULL DEFAULT 1,
  panel_activo TINYINT(1) NOT NULL DEFAULT 1,
  idioma VARCHAR(5) NOT NULL DEFAULT 'es',
  updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_compania_config_compania FOREIGN KEY (compania_id) REFERENCES companias(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed opcional para TUSAM
INSERT INTO compania_config (
  compania_id, prompts_version, menu_productos, cierre_venta, envio_datos_pago, panel_activo, idioma
) VALUES (
  1, 'v1', 1, 1, 1, 1, 'es'
) ON DUPLICATE KEY UPDATE
  prompts_version=VALUES(prompts_version),
  menu_productos=VALUES(menu_productos),
  cierre_venta=VALUES(cierre_venta),
  envio_datos_pago=VALUES(envio_datos_pago),
  panel_activo=VALUES(panel_activo),
  idioma=VALUES(idioma);


