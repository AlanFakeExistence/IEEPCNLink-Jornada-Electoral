# IEEPCNLink — Esquema de Base de Datos

> PostgreSQL 14+ · Extensión `pgcrypto` requerida

---

## Enums

| Tipo | Valores |
|------|---------|
| `estatus_casilla` | `pendiente` · `instalada` · `en_votacion` · `cerrada` · `en_computo` · `paquete_integrado` · `en_traslado` · `recibida_cme` |
| `tipo_incidencia` | `falta_funcionariado` · `conflicto` · `riesgo_seguridad` · `robo_material` · `error_actas` · `retraso_escrutinio` · `problema_traslado` · `paquete_con_observacion` · `otro` |
| `prioridad_incidencia` | `critica` · `alta` · `media` · `baja` |
| `estatus_paquete` | `en_casilla` · `en_traslado` · `en_cryt` · `saliendo_cryt` · `entregado_cme` |
| `opcion_entrega_paquete` | `directa` · `cryt_fijo` · `cryt_itinerante` · `dat` |

---

## Territorio

### `municipios`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | `gen_random_uuid()` |
| `nombre` | `TEXT NOT NULL` | |
| `created_at` | `TIMESTAMP` | `NOW()` |

### `zores` — Zonas de Responsabilidad Electoral

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `nombre` | `TEXT NOT NULL` | |
| `municipio_id` | `UUID FK → municipios` | |
| `created_at` | `TIMESTAMP` | |

### `ares` — Áreas de Responsabilidad Electoral

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `nombre` | `TEXT NOT NULL` | |
| `zore_id` | `UUID FK → zores` | |
| `created_at` | `TIMESTAMP` | |

---

## Personas

### `usuarios`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `nombre` | `TEXT NOT NULL` | |
| `rol` | `TEXT NOT NULL` | `cael` · `sel` · `coordinacion_central` · `dat` |
| `telegram_id` | `BIGINT UNIQUE` | ID de Telegram del usuario |
| `are_id` | `UUID FK → ares` | |
| `disponible` | `BOOLEAN` | default `true` |
| `activo` | `BOOLEAN` | default `true` — kill-switch de acceso |
| `created_at` | `TIMESTAMP` | |

---

## Casillas

### `casillas`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `clave` | `TEXT UNIQUE NOT NULL` | Clave oficial de la casilla |
| `seccion` | `TEXT` | Sección electoral |
| `tipo` | `TEXT` | `basica` · `contigua` · `extraordinaria` · `especial` |
| `municipio_id` | `UUID FK → municipios` | |
| `are_id` | `UUID FK → ares` | |
| `zore_id` | `UUID FK → zores` | |
| `estatus` | `estatus_casilla` | default `pendiente` |
| `lat` / `lng` | `DOUBLE PRECISION` | Coordenadas geográficas |
| `updated_at` | `TIMESTAMP` | |
| `created_at` | `TIMESTAMP` | |

---

## Operación Electoral

### `eventos_jornada`

Registro cronológico de los eventos operativos de cada casilla.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `casilla_id` | `UUID FK → casillas` | `ON DELETE CASCADE` |
| `tipo_evento` | `TEXT NOT NULL` | Ver valores abajo |
| `hora` | `TIMESTAMP` | `NOW()` |
| `usuario_id` | `UUID FK → usuarios` | Quien reporta |
| `observaciones` | `TEXT` | |
| `evidencia_url` | `TEXT` | URL de foto/documento |
| `lat` / `lng` | `DOUBLE PRECISION` | Georreferenciación del reporte |

**Valores `tipo_evento`:** `instalacion_confirmada` · `instalacion_no_confirmada` · `inicio_votacion` · `cierre_votacion` · `inicio_escrutinio` · `fin_escrutinio` · `paquete_integrado`

---

### `incidencias`

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `casilla_id` | `UUID FK → casillas` | `ON DELETE CASCADE` |
| `usuario_id` | `UUID FK → usuarios` | Quien reporta |
| `tipo` | `tipo_incidencia` | |
| `prioridad` | `prioridad_incidencia` | default `media` |
| `descripcion` | `TEXT` | |
| `observaciones` | `TEXT` | |
| `evidencia_url` | `TEXT` | |
| `estatus` | `TEXT` | `abierta` · `en_atencion` · `cerrada` |
| `hora_reporte` | `TIMESTAMP` | |
| `hora_cierre` | `TIMESTAMP` | |
| `escalado_a` | `UUID FK → usuarios` | Supervisor al que se escala |
| `updated_at` | `TIMESTAMP` | |

