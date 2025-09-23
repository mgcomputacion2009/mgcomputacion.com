# Contrato de Endpoints API - MGComputacion

## Propósito

Especificación detallada de endpoints REST para el sistema de mensajería inteligente MGComputacion, incluyendo formatos JSON de request/response, códigos de error y tiempos de respuesta esperados.

## Información General

- **Base URL**: `https://api.mgcomputacion.com/v1`
- **Content-Type**: `application/json`
- **Autenticación**: Bearer Token en header `Authorization`
- **Tiempo máximo de respuesta**: 500ms
- **Encoding**: UTF-8

## Headers Comunes

```http
Authorization: Bearer <token>
Content-Type: application/json
X-Company-ID: <compania_id>
X-Request-ID: <uuid>
```

## Endpoints

### 1. GET /health

**Propósito**: Verificación de estado del servicio

#### Request
```http
GET /health
```

#### Response Success (200)
```json
{
  "status": "healthy",
  "timestamp": "2025-09-23T03:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "llm": "available"
  },
  "uptime": "5d 16h 30m"
}
```

#### Response Error (503)
```json
{
  "status": "unhealthy",
  "timestamp": "2025-09-23T03:30:00Z",
  "errors": [
    {
      "service": "database",
      "status": "disconnected",
      "message": "Connection timeout"
    }
  ]
}
```

**Tiempo esperado**: < 100ms

---

### 2. POST /datos/precios

**Propósito**: Consulta de precios por marca y modelo

#### Request
```json
{
  "marca": "Dell",
  "modelo": "OptiPlex 7090",
  "compania_id": 1,
  "filtros": {
    "categoria": "desktop",
    "disponible": true
  }
}
```

#### Response Success (200)
```json
{
  "success": true,
  "data": {
    "marca": "Dell",
    "modelo": "OptiPlex 7090",
    "total_items": 3,
    "items": [
      {
        "id": 101,
        "sku": "DELL-OP7090-I5-8GB",
        "nombre": "Dell OptiPlex 7090 Intel i5 8GB RAM",
        "precio": 850.00,
        "disponible": true,
        "stock": 5,
        "especificaciones": {
          "procesador": "Intel Core i5-11500",
          "ram": "8GB DDR4",
          "almacenamiento": "256GB SSD"
        }
      },
      {
        "id": 102,
        "sku": "DELL-OP7090-I7-16GB",
        "nombre": "Dell OptiPlex 7090 Intel i7 16GB RAM",
        "precio": 1200.00,
        "disponible": true,
        "stock": 3,
        "especificaciones": {
          "procesador": "Intel Core i7-11700",
          "ram": "16GB DDR4",
          "almacenamiento": "512GB SSD"
        }
      }
    ]
  },
  "metadata": {
    "query_time": "45ms",
    "cache_hit": false,
    "source": "database"
  }
}
```

#### Response Error (400)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Marca y modelo son requeridos",
    "details": {
      "missing_fields": ["marca", "modelo"]
    }
  }
}
```

#### Response Error (404)
```json
{
  "success": false,
  "error": {
    "code": "NO_PRODUCTS_FOUND",
    "message": "No se encontraron productos para la marca y modelo especificados",
    "data": {
      "marca": "Dell",
      "modelo": "OptiPlex 7090"
    }
  }
}
```

**Tiempo esperado**: < 300ms

---

### 3. POST /datos/verificar_cliente

**Propósito**: Verificación de existencia de cliente por teléfono

#### Request
```json
{
  "telefono": "+5215512345678",
  "compania_id": 1
}
```

#### Response Success (200) - Cliente existe
```json
{
  "success": true,
  "data": {
    "existe": true,
    "cliente_id": 12345,
    "nombre": "Juan Pérez",
    "email": "juan.perez@email.com",
    "estado_verificacion": "verificado",
    "ultima_interaccion": "2025-09-22T15:30:00Z",
    "datos_adicionales": {
      "preferencias": ["notificaciones_whatsapp"],
      "segmento": "premium"
    }
  }
}
```

#### Response Success (200) - Cliente no existe
```json
{
  "success": true,
  "data": {
    "existe": false,
    "cliente_id": null,
    "nombre": null,
    "sugerencia": "Cliente no registrado. ¿Desea crear nuevo cliente?"
  }
}
```

#### Response Error (400)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PHONE",
    "message": "Formato de teléfono inválido",
    "details": {
      "telefono": "+5215512345678",
      "expected_format": "E.164 (+5215512345678)"
    }
  }
}
```

