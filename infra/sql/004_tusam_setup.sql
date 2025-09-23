-- =====================================================
-- Setup TUSAM (compania_id=1) para resolución de tenant
-- =====================================================

-- 1) Verificar/crear compañía TUSAM
SELECT 'Verificando compañía TUSAM...' as status;

SELECT id, nombre FROM companias WHERE id=1;

-- Si no existe, crear TUSAM
INSERT INTO companias(id, nombre, estado, creado_en) 
VALUES (1, 'TUSAM VENEZUELA', 1, NOW())
ON DUPLICATE KEY UPDATE 
    nombre=VALUES(nombre),
    estado=VALUES(estado),
    creado_en=VALUES(creado_en);

-- Verificar creación
SELECT 'Compañía TUSAM creada/actualizada:' as status;
SELECT id, nombre, estado, creado_en FROM companias WHERE id=1;

-- 2) Asegurar dispositivo principal TUSAM
SELECT 'Configurando dispositivo principal TUSAM...' as status;

INSERT INTO ar_dispositivos(compania_id, device_alias, phone_wa, token, estado)
VALUES (1, 'TUSAM_MAIN', '58421234567', 'TOKEN_TUSAM_MAIN', 1)
ON DUPLICATE KEY UPDATE 
    token=VALUES(token),
    estado=VALUES(estado),
    phone_wa=VALUES(phone_wa);

-- Verificar dispositivo
SELECT 'Dispositivo TUSAM creado/actualizado:' as status;
SELECT id, compania_id, device_alias, phone_wa, token, estado 
FROM ar_dispositivos 
WHERE compania_id=1 AND device_alias='TUSAM_MAIN';

-- 3) Crear mapeo cliente->compañía para fallback por teléfono
SELECT 'Configurando mapeo cliente TUSAM...' as status;

INSERT INTO wa_clientes_compania(phone_cliente, compania_id)
VALUES ('584247810736', 1)
ON DUPLICATE KEY UPDATE compania_id=VALUES(compania_id);

-- Verificar mapeo
SELECT 'Mapeo cliente TUSAM creado/actualizado:' as status;
SELECT phone_cliente, compania_id 
FROM wa_clientes_compania 
WHERE compania_id=1 AND phone_cliente='584247810736';

-- 4) Verificación final
SELECT '=== VERIFICACIÓN FINAL TUSAM ===' as status;

SELECT 'Compañía:' as tabla, id, nombre, estado FROM companias WHERE id=1
UNION ALL
SELECT 'Dispositivo:' as tabla, id, compania_id, device_alias FROM ar_dispositivos WHERE compania_id=1 AND device_alias='TUSAM_MAIN'
UNION ALL
SELECT 'Cliente:' as tabla, phone_cliente, compania_id, 'mapped' FROM wa_clientes_compania WHERE compania_id=1 AND phone_cliente='584247810736';

SELECT 'TUSAM configurado correctamente para resolución de tenant' as resultado;