---

### `alertas`

Mensajes proactivos generados por el sistema o por incidencias.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `casilla_id` | `UUID FK → casillas` | `ON DELETE SET NULL` |
| `incidencia_id` | `UUID FK → incidencias` | `ON DELETE SET NULL` |
| `prioridad` | `prioridad_incidencia` | default `media` |
| `tipo_alerta` | `TEXT` | `incidencia` · `inactividad` · `paquete_detenido` · `apertura_tardia` |
| `titulo` | `TEXT` | |
| `mensaje` | `TEXT NOT NULL` | |
| `enviada` | `BOOLEAN` | default `false` |
| `enviada_at` | `TIMESTAMP` | |
| `created_at` | `TIMESTAMP` | |

---

## Paquete Electoral y Cadena de Custodia

### `paquetes_electorales`

Un paquete por casilla (relación `1:1` enforced por `UNIQUE`).

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `casilla_id` | `UUID UNIQUE FK → casillas` | `ON DELETE CASCADE` |
| `responsable_id` | `UUID FK → usuarios` | |
| `responsable_nombre` | `TEXT` | Nombre libre (por si no está en usuarios) |
| `opcion_entrega` | `opcion_entrega_paquete` | |
| `estatus` | `estatus_paquete` | default `en_casilla` |
| `estado_fisico` | `TEXT` | `sin_observacion` · `con_observacion` |
| `observaciones` | `TEXT` | |
| `hora_integracion` | `TIMESTAMP` | |
| `hora_salida_casilla` | `TIMESTAMP` | |
| `hora_recepcion_cme` | `TIMESTAMP` | |
| `updated_at` / `created_at` | `TIMESTAMP` | |

---

### `cadena_custodia`

Audit trail de cada movimiento del paquete electoral.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `paquete_id` | `UUID FK → paquetes_electorales` | `ON DELETE CASCADE` |
| `responsable_id` | `UUID FK → usuarios` | |
| `responsable_nombre` | `TEXT` | |
| `evento` | `TEXT NOT NULL` | `sale_casilla` · `llega_cryt` · `sale_cryt` · `llega_cme` · `acuse_generado` |
| `ubicacion` | `TEXT` | Descripción textual |
| `lat` / `lng` | `DOUBLE PRECISION` | |
| `hora` | `TIMESTAMP` | |
| `observaciones` | `TEXT` | |

---

## Sistema Agéntico

### `agent_logs`

Log de decisiones y resoluciones del sistema multi-agente.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `session_id` | `TEXT` | ID de sesión de conversación |
| `agent_type` | `TEXT NOT NULL` | `orquestador` · `instalacion` · `monitoreo` · `incidencias` · `computo` · `logistica` · `custodia` |
| `usuario_id` | `UUID FK → usuarios` | |
| `intent_detectado` | `TEXT` | Intención clasificada por el agente |
| `pudo_resolver` | `BOOLEAN` | ¿El agente resolvió sin escalar? |
| `nivel` | `TEXT` | `info` · `warning` · `error` |
| `mensaje` | `TEXT` | |
| `created_at` | `TIMESTAMP` | |

---

### `agent_sessions`

Memoria de chat para `memoryPostgresChat` de n8n. Ventana de 10 mensajes por sesión.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `BIGSERIAL PK` | |
| `session_id` | `VARCHAR(255) NOT NULL` | `telegram_chat_id` |
| `message` | `JSONB NOT NULL` | Mensaje serializado |
| `created_at` | `TIMESTAMP NOT NULL` | |

---

## Catálogos y Tablas Maestras

### `catalogo_incidencias`

Fuente de verdad para pesos de score y acciones sugeridas.

| Columna | Tipo | Notas |
|---------|------|-------|
| `tipo` | `TEXT PK` | Coincide con enum `tipo_incidencia` |
| `nombre` | `TEXT NOT NULL` | Etiqueta legible |
| `descripcion` | `TEXT` | |
| `prioridad_default` | `TEXT` | `critica` · `alta` · `media` · `baja` |
| `peso_score` | `INTEGER` | default `10` |
| `accion_sugerida` | `TEXT` | Texto para el agente/dashboard |
| `activo` | `BOOLEAN` | default `true` |

