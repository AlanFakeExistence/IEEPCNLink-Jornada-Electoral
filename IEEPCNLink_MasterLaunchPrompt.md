# IEEPCNLink — Master Launch Prompt
> Copia y pega este documento completo como prompt de inicio para construir el proyecto desde cero.

---

## CONTEXTO DEL RETO

Eres un arquitecto de software especializado en sistemas electorales y automatización inteligente. Vas a construir **IEEPCNLink**, un sistema multi-agente de inteligencia operativa para el **Instituto Estatal Electoral y de Participación Ciudadana de Nuevo León (IEEPCNL)**.

### El problema a resolver

Durante la Jornada Electoral, los **Capacitadores Asistentes Electorales Locales (CAEL)** y **Supervisores Electorales Locales (SEL)** deben reportar en tiempo casi real: instalación de casillas, inicio de votación, incidencias de campo, cierre, escrutinio y cómputo, integración de paquetes electorales y traslado mediante mecanismos de recolección.

Este seguimiento depende de llamadas telefónicas, mensajes no estructurados y formatos dispersos, lo que impide:
- Priorizar riesgos en tiempo real
- Coordinar apoyos entre áreas
- Documentar evidencia trazable
- Conocer el estado real de cada casilla, ARE, ZORE o paquete electoral en tránsito

Una trazabilidad deficiente puede generar incertidumbre, retrasos y pérdida de control sobre la **cadena de custodia**, poniendo en riesgo los principios de certeza y legalidad del proceso electoral.

### Glosario operativo esencial

| Término | Definición operativa |
|---|---|
| **IEEPCNL** | Instituto Estatal Electoral y de Participación Ciudadana de Nuevo León. Organiza elecciones locales de Gubernatura, Diputaciones Locales y Ayuntamientos. |
| **Jornada Electoral** | Día en que la ciudadanía acude a votar. Momentos operativos: instalación, inicio de votación, desarrollo, atención de incidencias, cierre, escrutinio y cómputo, integración de paquetes y entrega. |
| **Casilla** | Lugar físico donde se recibe votación. Apertura 07:30 h, votación desde 08:00 h, cierre 18:00 h salvo fila. |
| **Mesa Directiva de Casilla** | Presidencia, dos Secretarías, tres Escrutadurías, tres Suplencias. |
| **CAEL** | Capacitador/a Asistente Electoral Local. Figura de campo temporal (30-45 días). Opera en su ARE, reporta incidencias, apoya traslado de paquetes. |
| **SEL** | Supervisor/a Electoral Local. Coordina y verifica actividades de CAEL dentro de una ZORE. |
| **ARE** | Área de Responsabilidad Electoral. Espacio operativo de un CAEL. 4-6 casillas promedio. |
| **ZORE** | Zona de Responsabilidad Electoral. Agrupa 5-6 ARE bajo un SEL. |
| **Paquete electoral** | Conjunto sellado de documentos: actas, sobres con boletas sobrantes, votos válidos, votos nulos, lista nominal. Viaja desde la casilla hasta la CME. |
| **Cadena de custodia** | Controles que aseguran que el paquete se mantenga íntegro, identificado, sellado y bajo responsabilidad conocida desde la casilla hasta la CME. |
| **CME** | Comisión Municipal Electoral. Órgano temporal que recibe los paquetes electorales al cierre de la jornada. |
| **CRyT Fijo** | Centro de Recepción y Traslado en inmueble autorizado. Recibe paquetes y los traslada a la CME. |
| **CRyT Itinerante** | Vehículo/ruta que recoge paquetes en puntos programados. |
| **DAT** | Dispositivo de Apoyo al Traslado. Vehículo que traslada al funcionariado y su paquete. |
| **Incidencia** | Evento fuera de lo normal que puede afectar instalación, votación, cierre, conteo, integración o traslado. |

### Flujo de la Jornada Electoral (8 momentos)

```
1. Instalación (07:30 h)
   └─ Funcionariado prepara casilla, arma urnas, llena Acta de Instalación

2. Inicio de votación (≈08:00 h)
   └─ Presidencia anuncia inicio; CAEL reporta al SEL

3. Desarrollo
   └─ Se recibe ciudadanía, se verifica lista nominal, reportes periódicos CAEL→SEL

4. Cierre (18:00 h o última persona en fila)
   └─ Se registra hora de cierre

5. Escrutinio y cómputo
   └─ Clasificación y conteo de votos; llenado de actas

6. Integración del paquete electoral
   └─ Se sellan actas, sobres y documentación; fotografía de evidencia

7. Recolección / traslado  ← PUNTO CRÍTICO
   └─ Opción A: Presidencia lleva el paquete directamente
   └─ Opción B: Presidencia entrega al CAEL para traslado
   └─ Opción C: CAEL acompaña al Presidente de Casilla

8. Entrega en CME
   └─ Recepción, registro, acuse, cierre de cadena de custodia
```

