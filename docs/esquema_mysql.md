# Esquema de Base de Datos MySQL - MGComputacion

## Propósito

Esquema de base de datos para el sistema de mensajería inteligente MGComputacion, diseñado para soportar múltiples compañías, gestión de clientes, sesiones de chat, catálogo de productos y procesamiento de pedidos.

## Tablas Principales

### 1. companias
**Propósito**: Gestión de empresas que utilizan el sistema

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PRIMARY KEY AUTO_INCREMENT | Identificador único |
| nombre | VARCHAR(255) NOT NULL | Nombre de la compañía |
| numero_wa | VARCHAR(20) UNIQUE | Número de WhatsApp Business |
| flags | JSON | Configuraciones adicionales y flags |
| origen_catalogo | ENUM('local', 'remoto', 'hibrido') | Origen del catálogo de productos |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Última actualización |

### 2. clientes
**Propósito**: Base de datos de clientes por compañía

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PRIMARY KEY AUTO_INCREMENT | Identificador único |
| telefono | VARCHAR(20) NOT NULL | Número de teléfono/WhatsApp |
| nombre | VARCHAR(255) | Nombre del cliente |
| email | VARCHAR(255) | Correo electrónico |
| compania_id | INT NOT NULL | Referencia a compañía |
| estado_verificacion | ENUM('pendiente', 'verificado', 'rechazado') | Estado de verificación |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Fecha de registro |
| updated_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Última actualización |

### 3. sesiones
**Propósito**: Control de sesiones de chat activas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PRIMARY KEY AUTO_INCREMENT | Identificador único |
| cliente_id | INT NOT NULL | Referencia a cliente |
| compania_id | INT NOT NULL | Referencia a compañía |
| estado | ENUM('activa', 'pausada', 'cerrada', 'transferida') | Estado de la sesión |
| intencion_actual | VARCHAR(100) | Intención detectada actualmente |
| opened_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Inicio de sesión |
| closed_at | TIMESTAMP NULL | Cierre de sesión |

### 4. productos
**Propósito**: Catálogo de productos por compañía

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PRIMARY KEY AUTO_INCREMENT | Identificador único |
| sku | VARCHAR(100) NOT NULL | Código SKU del producto |
| nombre | VARCHAR(255) NOT NULL | Nombre del producto |
| marca | VARCHAR(100) | Marca del producto |
| precio | DECIMAL(10,2) NOT NULL | Precio base |
| compania_id | INT NOT NULL | Referencia a compañía |
| origen_datos | ENUM('local', 'remoto') | Fuente de los datos |
| updated_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Última actualización |

### 5. pedidos
**Propósito**: Órdenes de compra generadas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PRIMARY KEY AUTO_INCREMENT | Identificador único |
| cliente_id | INT NOT NULL | Referencia a cliente |
| compania_id | INT NOT NULL | Referencia a compañía |
| total | DECIMAL(10,2) NOT NULL | Total del pedido |
| codigo_pedido | VARCHAR(50) UNIQUE | Código único del pedido |
| estado | ENUM('pendiente', 'confirmado', 'en_proceso', 'enviado', 'entregado', 'cancelado') | Estado del pedido |
| creado_en | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Última actualización |

### 6. pedido_items
**Propósito**: Items individuales de cada pedido

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PRIMARY KEY AUTO_INCREMENT | Identificador único |
| pedido_id | INT NOT NULL | Referencia a pedido |
| producto_id | INT NOT NULL | Referencia a producto |
| cantidad | INT NOT NULL | Cantidad solicitada |
| precio_unit | DECIMAL(10,2) NOT NULL | Precio unitario al momento de la compra |

### 7. config
**Propósito**: Configuraciones del sistema por compañía

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT PRIMARY KEY AUTO_INCREMENT | Identificador único |
| compania_id | INT | Referencia a compañía (NULL = global) |
| clave | VARCHAR(100) NOT NULL | Clave de configuración |
| valor | TEXT | Valor de la configuración |

## Relaciones (Foreign Keys)

### Relaciones Principales
- `clientes.compania_id` → `companias.id`
- `sesiones.cliente_id` → `clientes.id`
- `sesiones.compania_id` → `companias.id`
- `productos.compania_id` → `companias.id`
- `pedidos.cliente_id` → `clientes.id`
- `pedidos.compania_id` → `companias.id`
- `pedido_items.pedido_id` → `pedidos.id`
- `pedido_items.producto_id` → `productos.id`
- `config.compania_id` → `companias.id`

### Índices Sugeridos
- `clientes(telefono, compania_id)` - Búsqueda por teléfono
- `sesiones(estado, compania_id)` - Sesiones activas por compañía
- `productos(sku, compania_id)` - Búsqueda de productos
- `pedidos(codigo_pedido)` - Búsqueda por código
- `pedidos(cliente_id, estado)` - Pedidos por cliente
- `config(clave, compania_id)` - Configuraciones

## Ejemplos de Consultas Típicas

### 1. Obtener sesiones activas de una compañía
```sql
-- Obtener todas las sesiones activas de una compañía con datos del cliente
SELECT 
    s.id as sesion_id,
    s.intencion_actual,
    s.opened_at,
    c.nombre as cliente_nombre,
    c.telefono
FROM sesiones s
JOIN clientes c ON s.cliente_id = c.id
WHERE s.compania_id = ? 
  AND s.estado = 'activa'
ORDER BY s.opened_at DESC;
```

### 2. Generar reporte de ventas por período
```sql
-- Ventas totales por compañía en un rango de fechas
SELECT 
    comp.nombre as compania,
    COUNT(p.id) as total_pedidos,
    SUM(p.total) as ventas_totales,
    AVG(p.total) as ticket_promedio
FROM pedidos p
JOIN companias comp ON p.compania_id = comp.id
WHERE p.creado_en BETWEEN ? AND ?
  AND p.estado IN ('confirmado', 'en_proceso', 'enviado', 'entregado')
GROUP BY comp.id, comp.nombre
ORDER BY ventas_totales DESC;
```

### 3. Buscar productos por texto y compañía
```sql
-- Búsqueda de productos por nombre o SKU
SELECT 
    p.id,
    p.sku,
    p.nombre,
    p.marca,
    p.precio,
    p.origen_datos
FROM productos p
WHERE p.compania_id = ?
  AND (
    p.nombre LIKE CONCAT('%', ?, '%') 
    OR p.sku LIKE CONCAT('%', ?, '%')
    OR p.marca LIKE CONCAT('%', ?, '%')
  )
ORDER BY p.nombre
LIMIT 20;
```

## Consideraciones de Diseño

### Escalabilidad
- Uso de índices compuestos para consultas frecuentes
- Particionado por `compania_id` para grandes volúmenes
- Campos JSON para flexibilidad en configuraciones

### Integridad
- Constraints de foreign key para mantener consistencia
- Validaciones a nivel de aplicación para datos JSON
- Timestamps automáticos para auditoría

### Performance
- Índices en campos de búsqueda frecuente
- Campos calculados (`subtotal`) para evitar cálculos en tiempo real
- Separación de datos críticos vs. configuración flexible

## Próximos Pasos

1. **Implementación**: Crear scripts de migración SQL
2. **Validaciones**: Definir constraints y triggers
3. **Testing**: Crear datos de prueba para cada tabla
4. **Optimización**: Ajustar índices según patrones de uso real
5. **Backup**: Estrategia de respaldo y recuperación

---
*Esquema diseñado para MGComputacion - Sistema de Mensajería Inteligente*