**Datos pre-cargados:**

| tipo | prioridad | peso |
|------|-----------|------|
| `falta_funcionariado` | alta | 50 |
| `conflicto` | media | 15 |
| `riesgo_seguridad` | critica | 100 |
| `robo_material` | critica | 100 |
| `error_actas` | media | 15 |
| `retraso_escrutinio` | alta | 50 |
| `problema_traslado` | alta | 50 |
| `paquete_con_observacion` | alta | 50 |
| `otro` | media | 10 |

---

### `eventos_unificados`

Tabla append-only que alimenta el dashboard en tiempo real.

| Columna | Tipo | Notas |
|---------|------|-------|
| `id` | `UUID PK` | |
| `tipo_evento` | `TEXT NOT NULL` | `estatus_casilla` · `incidencia` · `paquete` · `alerta_proactiva` |
| `entidad_id` | `UUID` | FK polimórfica al registro de origen |
| `casilla_id` | `UUID FK → casillas` | `ON DELETE SET NULL` |
| `prioridad` | `TEXT` | |
| `payload` | `JSONB` | default `{}` |
| `lat` / `lng` | `DOUBLE PRECISION` | |
| `creado_en` | `TIMESTAMP` | |

---

## Vista

### `casilla_score`

Score de urgencia compuesto por cuatro factores. Consulta típica:

```sql
SELECT * FROM casilla_score WHERE score > 0 ORDER BY score DESC LIMIT 50;
```

| Columna | Descripción | Puntos |
|---------|-------------|--------|
| `score_incidencias` | Suma ponderada de incidencias abiertas × tiempo transcurrido (cap 5×) | variable |
| `score_inactividad` | Sin actualización > 45 min y no en estado `recibida_cme` | +40 |
| `score_paquete_detenido` | Paquete en tránsito sin movimiento > 30 min | +60 |
| `score_apertura_tardia` | Casilla `pendiente` después de las 08:15 CST | +30 |
| **`score`** | **Suma total** | |

---

## Índices

| Índice | Tabla | Columnas |
|--------|-------|----------|
| `idx_casillas_are` | `casillas` | `are_id` |
| `idx_casillas_estatus` | `casillas` | `estatus` |
| `idx_casillas_updated` | `casillas` | `updated_at` |
| `idx_incidencias_casilla` | `incidencias` | `casilla_id` |
| `idx_incidencias_estatus` | `incidencias` | `estatus, casilla_id, hora_reporte DESC` |
| `idx_incidencias_prioridad` | `incidencias` | `prioridad, estatus` |
| `idx_alertas_enviada_prio` | `alertas` | `enviada, prioridad` WHERE `enviada = FALSE` |
| `idx_alertas_casilla` | `alertas` | `casilla_id, created_at DESC` |
| `idx_paquetes_estatus` | `paquetes_electorales` | `estatus, updated_at` |
| `idx_cadena_paquete` | `cadena_custodia` | `paquete_id, hora DESC` |
| `idx_eventos_casilla_tipo` | `eventos_jornada` | `casilla_id, tipo_evento` |
| `idx_eu_casilla` | `eventos_unificados` | `casilla_id, creado_en DESC` |
| `idx_eu_tipo` | `eventos_unificados` | `tipo_evento, creado_en DESC` |
| `idx_eu_prio` | `eventos_unificados` | `prioridad` WHERE `critica / alta` |
| `idx_usuarios_telegram` | `usuarios` | `telegram_id` |
| `idx_agent_logs_session` | `agent_logs` | `session_id` |
| `idx_agent_sessions` | `agent_sessions` | `session_id, created_at` |

---

## Relaciones (resumen)

```
municipios
  └── zores
        └── ares
              └── usuarios
              └── casillas ──── eventos_jornada
                           ──── incidencias ─── alertas
                           ──── paquetes_electorales ─── cadena_custodia
                           ──── alertas
                           ──── eventos_unificados

agent_logs    → usuarios
agent_sessions (independiente, keyed by telegram_chat_id)
catalogo_incidencias → (referenciado por incidencias.tipo vía JOIN)
```
