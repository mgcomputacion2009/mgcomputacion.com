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
El tenant se identifica por el **número de teléfono entrante** del cliente, que se mapea a una compañía específica.

## Mapeo Número → Compañía

### Tabla de Mapeo
```sql
CREATE TABLE tenant_phone_mapping (
    id INT PRIMARY KEY AUTO_INCREMENT,
    phone_pattern VARCHAR(20) NOT NULL,
    compania_id INT NOT NULL,
    priority INT DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compania_id) REFERENCES companias(id)
);
```

### Reglas de Mapeo

#### 1. Mapeo Exacto
```json
{
  "phone_pattern": "+5215512345678",
  "compania_id": 1,
  "priority": 100
}
```

#### 2. Mapeo por Prefijo
```json
{
  "phone_pattern": "+52155*",
  "compania_id": 2,
  "priority": 50
}
```

#### 3. Mapeo por Rango
```json
{
  "phone_pattern": "+5215512345XXX",
  "compania_id": 3,
  "priority": 75
}
```

### Algoritmo de Selección
```python
def seleccionar_tenant(numero_telefono):
    """
    Selecciona el tenant basado en el número de teléfono entrante
    """
    # 1. Buscar mapeo exacto
    mapeo_exacto = buscar_mapeo_exacto(numero_telefono)
    if mapeo_exacto:
        return mapeo_exacto.compania_id
    
    # 2. Buscar por patrones (ordenado por prioridad)
    patrones = buscar_patrones(numero_telefono)
    if patrones:
        return patrones[0].compania_id
    
    # 3. Tenant por defecto
    return obtener_tenant_default()
```

## Carga de Configuración por Compañía

### 1. Prompts y Plantillas

#### Estructura de Archivos
```
prompts/
├── sistema/
│   ├── default/
│   │   ├── saludo.md
│   │   ├── despedida.md
│   │   └── error.md
│   └── compania_1/
│       ├── saludo.md
│       ├── despedida.md
│       └── error.md
├── intent_detection/
│   ├── default/
│   │   └── clasificador.md
│   └── compania_1/
│       └── clasificador.md
└── plantillas_respuesta/
    ├── default/
    │   ├── consulta_precios.md
    │   └── crear_pedido.md
    └── compania_1/
        ├── consulta_precios.md
        └── crear_pedido.md
```

#### Carga Dinámica
```python
def cargar_prompt(compania_id, tipo_prompt, nombre_archivo):
    """
    Carga prompt específico de la compañía o fallback a default
    """
    # 1. Intentar cargar desde directorio de la compañía
    ruta_compania = f"prompts/{tipo_prompt}/compania_{compania_id}/{nombre_archivo}"
    if archivo_existe(ruta_compania):
        return cargar_archivo(ruta_compania)
    
    # 2. Fallback a default
    ruta_default = f"prompts/{tipo_prompt}/default/{nombre_archivo}"
    return cargar_archivo(ruta_default)
```

### 2. Configuración de Sistema

#### Tabla de Configuración
```sql
CREATE TABLE tenant_config (
    id INT PRIMARY KEY AUTO_INCREMENT,
    compania_id INT NOT NULL,
    clave VARCHAR(100) NOT NULL,
    valor TEXT NOT NULL,
    tipo ENUM('string', 'number', 'boolean', 'json') NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compania_id) REFERENCES companias(id),
    UNIQUE KEY unique_config (compania_id, clave)
);
```

#### Configuraciones por Compañía
```json
{
  "compania_id": 1,
  "configuraciones": {
    "llm_model": "gpt-4",
    "max_sesiones_activas": 100,
    "tiempo_timeout": 300,
    "idioma_default": "es",
    "moneda": "MXN",
    "zona_horaria": "America/Mexico_City",
    "horario_atencion": {
      "inicio": "09:00",
      "fin": "18:00",
      "dias": ["lunes", "martes", "miercoles", "jueves", "viernes"]
    }
  }
}
```

### 3. Flags de Funcionalidad

#### Tabla de Flags
```sql
CREATE TABLE tenant_flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    compania_id INT NOT NULL,
    flag_name VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    configuracion JSON,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compania_id) REFERENCES companias(id),
    UNIQUE KEY unique_flag (compania_id, flag_name)
);
```

#### Flags Disponibles
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
    "soporte_humano": {
      "enabled": true,
      "configuracion": {
        "horario_disponible": "24/7",
        "transferencia_automatica": false,
        "tiempo_espera_maximo": 300
      }
    }
  }
}
```

## Aislamiento de Datos

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
        # Extraer número de teléfono del request
        numero_telefono = extraer_telefono(request)
        
        # Identificar tenant
        compania_id = seleccionar_tenant(numero_telefono)
        
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
    
    def get_prompt(self, tipo, nombre):
        return cargar_prompt(self.compania_id, tipo, nombre)
    
    def is_flag_enabled(self, flag_name):
        return self.tenant_flags.get(flag_name, {}).get('enabled', False)
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
    
    # Usar prompts específicos del tenant
    prompt_sistema = prompts.get('sistema', 'saludo')
    
    return llamar_llm(mensaje, modelo, prompt_sistema)
```

### 3. Generación de Respuestas
```python
def generar_respuesta(tipo_respuesta, datos, compania_id):
    """
    Genera respuesta usando plantillas del tenant
    """
    plantillas = cargar_plantillas(compania_id)
    flags = cargar_flags(compania_id)
    
    # Verificar si la funcionalidad está habilitada
    if not flags.get(tipo_respuesta, {}).get('enabled', False):
        return generar_respuesta_fallback(tipo_respuesta)
    
    # Usar plantilla específica del tenant
    plantilla = plantillas.get(tipo_respuesta)
    return renderizar_plantilla(plantilla, datos)
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
        'errores_por_hora': contar_errores(compania_id, periodo)
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
