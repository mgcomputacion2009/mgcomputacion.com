# Arquitectura Multi-Tenant - MGComputacion

## Propósito

Especificación de la arquitectura multi-tenant para el sistema MGComputacion, incluyendo reglas de selección de perfil de compañía, aislamiento de datos y configuración por tenant.

## Conceptos Clave

### Tenant (Compañía)
Cada compañía que utiliza el sistema es un tenant independiente con:
- Configuración propia
- Datos aislados
- Prompts personalizados
- Reglas de negocio específicas

### Identificación de Tenant
El tenant se identifica por el **número de WhatsApp Business** (`numero_wa`) que se mapea a una compañía específica.

## Mapeo Número WhatsApp → Compañía

### Tabla de Mapeo
```sql
CREATE TABLE tenant_phone_mapping (
    id INT PRIMARY KEY AUTO_INCREMENT,
    numero_wa VARCHAR(20) NOT NULL,
    compania_id INT NOT NULL,
    priority INT DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compania_id) REFERENCES companias(id)
);
```

### Reglas de Mapeo

#### 1. Mapeo Exacto
```json
{
  "numero_wa": "+5215512345678",
  "compania_id": 1,
  "priority": 100
}
```

#### 2. Mapeo por Prefijo
```json
{
  "numero_wa": "+52155*",
  "compania_id": 2,
  "priority": 50
}
```

#### 3. Mapeo por Rango
```json
{
  "numero_wa": "+5215512345XXX",
  "compania_id": 3,
  "priority": 75
}
```

### Algoritmo de Selección
```python
def seleccionar_tenant(numero_wa):
    """
    Selecciona el tenant basado en el número de WhatsApp entrante
    """
    # 1. Buscar mapeo exacto
    mapeo_exacto = buscar_mapeo_exacto(numero_wa)
    if mapeo_exacto:
        return mapeo_exacto.compania_id
    
    # 2. Buscar por patrones (ordenado por prioridad)
    patrones = buscar_patrones(numero_wa)
    if patrones:
        return patrones[0].compania_id
    
    # 3. Tenant por defecto
    return obtener_tenant_default()
```

## Carga de Prompts y Plantillas por Compañía

### 1. Estructura de Archivos
```
prompts/
├── sistema/
│   ├── v1/
│   │   ├── default/
│   │   │   ├── saludo.md
│   │   │   ├── despedida.md
│   │   │   └── error.md
│   │   └── compania_1/
│   │       ├── saludo.md
│   │       ├── despedida.md
│   │       └── error.md
│   └── v2/
│       ├── default/
│       └── compania_1/
├── intent_detection/
│   ├── v1/
│   │   ├── default/
│   │   └── compania_1/
│   └── v2/
└── plantillas_respuesta/
    ├── v1/
    └── v2/
```

### 2. Carga Dinámica con Versionado
```python
def cargar_prompt(compania_id, tipo_prompt, nombre_archivo, version="v1"):
    """
    Carga prompt específico de la compañía con versionado
    """
    # 1. Intentar cargar desde directorio de la compañía
    ruta_compania = f"prompts/{tipo_prompt}/{version}/compania_{compania_id}/{nombre_archivo}"
    if archivo_existe(ruta_compania):
        return cargar_archivo(ruta_compania)
    
    # 2. Fallback a default de la versión
    ruta_default = f"prompts/{tipo_prompt}/{version}/default/{nombre_archivo}"
    if archivo_existe(ruta_default):
        return cargar_archivo(ruta_default)
    
    # 3. Fallback a versión anterior
    if version != "v1":
        return cargar_prompt(compania_id, tipo_prompt, nombre_archivo, "v1")
    
    # 4. Error si no se encuentra
    raise PromptNotFoundError(f"Prompt no encontrado: {tipo_prompt}/{nombre_archivo}")
```

### 3. Configuración de Versión por Compañía
```json
{
  "compania_id": 1,
  "version_prompts": {
    "sistema": "v2",
    "intent_detection": "v1",
    "plantillas_respuesta": "v2"
  },
  "fecha_actualizacion": "2025-09-23T04:00:00Z"
}
```

## Aislamiento de Datos y Logs

### 1. Aislamiento a Nivel de Base de Datos

#### Filtrado Automático
```python
class TenantAwareModel:
    """
    Modelo base que incluye filtrado automático por tenant
    """
    def __init__(self, compania_id):
        self.compania_id = compania_id
    
    def get_queryset(self):
        return self.model.objects.filter(compania_id=self.compania_id)
    
    def create(self, **kwargs):
        kwargs['compania_id'] = self.compania_id
        return self.model.objects.create(**kwargs)
```

