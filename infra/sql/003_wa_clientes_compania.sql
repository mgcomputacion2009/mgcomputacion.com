-- Migración 003: Tabla de clientes WhatsApp por compañía
-- Crea la tabla de mapeo de clientes a compañías para fallback

CREATE TABLE IF NOT EXISTS wa_clientes_compania (
    phone_cliente VARCHAR(20) PRIMARY KEY,
    compania_id INT NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (compania_id) REFERENCES companias(id) ON DELETE CASCADE,
    INDEX idx_compania_id (compania_id),
    INDEX idx_creado_en (creado_en)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar cliente DEMO por defecto
INSERT IGNORE INTO wa_clientes_compania (phone_cliente, compania_id) 
VALUES ('+56912345678', 1);