### Catálogo de incidencias y prioridades

| Incidencia | Prioridad | Acción |
|---|---|---|
| Violencia, riesgo de seguridad, paquete extraviado | **Crítica** | Escalar de inmediato, notificar autoridades |
| Falta de funcionariado sin resolver, vehículo no disponible, error grave en acta | **Alta** | Activar protocolo, notificar SEL |
| Duda de llenado, retraso moderado, documentación por confirmar | **Media** | Apoyo y validación |
| Aclaración administrativa, observación menor controlada | **Baja** | Registro, sin notificación adicional |

---

## ARQUITECTURA DEL SISTEMA

### Stack tecnológico (100% open source / gratuito)

| Herramienta | Rol | Versión sugerida |
|---|---|---|
| **N8N** | Motor de automatización y orquestación de agentes | v1.x |
| **PostgreSQL** | Base de datos central de trazabilidad | v15 |
| **Claude (Anthropic)** | LLM de los agentes de IA | claude-sonnet-4-6 |
| **Telegram Bot API** | Canal de comunicación con CAEL/SEL y alertas maestras | — |
| **Streamlit** | Dashboard web de supervisión operativa | v1.x |
| **SQLAlchemy + psycopg2** | Conexión Streamlit → PostgreSQL | — |
| **Nominatim / OSRM** | Geolocalización y rutas (OpenStreetMap, gratuito) | — |

### Reglas de construcción (NO negociables)

1. **Sin JavaScript** en ningún nodo de N8N. Solo nodos nativos.
2. **Sin herramientas basadas en funciones JS** en los agentes. Solo: Postgres node, HTTP Request node, Telegram node.
3. **Doble registro** de toda alerta o warning: INSERT en PostgreSQL + mensaje al canal maestro de Telegram.
4. **Roles diferenciados**: el orquestador consulta el perfil del usuario antes de clasificar la intención.
5. **Autoevaluación de cada agente**: IF node evalúa si el agente puede resolver; si no, re-enruta al orquestador.
6. **Las queries SQL de Streamlit** viven en archivos `.sql` separados en una carpeta `queries/`, no incrustadas en Python.

---

## CAPA 1 — BASE DE DATOS POSTGRESQL

### Esquema completo (9 tablas + índices)

