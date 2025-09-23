-- Migración 001: Tabla de compañías
-- Crea la tabla principal de compañías para multi-tenant

CREATE TABLE IF NOT EXISTS companias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    estado TINYINT NOT NULL DEFAULT 1 COMMENT '1=activo, 0=inactivo',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_estado (estado),
    INDEX idx_creado_en (creado_en)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar compañía DEMO por defecto
INSERT IGNORE INTO companias (id, nombre, estado) VALUES (1, 'DEMO', 1);