#### Middleware de Tenant
```python
class TenantMiddleware:
    """
    Middleware que identifica y establece el tenant en cada request
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extraer número de WhatsApp del request
        numero_wa = extraer_numero_wa(request)
        
        # Identificar tenant
        compania_id = seleccionar_tenant(numero_wa)
        
        # Establecer en el contexto de la request
        request.tenant_id = compania_id
        request.tenant_config = cargar_configuracion(compania_id)
        
        response = self.get_response(request)
        return response
```

### 2. Aislamiento de Logs

#### Estructura de Logs por Tenant
```
logs/
├── compania_1/
│   ├── 2025-09-23/
│   │   ├── sesiones.log
│   │   ├── errores.log
│   │   └── auditoria.log
│   └── 2025-09-24/
├── compania_2/
│   └── 2025-09-23/
└── sistema/
    ├── 2025-09-23/
    └── 2025-09-24/
```

#### Configuración de Logging
```python
def configurar_logging_tenant(compania_id):
    """
    Configura logging específico para el tenant
    """
    log_config = {
        'version': 1,
        'handlers': {
            'tenant_file': {
                'class': 'logging.FileHandler',
                'filename': f'logs/compania_{compania_id}/{datetime.now().strftime("%Y-%m-%d")}/sesiones.log',
                'formatter': 'tenant_formatter'
            }
        },
        'loggers': {
            f'tenant_{compania_id}': {
                'handlers': ['tenant_file'],
                'level': 'INFO'
            }
        }
    }
    return log_config
```

### 3. Aislamiento de Sesiones

#### Contexto de Sesión
```python
class SessionContext:
    """
    Contexto de sesión que incluye información del tenant
    """
    def __init__(self, session_id, compania_id):
        self.session_id = session_id
        self.compania_id = compania_id
        self.tenant_config = cargar_configuracion(compania_id)
        self.tenant_prompts = cargar_prompts(compania_id)
        self.tenant_flags = cargar_flags(compania_id)
    
    def get_prompt(self, tipo, nombre, version=None):
        if not version:
            version = self.tenant_config.get(f'version_prompts.{tipo}', 'v1')
        return cargar_prompt(self.compania_id, tipo, nombre, version)
    
    def is_flag_enabled(self, flag_name):
        return self.tenant_flags.get(flag_name, {}).get('enabled', False)
```

## Flags de Features por Compañía

### 1. Tabla de Flags
```sql
CREATE TABLE tenant_flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    compania_id INT NOT NULL,
    flag_name VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    configuracion JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compania_id) REFERENCES companias(id),
    UNIQUE KEY unique_flag (compania_id, flag_name)
);
```

### 2. Flags Disponibles
```json
{
  "flags": {
    "menu_productos": {
      "enabled": true,
      "configuracion": {
        "categorias_visibles": ["laptops", "desktops", "accesorios"],
        "mostrar_precios": true,
        "filtros_disponibles": ["marca", "precio", "categoria"]
      }
    },
    "cierre_venta": {
      "enabled": true,
      "configuracion": {
        "metodos_pago": ["transferencia", "efectivo", "tarjeta"],
        "requerir_direccion": true,
        "confirmacion_automatica": false
      }
    },
    "envio_datos_pago": {
      "enabled": false,
      "configuracion": {
        "metodo_envio": "whatsapp",
        "formato": "pdf",
        "incluir_instrucciones": true
      }
    },
    "panel_activo": {
      "enabled": true,
      "configuracion": {
        "acceso_24_7": true,
        "notificaciones_push": true,
        "dashboard_personalizado": true
      }
    }
  }
}
```

## Estrategia de Versionado de Prompts

### 1. Estructura de Versiones
```
prompts/
├── sistema/
│   ├── v1/          # Versión estable
│   ├── v2/          # Versión en desarrollo
│   └── v3/          # Versión experimental
├── intent_detection/
│   ├── v1/
│   └── v2/
└── plantillas_respuesta/
    ├── v1/
    └── v2/
```

### 2. Configuración de Versión por Compañía
```json
{
  "compania_id": 1,
  "version_prompts": {
    "sistema": "v2",
    "intent_detection": "v1",
    "plantillas_respuesta": "v2"
  },
  "fecha_actualizacion": "2025-09-23T04:00:00Z",
  "version_anterior": {
    "sistema": "v1",
    "intent_detection": "v1",
    "plantillas_respuesta": "v1"
  }
}
```

### 3. Migración de Versiones
```python
def migrar_prompts_tenant(compania_id, tipo_prompt, version_anterior, version_nueva):
    """
    Migra prompts de una versión a otra para un tenant específico
    """
    # 1. Crear backup de la versión actual
    crear_backup_prompts(compania_id, tipo_prompt, version_anterior)
    
    # 2. Copiar prompts de default a tenant
    copiar_prompts_default(compania_id, tipo_prompt, version_nueva)
    
    # 3. Aplicar personalizaciones específicas
    aplicar_personalizaciones(compania_id, tipo_prompt, version_nueva)
    
    # 4. Actualizar configuración
    actualizar_configuracion_version(compania_id, tipo_prompt, version_nueva)
    
    # 5. Validar prompts
    validar_prompts_tenant(compania_id, tipo_prompt, version_nueva)
```