```sql
-- ── TERRITORIO ──────────────────────────────────────────────────────────

CREATE TABLE zore (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre     TEXT NOT NULL,
  municipio  TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE are (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre     TEXT NOT NULL,
  zore_id    UUID NOT NULL REFERENCES zore(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ── PERSONAS Y CASILLAS ─────────────────────────────────────────────────

CREATE TABLE usuarios (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre      TEXT NOT NULL,
  rol         TEXT NOT NULL CHECK (rol IN ('cael','sel','coordinacion_central','dat')),
  telegram_id BIGINT UNIQUE,
  are_id      UUID REFERENCES are(id),
  disponible  BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE casillas (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  seccion              TEXT NOT NULL,
  municipio            TEXT NOT NULL,
  tipo                 TEXT CHECK (tipo IN ('basica','contigua','extraordinaria','especial')),
  are_id               UUID NOT NULL REFERENCES are(id),
  estatus_operativo    TEXT DEFAULT 'pendiente' CHECK (estatus_operativo IN (
                         'pendiente','instalada','votando','cerrada',
                         'en_escrutinio','paquete_integrado','en_traslado',
                         'entregada','proceso_completo','con_incidencia')),
  ultima_actualizacion TIMESTAMP DEFAULT NOW(),
  lat                  DECIMAL(9,6),
  lng                  DECIMAL(9,6)
);

-- ── OPERACIÓN ELECTORAL ─────────────────────────────────────────────────

CREATE TABLE eventos_jornada (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  casilla_id   UUID NOT NULL REFERENCES casillas(id),
  tipo_evento  TEXT NOT NULL,
  -- valores: instalacion_confirmada | instalacion_no_confirmada |
  --          inicio_votacion | cierre_votacion | inicio_escrutinio |
  --          fin_escrutinio | paquete_integrado
  hora         TIMESTAMP DEFAULT NOW(),
  usuario_id   UUID REFERENCES usuarios(id),
  observaciones TEXT,
  evidencia_url TEXT
);

CREATE TABLE incidencias (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  casilla_id    UUID NOT NULL REFERENCES casillas(id),
  usuario_id    UUID REFERENCES usuarios(id),
  tipo          TEXT NOT NULL,
  -- valores: falta_funcionariado | conflicto | riesgo_seguridad |
  --          robo_material | error_acta | retraso_escrutinio |
  --          problema_traslado | paquete_con_observacion | inactividad
  prioridad     TEXT NOT NULL CHECK (prioridad IN ('critica','alta','media','baja')),
  descripcion   TEXT,
  estatus       TEXT DEFAULT 'abierta' CHECK (estatus IN ('abierta','en_atencion','cerrada')),
  hora_reporte  TIMESTAMP DEFAULT NOW(),
  hora_cierre   TIMESTAMP,
  escalado_a    UUID REFERENCES usuarios(id)
);

CREATE TABLE alertas (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incidencia_id   UUID NOT NULL REFERENCES incidencias(id),
  tipo_alerta     TEXT NOT NULL,
  nivel           TEXT NOT NULL CHECK (nivel IN ('critica','alta','media','baja')),
  mensaje         TEXT NOT NULL,
  enviado_telegram BOOLEAN DEFAULT FALSE,
  telegram_msg_id  BIGINT,
  created_at      TIMESTAMP DEFAULT NOW()
);

-- ── PAQUETE Y CADENA DE CUSTODIA ────────────────────────────────────────

CREATE TABLE paquetes_electorales (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  casilla_id           UUID NOT NULL REFERENCES casillas(id),
  responsable_id       UUID REFERENCES usuarios(id),
  mecanismo            TEXT CHECK (mecanismo IN
                         ('entrega_directa','cryt_fijo','cryt_itinerante','dat')),
  estatus              TEXT DEFAULT 'integrado' CHECK (estatus IN
                         ('integrado','en_traslado','en_cryt','recibido_cme')),
  estado_fisico        TEXT CHECK (estado_fisico IN ('sin_observacion','con_observacion')),
  observaciones        TEXT,
  hora_integracion     TIMESTAMP,
  hora_salida_casilla  TIMESTAMP,
  hora_recepcion_cme   TIMESTAMP
);

CREATE TABLE cadena_custodia (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paquete_id      UUID NOT NULL REFERENCES paquetes_electorales(id),
  responsable_id  UUID REFERENCES usuarios(id),
  evento          TEXT NOT NULL,
  -- valores: sale_casilla | llega_cryt | sale_cryt | llega_cme | acuse_generado
  ubicacion       TEXT,
  lat             DECIMAL(9,6),
  lng             DECIMAL(9,6),
  hora            TIMESTAMP DEFAULT NOW(),
  observaciones   TEXT
);

-- ── SISTEMA AGÉNTICO ────────────────────────────────────────────────────

CREATE TABLE agent_logs (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id       TEXT,
  agent_type       TEXT NOT NULL,
  -- valores: orquestador | instalacion | monitoreo | incidencias |
  --          computo | logistica | custodia
  usuario_id       UUID REFERENCES usuarios(id),
  intent_detectado TEXT,
  pudo_resolver    BOOLEAN,
  nivel            TEXT CHECK (nivel IN ('info','warning','error')),
  mensaje          TEXT,
  created_at       TIMESTAMP DEFAULT NOW()
);

-- ── ÍNDICES ─────────────────────────────────────────────────────────────

CREATE INDEX idx_casillas_are       ON casillas(are_id);
CREATE INDEX idx_casillas_estatus   ON casillas(estatus_operativo);
CREATE INDEX idx_incidencias_casilla ON incidencias(casilla_id);
CREATE INDEX idx_incidencias_prio   ON incidencias(prioridad, estatus);
CREATE INDEX idx_alertas_nivel      ON alertas(nivel, enviado_telegram);
CREATE INDEX idx_cadena_paquete     ON cadena_custodia(paquete_id);
CREATE INDEX idx_eventos_casilla    ON eventos_jornada(casilla_id, tipo_evento);
CREATE INDEX idx_usuarios_telegram  ON usuarios(telegram_id);
CREATE INDEX idx_agent_logs_session ON agent_logs(session_id);
```

---

## CAPA 2 — SISTEMA MULTI-AGENTE N8N

### Principio de funcionamiento

```
[TRIGGER] → [SET node: normaliza entrada] → [POSTGRES node: perfil usuario]
    → [AI AGENT: orquestador] → {agent, confidence, user_role, context}
    → [SWITCH node: lee campo "agent"]
    → rama específica → [AI AGENT especializado]
    → [IF node: puede_resolver?]
         ├─ NO → INSERT agent_logs + vuelve al orquestador
         └─ SÍ → herramientas nativas → [IF node: nivel alerta?]
                      ├─ crítica/alta → [POSTGRES INSERT alertas] + [TELEGRAM maestro]
                      └─ info/baja   → [POSTGRES UPDATE estatus]
                      └─ [TELEGRAM: responde al usuario]
```

### Capa 1 — Triggers de entrada (4 nodos)

