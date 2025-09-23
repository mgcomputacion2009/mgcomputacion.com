# Panel de Sesiones en Vivo - Especificación UX

## Propósito

Especificación de experiencia de usuario para el panel de administración de sesiones en tiempo real del sistema MGComputacion, incluyendo funcionalidades de monitoreo, gestión y métricas en vivo.

## Vista General

El panel de sesiones es una interfaz React que permite a los administradores monitorear y gestionar conversaciones activas en tiempo real, con capacidades de filtrado, visualización de chat y métricas en vivo.

## Componentes Principales

### 1. Cabecera con KPIs

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ MGComputacion - Panel de Sesiones                    [Usuario] │
├─────────────────────────────────────────────────────────────────┤
│ 📊 KPIs EN VIVO                                                │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Sesiones    │ │ Tiempo Medio│ │ Captación   │ │ Conversión  │ │
│ │ Activas     │ │ Respuesta   │ │ Teléfono    │ │ a Pedido    │ │
│ │     12      │ │   2.3s      │ │    85%      │ │    23%      │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### KPIs Detallados
- **Sesiones Activas**: Contador en tiempo real de sesiones con estado "activa"
- **Tiempo Medio Respuesta**: Promedio de tiempo de respuesta del bot en los últimos 30 minutos
- **Captación Teléfono**: Porcentaje de sesiones que obtuvieron número de teléfono
- **Conversión a Pedido**: Porcentaje de sesiones que generaron un pedido

### 2. Filtros y Búsqueda

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ 🔍 FILTROS                                                      │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Compañía    │ │ Estado      │ │ Intención   │ │ Búsqueda    │ │
│ │ [Todas ▼]   │ │ [Activa ▼]  │ │ [Todas ▼]   │ │ [🔍]        │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### Opciones de Filtro
- **Compañía**: Dropdown con todas las compañías activas
- **Estado**: 
  - Activa
  - Pausada
  - Cerrada
  - Transferida
- **Intención**:
  - Consulta de precios
  - Crear pedido
  - Soporte técnico
  - Información general
  - Otras
- **Búsqueda**: Campo de texto libre para buscar por teléfono, nombre o ID de sesión

### 3. Lista de Sesiones

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ 📋 SESIONES ACTIVAS (12)                                       │
├─────────────────────────────────────────────────────────────────┤
│ ID    │ Cliente        │ Estado        │ Intención    │ Tiempo  │
├───────┼────────────────┼───────────────┼──────────────┼─────────┤
│ #1234 │ Juan Pérez     │ [Esperando]   │ Precios      │ 2m 30s  │
│ #1235 │ María López    │ [Consultando] │ Pedido       │ 5m 15s  │
│ #1236 │ Carlos Ruiz    │ [Pedido OK]   │ Soporte      │ 1m 45s  │
└───────┴────────────────┴───────────────┴──────────────┴─────────┘
```

#### Columnas
- **ID**: Identificador único de la sesión (clickeable)
- **Cliente**: Nombre del cliente o "Sin nombre" si no se ha capturado
- **Estado**: Badge con estado actual (ver sección de badges)
- **Intención**: Intención detectada actualmente
- **Tiempo**: Tiempo transcurrido desde el inicio de la sesión
- **Acciones**: Botones para "Ver detalle", "Transferir", "Cerrar"

### 4. Vista Detalle de Chat

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ 💬 SESIÓN #1234 - Juan Pérez (+52 55 1234 5678)               │
│ Estado: [Esperando Teléfono] │ Intención: Consulta de Precios  │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 14:30:25 [BOT] Hola! ¿En qué puedo ayudarte hoy?          │ │
│ │ 14:30:45 [CLIENTE] Necesito cotizar una computadora       │ │
│ │ 14:30:46 [BOT] Perfecto! ¿Podrías darme tu número de      │ │
│ │           teléfono para enviarte la cotización?           │ │
│ │ 14:31:12 [CLIENTE] +52 55 1234 5678                       │ │
│ │ 14:31:13 [BOT] ✅ Teléfono capturado. ¿Qué marca          │ │
│ │           prefieres? Dell, HP, Lenovo...                  │ │
│ │ 14:31:45 [CLIENTE] Dell por favor                         │ │
│ │ 14:31:46 [BOT] 🔍 Buscando productos Dell...              │ │
│ │ 14:31:50 [BOT] Encontré 3 opciones:                       │ │
│ │           • OptiPlex 7090 - $850                          │ │
│ │           • OptiPlex 7090 Pro - $1,200                    │ │
│ │           • Precision 3650 - $1,500                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ [Escribir mensaje...] [Enviar] [Transferir] [Cerrar]          │
└─────────────────────────────────────────────────────────────────┘
```

#### Características del Chat
- **Columnas**: "Cliente" (izquierda) y "Bot" (derecha)
- **Marca de tiempo**: Formato HH:MM:SS en cada mensaje
- **Estados visuales**: 
  - Mensaje enviado: ✅
  - Mensaje recibido: 📨
  - Bot escribiendo: ⌨️
  - Error: ❌
- **Scroll automático**: Al final del chat
- **Actualización en tiempo real**: WebSocket para nuevos mensajes

### 5. Badges de Estado

#### Diseño Visual
```
┌─────────────────────────────────────────────────────────────────┐
│ 🏷️ BADGES DE ESTADO                                            │
├─────────────────────────────────────────────────────────────────┤
│ [Esperando Teléfono] [Nombre Obtenido] [Consultando Precios]   │
│ [Pedido Creado] [Soporte Técnico] [Transferido] [Cerrado]      │
└─────────────────────────────────────────────────────────────────┘
```