### 4. Rollback de Versiones
```python
def rollback_prompts_tenant(compania_id, tipo_prompt, version_objetivo):
    """
    Hace rollback de prompts a una versión anterior
    """
    # 1. Validar que la versión objetivo existe
    if not version_existe(tipo_prompt, version_objetivo):
        raise VersionNotFoundError(f"Versión {version_objetivo} no encontrada")
    
    # 2. Restaurar desde backup
    restaurar_backup_prompts(compania_id, tipo_prompt, version_objetivo)
    
    # 3. Actualizar configuración
    actualizar_configuracion_version(compania_id, tipo_prompt, version_objetivo)
    
    # 4. Notificar cambio
    notificar_cambio_version(compania_id, tipo_prompt, version_objetivo)
```

## Reglas de Negocio por Tenant

### 1. Validación de Datos
```python
def validar_datos_tenant(datos, compania_id):
    """
    Valida datos según las reglas del tenant
    """
    config = cargar_configuracion(compania_id)
    
    # Validar formato de teléfono según configuración
    if not validar_telefono(datos['telefono'], config['formato_telefono']):
        raise ValidationError("Formato de teléfono inválido")
    
    # Validar moneda según configuración
    if not validar_moneda(datos['precio'], config['moneda']):
        raise ValidationError("Moneda no soportada")
    
    return True
```

### 2. Procesamiento de LLM
```python
def procesar_con_llm(mensaje, compania_id):
    """
    Procesa mensaje con LLM usando configuración del tenant
    """
    config = cargar_configuracion(compania_id)
    prompts = cargar_prompts(compania_id)
    
    # Usar modelo específico del tenant
    modelo = config.get('llm_model', 'gpt-3.5-turbo')
    
    # Usar prompts específicos del tenant con versionado
    version = config.get('version_prompts.sistema', 'v1')
    prompt_sistema = prompts.get('sistema', 'saludo', version)
    
    return llamar_llm(mensaje, modelo, prompt_sistema)
```

## Monitoreo y Auditoría

### 1. Métricas por Tenant
```python
def obtener_metricas_tenant(compania_id, periodo):
    """
    Obtiene métricas específicas del tenant
    """
    return {
        'sesiones_activas': contar_sesiones_activas(compania_id),
        'tiempo_respuesta_promedio': calcular_tiempo_respuesta(compania_id, periodo),
        'conversion_pedidos': calcular_conversion(compania_id, periodo),
        'errores_por_hora': contar_errores(compania_id, periodo),
        'version_prompts_activa': obtener_version_prompts(compania_id)
    }
```

### 2. Logs de Auditoría
```python
def registrar_auditoria_tenant(compania_id, accion, datos):
    """
    Registra acción de auditoría específica del tenant
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'compania_id': compania_id,
        'accion': accion,
        'datos': datos,
        'usuario': obtener_usuario_actual(),
        'ip': obtener_ip_actual()
    }
    
    escribir_log_auditoria(compania_id, log_entry)
```

## Consideraciones de Seguridad

### 1. Aislamiento de Datos
- **Filtrado obligatorio**: Todas las consultas incluyen `compania_id`
- **Validación de acceso**: Verificar tenant en cada operación
- **Encriptación**: Datos sensibles encriptados por tenant

### 2. Configuración de Seguridad
```json
{
  "seguridad": {
    "encriptacion_datos": true,
    "retencion_logs_dias": 90,
    "acceso_cross_tenant": false,
    "auditoria_obligatoria": true,
    "backup_por_tenant": true
  }
}
```

## Implementación

### 1. Migración de Datos
```python
def migrar_a_multi_tenant():
    """
    Migra datos existentes a estructura multi-tenant
    """
    # Asignar tenant por defecto a datos existentes
    datos_existentes = obtener_datos_sin_tenant()
    for dato in datos_existentes:
        dato.compania_id = TENANT_DEFAULT
        dato.save()
```

### 2. Testing Multi-Tenant
```python
def test_aislamiento_tenant():
    """
    Verifica que los datos están correctamente aislados
    """
    # Crear datos para tenant 1
    crear_datos_tenant(1)
    
    # Crear datos para tenant 2
    crear_datos_tenant(2)
    
    # Verificar que tenant 1 no ve datos de tenant 2
    datos_tenant_1 = obtener_datos_tenant(1)
    assert len(datos_tenant_1) == 1
    assert datos_tenant_1[0].compania_id == 1
```

---
*Arquitectura Multi-Tenant diseñada para MGComputacion - Sistema de Mensajería Inteligente*