```
Telegram Bot Trigger  → CAEL y SEL reportan desde campo
                         Escucha texto libre + imágenes

Webhook Trigger       → App web / panel envía JSON estructurado
                         Body: {user_id, message, casilla_id, tipo}

Form Trigger          → Captura estructurada de eventos clave
                         Campos: tipo_evento, casilla, hora, observaciones

Schedule Trigger      → Cada 15 min durante jornada
                         Verifica casillas sin reporte > 45 min
                         Paquetes en traslado sin actualización > 30 min
```

### Capa 2 — Agente orquestador

**Nodo**: AI Agent node · LLM: Claude Sonnet  
**Memoria**: Window Buffer Memory + Postgres Chat Memory  
**Herramienta**: Postgres node → `SELECT rol, are_id, zore_id FROM usuarios WHERE telegram_id = :id`

**System prompt del orquestador**:
```
Eres el orquestador del sistema IEEPCNLink para el IEEPCNL de Nuevo León.
El usuario que escribe tiene rol: {{user_role}} y trabaja en ARE: {{are_id}}.

Analiza el mensaje en español de México con contexto electoral y clasifica
la intención en UNO de estos dominios:

- instalacion: apertura, checklist, acta de instalación, no llegó el funcionariado
- monitoreo: estatus, cuántas casillas, reporte, tablero, avance
- incidencias: problema, conflicto, robo, violencia, error, falta material
- computo: votos, escrutinio, actas, paquete, cerrar casilla
- logistica: traslado, CRyT, DAT, ruta, llevar el paquete
- custodia: entregué, CME, recibieron, acuse, cadena de custodia
- fallback: no puedes clasificar con seguridad

Responde ÚNICAMENTE con este JSON (sin texto adicional):
{
  "agent": "<dominio>",
  "confidence": <0-100>,
  "user_role": "{{user_role}}",
  "are_id": "{{are_id}}",
  "zore_id": "{{zore_id}}",
  "casilla_id": "<uuid o null>",
  "context": "<resumen de 1 oración de lo que necesita el usuario>",
  "original_message": "<mensaje original>"
}

Si confidence < 70 usa "agent": "fallback".
```

**Salida JSON del orquestador**:
```json
{
  "agent": "incidencias",
  "confidence": 92,
  "user_role": "cael",
  "are_id": "uuid-are-03",
  "zore_id": "uuid-zore-01",
  "casilla_id": "uuid-casilla-1205",
  "context": "Falta de funcionariado en casilla 1205, no llegó el presidente",
  "original_message": "El presidente de la 1205 no llegó, ya van 20 minutos"
}
```

### Capa 3 — Switch node (enrutador nativo)

```
Modo: Expression
Campo evaluado: {{ $json.agent }}

Ramas:
  "instalacion"  → Agente de instalación
  "monitoreo"    → Agente de monitoreo
  "incidencias"  → Agente de incidencias
  "computo"      → Agente de cómputo
  "logistica"    → Agente de logística
  "custodia"     → Agente de custodia
  "fallback"     → Telegram node: pide reformulación con botones inline
  default        → Re-envía al orquestador con nota de error
```

### Capa 4 — Agentes especializados

Todos los agentes usan este patrón de autoevaluación en su system prompt:

```
AUTOEVALUACIÓN (siempre ejecuta esto primero):
Antes de responder, evalúa si el mensaje pertenece a tu dominio: <DOMINIO>.
Si NO pertenece o no tienes datos suficientes en las herramientas disponibles,
responde SOLO con: {"puede_resolver": false, "razon": "<descripción breve>"}
Si SÍ puedes resolver, procede normalmente y al final incluye:
{"puede_resolver": true, "nivel_alerta": "<critica|alta|media|baja|ninguna>"}
```

El IF node evalúa `puede_resolver === false` y bifurca hacia re-enrutamiento.

---

#### Agente 1 — Instalación

**Dominio**: Fase 1 — apertura y verificación de casillas  
**System prompt foco**: Verificar que la casilla se instaló correctamente, registrar hora y funcionariado, detectar no-instalaciones.

**Herramientas nativas**:
```sql
-- Tool 1: Lista de casillas asignadas al ARE del usuario
SELECT id, seccion, municipio, estatus_operativo
FROM casillas
WHERE are_id = :are_id;

-- Tool 2: Registrar evento de instalación
INSERT INTO eventos_jornada (casilla_id, tipo_evento, hora, usuario_id, observaciones)
VALUES (:casilla_id, :tipo, NOW(), :usuario_id, :obs);

-- Tool 3: Actualizar estatus de casilla
UPDATE casillas
SET estatus_operativo = :estatus, ultima_actualizacion = NOW()
WHERE id = :casilla_id;
```

---

#### Agente 2 — Monitoreo

**Dominio**: Fase 2 — seguimiento en tiempo real del estado de casillas  
**System prompt foco**: Responder consultas de estatus del SEL, detectar zonas sin reporte, generar resúmenes de avance.

