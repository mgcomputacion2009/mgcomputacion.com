-- Migración 008: Sistema de cola de mensajes de salida (Outbox)
-- Permite que Tasker consulte mensajes pendientes de envío

CREATE TABLE IF NOT EXISTS outbox_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compania_id INT NOT NULL,
    phone VARCHAR(20) NOT NULL COMMENT 'Número de teléfono destino',
    message TEXT NOT NULL COMMENT 'Contenido del mensaje',
    message_type VARCHAR(50) DEFAULT 'notification' COMMENT 'Tipo: notification, session, alert, etc.',
    priority TINYINT DEFAULT 5 COMMENT '1=alta, 5=media, 10=baja',
    status ENUM('pending', 'leased', 'sent', 'failed') DEFAULT 'pending',
    leased_at TIMESTAMP NULL COMMENT 'Momento en que Tasker tomó el mensaje',
    leased_by VARCHAR(100) NULL COMMENT 'Identificador de Tasker que tomó el mensaje',
    sent_at TIMESTAMP NULL COMMENT 'Momento en que se envió exitosamente',
    failed_at TIMESTAMP NULL COMMENT 'Momento en que falló el envío',
    retry_count TINYINT DEFAULT 0 COMMENT 'Número de reintentos',
    max_retries TINYINT DEFAULT 3 COMMENT 'Máximo número de reintentos',
    error_message TEXT NULL COMMENT 'Mensaje de error si falló',
    metadata JSON NULL COMMENT 'Metadatos adicionales',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para consultas eficientes
    INDEX idx_compania_status (compania_id, status),
    INDEX idx_status_priority (status, priority),
    INDEX idx_leased_at (leased_at),
    INDEX idx_created_at (created_at),
    INDEX idx_phone (phone),
    
    -- Clave foránea
    FOREIGN KEY (compania_id) REFERENCES companias(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comentarios de la tabla
ALTER TABLE outbox_messages COMMENT = 'Cola de mensajes de salida para Tasker';

-- Insertar algunos mensajes de prueba para TUSAM
INSERT INTO outbox_messages (compania_id, phone, message, message_type, priority) VALUES
(1, '584247810736', 'Bienvenido a TUSAM. Su sesión ha sido iniciada correctamente.', 'session', 3),
(1, '584247810736', 'Recordatorio: Su cita está programada para mañana a las 10:00 AM.', 'notification', 2),
(1, '584247810736', 'Nueva promoción disponible. Consulte nuestros servicios.', 'promotion', 5);

-- Verificar inserción
SELECT 'Mensajes de prueba insertados en outbox:' as status;
SELECT id, compania_id, phone, message_type, priority, status, created_at 
FROM outbox_messages 
WHERE compania_id = 1;