#### Estados y Colores
- **Esperando Teléfono**: `#FF6B6B` (Rojo) - Cliente no ha proporcionado teléfono
- **Nombre Obtenido**: `#4ECDC4` (Verde azulado) - Teléfono capturado, esperando nombre
- **Consultando Precios**: `#45B7D1` (Azul) - Cliente consultando productos
- **Pedido Creado**: `#96CEB4` (Verde) - Pedido generado exitosamente
- **Soporte Técnico**: `#FFEAA7` (Amarillo) - Requiere intervención humana
- **Transferido**: `#DDA0DD` (Púrpura) - Sesión transferida a agente
- **Cerrado**: `#D3D3D3` (Gris) - Sesión finalizada

### 6. Tabla de Eventos en Tiempo Real

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ 📊 EVENTOS EN TIEMPO REAL                                      │
├─────────────────────────────────────────────────────────────────┤
│ Timestamp    │ Sesión │ Evento              │ Payload           │
├──────────────┼────────┼─────────────────────┼───────────────────┤
│ 14:31:45     │ #1234  │ telefono_capturado  │ {"telefono": "+52 │
│              │        │                     │ 55 1234 5678"}    │
│ 14:31:50     │ #1235  │ producto_buscado    │ {"marca": "Dell", │
│              │        │                     │ "resultados": 3}  │
│ 14:32:15     │ #1236  │ pedido_creado       │ {"codigo": "PED-  │
│              │        │                     │ 2025-0917-001"}   │
└──────────────┴────────┴─────────────────────┴───────────────────┘
```

#### Tipos de Eventos
- **telefono_capturado**: Cliente proporcionó número de teléfono
- **nombre_obtenido**: Cliente proporcionó nombre
- **producto_buscado**: Búsqueda de productos realizada
- **precio_consultado**: Consulta de precios específica
- **pedido_creado**: Pedido generado exitosamente
- **sesion_cerrada**: Sesión finalizada
- **transferencia_iniciada**: Sesión transferida a agente
- **error_llm**: Error en procesamiento de LLM

#### Payloads de Ejemplo
```json
{
  "telefono_capturado": {
    "telefono": "+5215512345678",
    "validado": true,
    "formato": "E.164"
  },
  "producto_buscado": {
    "marca": "Dell",
    "modelo": "OptiPlex 7090",
    "resultados": 3,
    "tiempo_busqueda": "1.2s"
  },
  "pedido_creado": {
    "codigo_pedido": "PED-2025-0917-001234",
    "total": 2900.00,
    "items": 2,
    "cliente_id": 12345
  }
}
```

## Funcionalidades Interactivas

### 1. Acciones por Sesión
- **Ver Detalle**: Abre vista de chat completa
- **Transferir**: Transfiere sesión a agente humano
- **Cerrar**: Finaliza sesión con motivo
- **Marcar Importante**: Destaca sesión para seguimiento
- **Exportar Chat**: Descarga conversación en PDF

### 2. Filtros Avanzados
- **Rango de tiempo**: Última hora, 24h, 7 días
- **Agente asignado**: Filtro por agente o bot
- **Tipo de intención**: Múltiples selecciones
- **Estado de captación**: Teléfono, nombre, email
- **Valor del pedido**: Rango de montos

### 3. Notificaciones en Tiempo Real
- **Nueva sesión**: Sonido + notificación visual
- **Sesión transferida**: Badge de alerta
- **Error crítico**: Notificación de error
- **Pedido creado**: Notificación de éxito

## Métricas y KPIs

### 1. Métricas en Tiempo Real
- **Sesiones activas**: Contador actualizado cada 5 segundos
- **Tiempo medio de respuesta**: Calculado en ventana deslizante de 30 minutos
- **Tasa de captación**: Porcentaje de sesiones que capturan teléfono
- **Conversión a pedido**: Porcentaje de sesiones que generan pedidos

### 2. Métricas Históricas
- **Sesiones por hora**: Gráfico de líneas
- **Intenciones más comunes**: Gráfico de barras
- **Tiempo promedio por sesión**: Histograma
- **Satisfacción del cliente**: Rating promedio

### 3. Alertas Automáticas
- **Alto volumen**: > 50 sesiones activas simultáneas
- **Tiempo de respuesta alto**: > 10 segundos promedio
- **Baja captación**: < 60% en la última hora
- **Errores frecuentes**: > 5 errores en 10 minutos

## Responsive Design

### Desktop (1200px+)
- Layout de 3 columnas: Lista | Chat | Eventos
- KPIs en cabecera horizontal
- Filtros en barra superior

### Tablet (768px - 1199px)
- Layout de 2 columnas: Lista | Chat
- Eventos en pestaña deslizable
- KPIs en grid 2x2

### Mobile (320px - 767px)
- Layout de 1 columna con pestañas
- Chat en pantalla completa
- KPIs en carrusel horizontal

## Tecnologías Requeridas

### Frontend
- **React 18+** con TypeScript
- **Tailwind CSS** para estilos
- **Socket.io** para tiempo real
- **React Query** para estado del servidor
- **Recharts** para gráficos

### Backend
- **WebSocket** para eventos en tiempo real
- **Redis** para cache de sesiones activas
- **PostgreSQL** para persistencia
- **Rate limiting** para protección

## Consideraciones de Performance

### Optimizaciones
- **Virtualización**: Para listas largas de sesiones
- **Debouncing**: En filtros y búsquedas
- **Lazy loading**: Para mensajes de chat antiguos
- **Compresión**: Para payloads de WebSocket
- **Caching**: Para datos de compañías y configuraciones

### Límites
- **Máximo 1000 sesiones** en lista
- **Máximo 1000 mensajes** por chat
- **Actualización cada 5 segundos** para métricas
- **Retención de 7 días** para eventos

---
*Especificación UX diseñada para MGComputacion - Panel de Sesiones en Vivo*