**Herramientas nativas**:
```sql
-- Tool 1: Estado actual del ARE o ZORE
SELECT c.seccion, c.municipio, c.estatus_operativo,
       c.ultima_actualizacion,
       EXTRACT(EPOCH FROM (NOW() - c.ultima_actualizacion))/60 AS minutos_sin_reporte
FROM casillas c
JOIN are ar ON ar.id = c.are_id
WHERE ar.zore_id = :zore_id OR c.are_id = :are_id;

-- Tool 2: Conteo por estatus
SELECT estatus_operativo, COUNT(*) AS total
FROM casillas
WHERE are_id = :are_id
GROUP BY estatus_operativo;
```

---

#### Agente 3 — Incidencias

**Dominio**: Fases 2 y 3 — clasificación y escalamiento de problemas en campo  
**System prompt foco**: Clasificar el tipo e impacto de la incidencia, sugerir el protocolo correcto, registrar y escalar según prioridad.

**Lógica de prioridad** (evalúa el LLM, no código):
- **Crítica**: riesgo a personas, paquete comprometido, casilla sin operar
- **Alta**: retraso significativo, falta funcionariado sin resolver
- **Media**: duda de llenado, retraso moderado
- **Baja**: observación menor ya controlada

**Herramientas nativas**:
```sql
-- Tool 1: Registrar incidencia
INSERT INTO incidencias
  (casilla_id, usuario_id, tipo, prioridad, descripcion, hora_reporte)
VALUES (:casilla_id, :usuario_id, :tipo, :prioridad, :desc, NOW())
RETURNING id;

-- Tool 2: Actualizar incidencia existente
UPDATE incidencias
SET prioridad = :prioridad, estatus = :estatus, escalado_a = :escalado_a
WHERE id = :incidencia_id;

-- Tool 3: Marcar casilla con incidencia
UPDATE casillas
SET estatus_operativo = 'con_incidencia', ultima_actualizacion = NOW()
WHERE id = :casilla_id;
```

---

#### Agente 4 — Cómputo

**Dominio**: Fase 3 — escrutinio, validación de actas e integración del paquete  
**System prompt foco**: Registrar cierre y escrutinio, validar coherencia de totales reportados, marcar paquete como integrado y listo.

**Herramientas nativas**:
```sql
-- Tool 1: Registrar evento de cómputo
INSERT INTO eventos_jornada (casilla_id, tipo_evento, hora, usuario_id)
VALUES (:casilla_id, :tipo_evento, NOW(), :usuario_id);
-- tipo_evento: cierre_votacion | inicio_escrutinio | fin_escrutinio | paquete_integrado

-- Tool 2: Crear registro de paquete
INSERT INTO paquetes_electorales
  (casilla_id, responsable_id, hora_integracion, estatus)
VALUES (:casilla_id, :responsable_id, NOW(), 'integrado')
RETURNING id;

-- Tool 3: Verificar si ya existe paquete (evita duplicados)
SELECT id FROM paquetes_electorales WHERE casilla_id = :casilla_id;
```

---

#### Agente 5 — Logística

**Dominio**: Fase 4 — traslado del paquete desde casilla hasta CRyT o CME  
**System prompt foco**: Registrar salida del paquete, asignar mecanismo de recolección, rastrear estado, alertar ante retrasos.

**Herramientas nativas**:
```sql
-- Tool 1: Registrar salida del paquete
UPDATE paquetes_electorales
SET estatus = 'en_traslado', hora_salida_casilla = NOW(),
    mecanismo = :mecanismo, responsable_id = :responsable_id
WHERE id = :paquete_id;

-- Tool 2: Insertar evento en cadena de custodia
INSERT INTO cadena_custodia
  (paquete_id, responsable_id, evento, ubicacion, lat, lng, hora)
VALUES (:pid, :uid, :evento, :ubicacion, :lat, :lng, NOW());

-- Tool 3: Buscar vehículos DAT disponibles
SELECT u.id, u.nombre, ar.nombre AS are
FROM usuarios u
JOIN are ar ON ar.id = u.are_id
WHERE u.rol = 'dat' AND u.disponible = true;
```

**HTTP Request tool** (Nominatim): `GET https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json`

---

#### Agente 6 — Custodia

**Dominio**: Fase 5 — entrega final en CME y cierre de la cadena de custodia  
**System prompt foco**: Verificar integridad del paquete al recibir, registrar acuse, cerrar la cadena de custodia completa.