**Tiempo esperado**: < 200ms

---

### 4. POST /datos/crear_pedido

**Propósito**: Creación de nuevo pedido

#### Request
```json
{
  "cliente_id": 12345,
  "compania_id": 1,
  "items": [
    {
      "producto_id": 101,
      "cantidad": 2,
      "precio_unit": 850.00
    },
    {
      "producto_id": 102,
      "cantidad": 1,
      "precio_unit": 1200.00
    }
  ],
  "metodo_pago": "transferencia",
  "direccion_entrega": {
    "calle": "Av. Reforma 123",
    "colonia": "Centro",
    "ciudad": "Ciudad de México",
    "cp": "06000"
  },
  "notas": "Entrega urgente"
}
```

#### Response Success (201)
```json
{
  "success": true,
  "data": {
    "codigo_pedido": "PED-2025-0917-001234",
    "pedido_id": 56789,
    "total": 2900.00,
    "estado": "pendiente",
    "items": [
      {
        "producto_id": 101,
        "sku": "DELL-OP7090-I5-8GB",
        "nombre": "Dell OptiPlex 7090 Intel i5 8GB RAM",
        "cantidad": 2,
        "precio_unit": 850.00,
        "subtotal": 1700.00
      },
      {
        "producto_id": 102,
        "sku": "DELL-OP7090-I7-16GB",
        "nombre": "Dell OptiPlex 7090 Intel i7 16GB RAM",
        "cantidad": 1,
        "precio_unit": 1200.00,
        "subtotal": 1200.00
      }
    ],
    "resumen": {
      "subtotal": 2900.00,
      "descuentos": 0.00,
      "total": 2900.00
    },
    "creado_en": "2025-09-23T03:30:00Z",
    "tiempo_estimado_entrega": "3-5 días hábiles"
  }
}
```

#### Response Error (400)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_ORDER",
    "message": "Datos del pedido inválidos",
    "details": {
      "cliente_id": "Cliente no existe",
      "items": [
        {
          "producto_id": 999,
          "error": "Producto no disponible"
        }
      ]
    }
  }
}
```

#### Response Error (422)
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Stock insuficiente para algunos productos",
    "details": {
      "items_insuficientes": [
        {
          "producto_id": 101,
          "solicitado": 10,
          "disponible": 5
        }
      ]
    }
  }
}
```

**Tiempo esperado**: < 400ms

---

### 5. GET /datos/pedido/{codigo_pedido}

**Propósito**: Consulta de pedido por código

#### Request
```http
GET /datos/pedido/PED-2025-0917-001234
```

