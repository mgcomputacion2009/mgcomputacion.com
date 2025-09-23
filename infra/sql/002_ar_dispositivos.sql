-- Migración 002: Tabla de dispositivos AR (WhatsApp Business)
-- Crea la tabla de dispositivos asociados a compañías

CREATE TABLE IF NOT EXISTS ar_dispositivos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compania_id INT NOT NULL,
    device_alias VARCHAR(100) NOT NULL UNIQUE,
    phone_wa VARCHAR(20) NOT NULL UNIQUE,
    token VARCHAR(500) NOT NULL,
    estado TINYINT NOT NULL DEFAULT 1 COMMENT '1=activo, 0=inactivo',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (compania_id) REFERENCES companias(id) ON DELETE CASCADE,
    INDEX idx_compania_id (compania_id),
    INDEX idx_estado (estado),
    INDEX idx_creado_en (creado_en),
    UNIQUE KEY uk_device_alias (device_alias),
    UNIQUE KEY uk_phone_wa (phone_wa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar dispositivo DEMO por defecto
INSERT IGNORE INTO ar_dispositivos (compania_id, device_alias, phone_wa, token, estado) 
VALUES (1, 'demo_device', '+56912345678', 'demo_token_123', 1);