**Herramientas nativas**:
```sql
-- Tool 1: Confirmar recepción en CME
UPDATE paquetes_electorales
SET estatus = 'recibido_cme',
    hora_recepcion_cme = NOW(),
    estado_fisico = :estado_fisico,
    observaciones = :observaciones
WHERE id = :paquete_id;

-- Tool 2: Insertar evento final en cadena de custodia
INSERT INTO cadena_custodia
  (paquete_id, responsable_id, evento, ubicacion, hora, observaciones)
VALUES (:pid, :uid, 'entrega_cme', :ubicacion, NOW(), :obs);

-- Tool 3: Marcar casilla como proceso completo
UPDATE casillas
SET estatus_operativo = 'proceso_completo', ultima_actualizacion = NOW()
WHERE id = (SELECT casilla_id FROM paquetes_electorales WHERE id = :paquete_id);
```

### Sistema de alertas — flujo de doble registro

```
[Resultado del agente incluye nivel_alerta = "critica" o "alta"]
        │
        ▼
[IF node: nivel_alerta IN ('critica','alta')]
        │
   ┌────┴───────────────────────────┐
   ▼                                ▼
[Postgres node]                [Telegram node]
INSERT INTO alertas             Mensaje al chat_id maestro
(incidencia_id, tipo_alerta,    Formato:
 nivel, mensaje,                ────────────────────
 enviado_telegram = true,       🔴 ALERTA CRÍTICA
 created_at = NOW())            Tipo: {tipo}
                                Casilla: {seccion} (Sección {s})
                                ARE: {are} | ZORE: {zore}
                                Municipio: {municipio}
                                Reportado por: {nombre} ({rol})
                                Hora: {hora}
                                ────────────────────
                                Descripción: {descripcion}
                                Acción sugerida: {accion}
```

### Insert en agent_logs (todos los agentes al terminar)

```sql
INSERT INTO agent_logs
  (session_id, agent_type, usuario_id, intent_detectado,
   pudo_resolver, nivel, mensaje)
VALUES
  (:session_id, :agent_type, :usuario_id, :intent,
   :pudo_resolver, :nivel, :mensaje);
```

---

## CAPA 3 — DASHBOARD STREAMLIT

### Estructura de archivos

```
ieepcnlink_dashboard/
├── app.py                  # Entrada principal, detección de rol
├── auth.py                 # st.session_state, login básico
├── db.py                   # Conexión SQLAlchemy, run_query(), run_update()
├── .streamlit/
│   └── config.toml         # Tema institucional IEEPCNL
├── queries/
│   ├── pulso_general.sql
│   ├── alertas_activas.sql
│   ├── casillas_mapa.sql
│   ├── cadena_custodia_timeline.sql
│   └── disponibilidad_operativa.sql
└── pages/
    ├── 01_estado_global.py
    ├── 02_mapa_operativo.py
    ├── 03_alertas.py
    ├── 04_paquetes.py
    ├── 05_disponibilidad.py
    └── 06_bitacora.py
```

### Las 5 queries maestras (archivos .sql)

**`pulso_general.sql`** — KPIs del encabezado
```sql
SELECT
  COUNT(*) FILTER (WHERE estatus_operativo = 'instalada')        AS instaladas,
  COUNT(*) FILTER (WHERE estatus_operativo = 'votando')          AS votando,
  COUNT(*) FILTER (WHERE estatus_operativo = 'paquete_integrado') AS listas,
  COUNT(*) FILTER (WHERE estatus_operativo = 'en_traslado')      AS en_ruta,
  COUNT(*) FILTER (WHERE estatus_operativo = 'entregada')        AS entregadas,
  COUNT(*) FILTER (WHERE estatus_operativo = 'con_incidencia')   AS con_problema
FROM casillas;
```

**`alertas_activas.sql`** — Panel lateral de alertas
```sql
SELECT
  a.id, a.nivel, a.tipo_alerta, a.mensaje, a.created_at,
  i.tipo AS tipo_incidencia, i.prioridad,
  c.seccion, c.municipio,
  ar.nombre AS are, z.nombre AS zore
FROM alertas a
JOIN incidencias i  ON i.id = a.incidencia_id
JOIN casillas   c   ON c.id = i.casilla_id
JOIN are        ar  ON ar.id = c.are_id
JOIN zore       z   ON z.id = ar.zore_id
WHERE i.estatus IN ('abierta', 'en_atencion')
ORDER BY
  CASE a.nivel WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 END,
  a.created_at DESC;
```

**`casillas_mapa.sql`** — Mapa operativo con filtros
```sql
SELECT
  c.id, c.seccion, c.municipio, c.tipo,
  c.estatus_operativo, c.lat, c.lng,
  c.ultima_actualizacion,
  ar.nombre AS are, z.nombre AS zore,
  u.nombre  AS cael_responsable,
  EXTRACT(EPOCH FROM (NOW() - c.ultima_actualizacion))/60 AS minutos_sin_reporte
FROM casillas c
JOIN are  ar ON ar.id = c.are_id
JOIN zore z  ON z.id  = ar.zore_id
LEFT JOIN usuarios u ON u.are_id = c.are_id AND u.rol = 'cael'
WHERE (:municipio IS NULL OR c.municipio = :municipio)
  AND (:zore      IS NULL OR z.nombre    = :zore);
```