#### Response Success (200)
```json
{
  "success": true,
  "data": {
    "codigo_pedido": "PED-2025-0917-001234",
    "pedido_id": 56789,
    "cliente": {
      "id": 12345,
      "nombre": "Juan Pérez",
      "telefono": "+5215512345678",
      "email": "juan.perez@email.com"
    },
    "estado": "en_proceso",
    "total": 2900.00,
    "metodo_pago": "transferencia",
    "direccion_entrega": {
      "calle": "Av. Reforma 123",
      "colonia": "Centro",
      "ciudad": "Ciudad de México",
      "cp": "06000"
    },
    "items": [
      {
        "producto_id": 101,
        "sku": "DELL-OP7090-I5-8GB",
        "nombre": "Dell OptiPlex 7090 Intel i5 8GB RAM",
        "cantidad": 2,
        "precio_unit": 850.00,
        "subtotal": 1700.00
      },
      {
        "producto_id": 102,
        "sku": "DELL-OP7090-I7-16GB",
        "nombre": "Dell OptiPlex 7090 Intel i7 16GB RAM",
        "cantidad": 1,
        "precio_unit": 1200.00,
        "subtotal": 1200.00
      }
    ],
    "timeline": [
      {
        "estado": "pendiente",
        "timestamp": "2025-09-23T03:30:00Z",
        "descripcion": "Pedido creado"
      },
      {
        "estado": "confirmado",
        "timestamp": "2025-09-23T04:15:00Z",
        "descripcion": "Pago confirmado"
      },
      {
        "estado": "en_proceso",
        "timestamp": "2025-09-23T08:00:00Z",
        "descripcion": "Preparando envío"
      }
    ],
    "creado_en": "2025-09-23T03:30:00Z",
    "actualizado_en": "2025-09-23T08:00:00Z"
  }
}
```

#### Response Error (404)
```json
{
  "success": false,
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "Pedido no encontrado",
    "details": {
      "codigo_pedido": "PED-2025-0917-001234"
    }
  }
}
```

#### Response Error (403)
```json
{
  "success": false,
  "error": {
    "code": "ACCESS_DENIED",
    "message": "No tienes permisos para ver este pedido",
    "details": {
      "codigo_pedido": "PED-2025-0917-001234",
      "compania_id": 1
    }
  }
}
```

**Tiempo esperado**: < 200ms

## Códigos de Error Estándar

### 4xx - Errores del Cliente
- `400 Bad Request` - Datos de entrada inválidos
- `401 Unauthorized` - Token de autenticación inválido
- `403 Forbidden` - Sin permisos para el recurso
- `404 Not Found` - Recurso no encontrado
- `422 Unprocessable Entity` - Datos válidos pero no procesables

### 5xx - Errores del Servidor
- `500 Internal Server Error` - Error interno del servidor
- `503 Service Unavailable` - Servicio temporalmente no disponible
- `504 Gateway Timeout` - Timeout en servicio externo

## Códigos de Error Personalizados

| Código | Descripción |
|--------|-------------|
| `INVALID_REQUEST` | Datos de entrada inválidos |
| `INVALID_PHONE` | Formato de teléfono inválido |
| `NO_PRODUCTS_FOUND` | No se encontraron productos |
| `INVALID_ORDER` | Datos del pedido inválidos |
| `INSUFFICIENT_STOCK` | Stock insuficiente |
| `ORDER_NOT_FOUND` | Pedido no encontrado |
| `ACCESS_DENIED` | Sin permisos para el recurso |
| `CLIENT_NOT_FOUND` | Cliente no encontrado |
| `COMPANY_NOT_FOUND` | Compañía no encontrada |

## Consideraciones de Performance

### Tiempos de Respuesta
- **Health Check**: < 100ms
- **Consultas simples**: < 200ms
- **Consultas complejas**: < 300ms
- **Operaciones de escritura**: < 400ms
- **Máximo absoluto**: < 500ms

### Estrategias de Optimización
- **Caching**: Redis para consultas frecuentes
- **Índices**: Optimización de consultas de base de datos
- **Paginación**: Límite de 20 items por defecto
- **Compresión**: GZIP para responses grandes
- **CDN**: Assets estáticos en CDN

## Versionado

- **Versión actual**: v1
- **Compatibilidad**: Backward compatible por 6 meses
- **Deprecación**: 3 meses de aviso antes de remover endpoints

## Testing

### Casos de Prueba Recomendados
1. **Happy Path**: Flujo completo exitoso
2. **Error Handling**: Todos los códigos de error
3. **Performance**: Tiempos de respuesta bajo carga
4. **Security**: Validación de tokens y permisos
5. **Edge Cases**: Datos límite y casos especiales

---
*Contrato de API diseñado para MGComputacion - Sistema de Mensajería Inteligente*