**`cadena_custodia_timeline.sql`** — Trazabilidad de paquetes
```sql
SELECT
  p.id AS paquete_id, c.seccion, c.municipio,
  p.mecanismo, p.estatus,
  p.hora_integracion, p.hora_salida_casilla, p.hora_recepcion_cme,
  cc.evento, cc.ubicacion, cc.hora AS hora_evento,
  u.nombre AS responsable
FROM paquetes_electorales p
JOIN casillas        c  ON c.id = p.casilla_id
JOIN cadena_custodia cc ON cc.paquete_id = p.id
JOIN usuarios        u  ON u.id = cc.responsable_id
WHERE p.estatus != 'recibido_cme'
ORDER BY p.id, cc.hora ASC;
```

**`disponibilidad_operativa.sql`** — Índice de carga CAEL/SEL
```sql
SELECT
  u.id, u.nombre, u.rol, u.disponible,
  ar.nombre AS are, z.nombre AS zore,
  COUNT(DISTINCT c.id) AS total_casillas,
  COUNT(c.id) FILTER (WHERE c.estatus_operativo = 'proceso_completo') AS completadas,
  COUNT(i.id) FILTER (WHERE i.estatus = 'abierta') AS incidencias_abiertas,
  ROUND(
    COUNT(i.id) FILTER (WHERE i.estatus = 'abierta')::numeric /
    NULLIF(COUNT(DISTINCT c.id), 0), 2
  ) AS indice_carga
FROM usuarios u
JOIN are  ar ON ar.id = u.are_id
JOIN zore z  ON z.id  = ar.zore_id
LEFT JOIN casillas    c ON c.are_id = u.are_id
LEFT JOIN incidencias i ON i.casilla_id = c.id
WHERE u.rol IN ('cael', 'sel')
GROUP BY u.id, u.nombre, u.rol, u.disponible, ar.nombre, z.nombre
ORDER BY indice_carga DESC;
```

### Acciones del operador — queries de escritura

```sql
-- Acción 1: Cambiar prioridad de incidencia
UPDATE incidencias
SET prioridad = :nueva_prioridad, escalado_a = :usuario_escalado
WHERE id = :incidencia_id;

-- Acción 2: Reasignar CAEL a ARE saturada
UPDATE usuarios
SET are_id = :nueva_are, disponible = false
WHERE id = :cael_id;

-- Acción 3: Confirmar recepción en CME
UPDATE paquetes_electorales
SET estatus = 'recibido_cme', hora_recepcion_cme = NOW(), estado_fisico = :estado
WHERE id = :paquete_id;

INSERT INTO cadena_custodia (paquete_id, responsable_id, evento, hora)
VALUES (:pid, :uid, 'entrega_cme', NOW());

-- Acción 4: Cerrar incidencia
UPDATE incidencias
SET estatus = 'cerrada', hora_cierre = NOW()
WHERE id = :incidencia_id;

-- Acción 5: Marcar casilla silenciosa como crítica
INSERT INTO incidencias (casilla_id, tipo, prioridad, descripcion, hora_reporte)
VALUES (:cid, 'inactividad', 'alta', 'Sin reporte desde dashboard operativo', NOW());

-- Acción 6: Exportar bitácora (sin SQL adicional)
-- st.download_button(data=df_custodia.to_csv(), file_name="bitacora.csv")
```

### Vistas por rol

| Rol | Páginas disponibles | Acciones permitidas |
|---|---|---|
| **coordinacion_central** | Todas (01-06) | Todas las acciones |
| **sel** | mi_zore, mis_cael, incidencias_zore, paquetes_zore | Cerrar incidencias, escalar a coordinación |
| **cael** | Solo Telegram (no accede al dashboard web) | Reportar vía Telegram/Form |

---

## FLUJO COMPLETO DE EJEMPLO

> **Escenario**: CAEL reporta por Telegram que el presidente de casilla no llegó.

```
1. CAEL escribe en Telegram:
   "El presidente de la casilla 1205 no llegó, ya van 20 minutos"

2. Telegram Bot Trigger recibe el mensaje
   → Set node normaliza: {user_id, telegram_id, mensaje, timestamp, canal: "telegram"}

3. AI Agent (orquestador):
   → Postgres tool: SELECT rol='cael', are_id='are-03' WHERE telegram_id=:id
   → Clasifica: {"agent": "incidencias", "confidence": 92, "context": "falta funcionariado"}

4. Switch node → rama "incidencias"

5. AI Agent (incidencias) — autoevaluación:
   → puede_resolver: true (contexto claro, casilla_id disponible)
   → Postgres tool INSERT incidencias: tipo='falta_funcionariado', prioridad='alta'
   → Postgres tool UPDATE casillas: estatus='con_incidencia'
   → nivel_alerta: "alta"

6. IF node: nivel_alerta = "alta" → bifurca en paralelo:

   RAMA A — Postgres node:
   INSERT INTO alertas (nivel='alta', enviado_telegram=true, ...)

   RAMA B — Telegram node → canal maestro:
   🟡 ALERTA ALTA — IEEPCNLink
   Tipo: Falta de funcionariado
   Casilla: 1205 | ARE-03 | ZORE-01 | Monterrey
   CAEL: María López | Hora: 07:52
   Acción: Activar suplente o recorrer cargo

7. Telegram node → responde al CAEL:
   "Registrado con prioridad Alta. Activa al suplente.
    El SEL Luis Martínez ya fue notificado."

8. Postgres INSERT agent_logs:
   {session_id, agent_type='incidencias', pudo_resolver=true, nivel='warning'}

9. Streamlit dashboard (próximo ciclo de 30 seg):
   → Alerta aparece en tabla de alertas_activas con pill 🟡 ALTA
   → Casilla 1205 cambia color en mapa operativo a rojo
   → KPI "con_problema" sube de 2 a 3

10. Operador en dashboard:
    → Selecciona la incidencia
    → Acción: "Escalar → SEL ZORE-01"
    → UPDATE incidencias SET escalado_a = :sel_id
```

---

## INSTRUCCIONES DE CONSTRUCCIÓN

Construye el sistema en este orden:

### Fase 1 — Base de datos
1. Crea todas las tablas en el orden del script (respetar claves foráneas).
2. Inserta datos muestra: 2 ZORE, 6 ARE, 4 usuarios (1 coordinación, 2 SEL, 6 CAEL), 20 casillas con coordenadas ficticias de Nuevo León, 5 incidencias de ejemplo.
3. Verifica que las 5 queries maestras devuelven resultados coherentes.

### Fase 2 — N8N
1. Crea el bot de Telegram y obtén el token.
2. Configura el Telegram Bot Trigger como punto de entrada principal.
3. Construye el Set node de normalización.
4. Crea el AI Agent del orquestador con el system prompt exacto y el Postgres tool del perfil.
5. Configura el Switch node con las 7 ramas.
6. Construye cada agente especializado con sus herramientas nativas y el IF de autoevaluación.
7. Añade el doble registro (Postgres + Telegram) para alertas alta/crítica.
8. Configura el Schedule trigger para detección proactiva cada 15 min.

### Fase 3 — Dashboard Streamlit
1. Crea el archivo `db.py` con la función `run_query(nombre)` que carga archivos `.sql`.
2. Crea los 5 archivos `.sql` en la carpeta `queries/`.
3. Construye la página `01_estado_global.py` primero (usa Query 1 y 2).
4. Añade `02_mapa_operativo.py` con `st.pydeck_chart` (Query 3).
5. Construye `03_alertas.py` con las acciones del operador (Acciones 1, 4 y 5).
6. Construye `04_paquetes.py` con Query 4 y Acción 3.
7. Construye `05_disponibilidad.py` con Query 5 y Acción 2.
8. Añade `06_bitacora.py` con exportación CSV (Acción 6).

### Restricciones que debes respetar en todo momento
- Cero JavaScript en nodos de N8N.
- Las queries SQL van en archivos `.sql` separados, no en strings de Python.
- Cada alerta crítica o alta genera SIEMPRE dos registros: uno en `alertas` de Postgres y uno en Telegram.
- El rol del usuario se obtiene de la base de datos, nunca se infiere del mensaje.
- Streamlit no tiene lógica de negocio; solo lee, muestra y dispara UPDATEs.

---

## CRITERIOS DE ÉXITO (validación del prototipo)

- [ ] Un CAEL reporta por Telegram y la incidencia aparece en el dashboard en menos de 60 segundos.
- [ ] Una alerta "crítica" genera mensaje en el canal maestro de Telegram en menos de 5 segundos.
- [ ] El operador cambia la prioridad de una incidencia desde Streamlit y el cambio persiste en PostgreSQL.
- [ ] La query de cadena de custodia muestra el historial completo de un paquete desde integrado hasta recibido_cme.
- [ ] El Schedule trigger genera una alerta de "inactividad" para una casilla sin reporte en más de 45 minutos.
- [ ] La tabla de disponibilidad identifica correctamente qué CAEL tiene índice de carga bajo para reasignación.
- [ ] El agente de incidencias re-enruta correctamente cuando recibe un mensaje que pertenece al dominio de logística.

---

*IEEPCNLink — InnovaTecNM 2026 — HackaTec Etapa Local*
*IEEPCNL / Tecnológico Nacional de México*
