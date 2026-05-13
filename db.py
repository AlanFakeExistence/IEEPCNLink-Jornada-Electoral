"""
IEEPCNLink — Capa de datos
Cambia USE_MOCK_DATA = False y define DATABASE_URL para conectar con PostgreSQL real.
"""
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ── Configuración ────────────────────────────────────────────────────────────
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
DATABASE_URL  = os.getenv("DATABASE_URL", "")

QUERIES_DIR = Path(__file__).parent / "queries"

# ── Motor SQLAlchemy (se crea solo cuando se necesita) ───────────────────────
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy import create_engine
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine


# ── API pública ───────────────────────────────────────────────────────────────

def run_query(nombre: str, params: dict = None) -> pd.DataFrame:
    """
    Ejecuta queries/<nombre>.sql contra PostgreSQL.
    En modo demo devuelve datos de ejemplo con el mismo esquema de columnas.
    """
    if USE_MOCK_DATA:
        return _mock(nombre)

    sql_file = QUERIES_DIR / f"{nombre}.sql"
    if not sql_file.exists():
        raise FileNotFoundError(f"Query no encontrada: {sql_file}")

    from sqlalchemy import text
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql_file.read_text(encoding="utf-8")), conn, params=params or {})


def run_update(sql: str, params: dict = None) -> None:
    """
    Ejecuta un UPDATE / INSERT directo.
    En modo demo es un no-op (no modifica nada).
    """
    if USE_MOCK_DATA:
        return
    from sqlalchemy import text
    with get_engine().begin() as conn:
        conn.execute(text(sql), params or {})


def is_demo() -> bool:
    return USE_MOCK_DATA


# ── Datos de ejemplo (espejo exacto del esquema PostgreSQL) ───────────────────

def _mock(nombre: str) -> pd.DataFrame:
    random.seed(42)
    now = datetime.now()

    if nombre == "pulso_general":
        return pd.DataFrame([{
            "instaladas":   14,
            "votando":       8,
            "listas":        5,
            "en_ruta":       3,
            "entregadas":    2,
            "con_problema":  4,
        }])

    if nombre == "alertas_activas":
        return pd.DataFrame([
            {
                "id": "a1", "nivel": "critica", "tipo_alerta": "riesgo_seguridad",
                "mensaje": "Confrontación reportada cerca de casilla 0312. Requiere intervención inmediata.",
                "created_at": now - timedelta(minutes=5),
                "tipo_incidencia": "riesgo_seguridad", "prioridad": "critica",
                "seccion": "0312", "municipio": "Monterrey", "are": "ARE-02", "zore": "ZORE-01",
            },
            {
                "id": "a2", "nivel": "alta", "tipo_alerta": "falta_funcionariado",
                "mensaje": "Presidente de casilla 1205 no llegó. 25 min de retraso.",
                "created_at": now - timedelta(minutes=18),
                "tipo_incidencia": "falta_funcionariado", "prioridad": "alta",
                "seccion": "1205", "municipio": "San Nicolás", "are": "ARE-03", "zore": "ZORE-01",
            },
            {
                "id": "a3", "nivel": "alta", "tipo_alerta": "problema_traslado",
                "mensaje": "Paquete electoral sin actualización hace 35 min. Casilla 0874.",
                "created_at": now - timedelta(minutes=35),
                "tipo_incidencia": "problema_traslado", "prioridad": "alta",
                "seccion": "0874", "municipio": "Guadalupe", "are": "ARE-05", "zore": "ZORE-02",
            },
            {
                "id": "a4", "nivel": "media", "tipo_alerta": "error_acta",
                "mensaje": "Duda en llenado de acta de instalación. CAEL solicita apoyo.",
                "created_at": now - timedelta(minutes=52),
                "tipo_incidencia": "error_acta", "prioridad": "media",
                "seccion": "0521", "municipio": "Apodaca", "are": "ARE-04", "zore": "ZORE-02",
            },
            {
                "id": "a5", "nivel": "baja", "tipo_alerta": "paquete_con_observacion",
                "mensaje": "Sobre de boletas sobrantes con sello incompleto. Controlado.",
                "created_at": now - timedelta(minutes=70),
                "tipo_incidencia": "paquete_con_observacion", "prioridad": "baja",
                "seccion": "0145", "municipio": "Santa Catarina", "are": "ARE-01", "zore": "ZORE-01",
            },
        ])

    if nombre == "casillas_mapa":
        secciones = ["0101","0312","0521","0874","1205","1380","1402","1518",
                     "0203","0445","0667","0789","0923","1100","1247","1356",
                     "0060","0188","0299","0412"]
        municipios = ["Monterrey","Monterrey","Apodaca","Guadalupe","San Nicolás",
                      "García","Escobedo","Juárez","Monterrey","Santa Catarina",
                      "Guadalupe","San Nicolás","Apodaca","García","Escobedo",
                      "Juárez","Santa Catarina","Monterrey","Guadalupe","San Nicolás"]
        estatuses = [
            "instalada","con_incidencia","instalada","en_traslado","con_incidencia",
            "votando","votando","paquete_integrado","instalada","votando",
            "cerrada","paquete_integrado","instalada","en_traslado","votando",
            "proceso_completo","proceso_completo","instalada","votando","cerrada",
        ]
        ares = [f"ARE-0{(i % 6)+1}" for i in range(20)]
        zores = [f"ZORE-0{(i // 10)+1}" for i in range(20)]
        caels = [f"CAEL-{chr(65+i)}" for i in range(20)]
        lats  = [25.67 + random.uniform(-0.15, 0.15) for _ in range(20)]
        lngs  = [-100.31 + random.uniform(-0.15, 0.15) for _ in range(20)]
        mins  = [random.randint(2, 80) for _ in range(20)]
        rows = []
        for i in range(20):
            rows.append({
                "id": f"c{i}", "seccion": secciones[i], "municipio": municipios[i],
                "tipo": random.choice(["basica","contigua","extraordinaria"]),
                "estatus_operativo": estatuses[i],
                "lat": lats[i], "lng": lngs[i],
                "ultima_actualizacion": now - timedelta(minutes=mins[i]),
                "are": ares[i], "zore": zores[i],
                "cael_responsable": caels[i],
                "minutos_sin_reporte": mins[i],
            })
        return pd.DataFrame(rows)

    if nombre == "cadena_custodia_timeline":
        return pd.DataFrame([
            {
                "paquete_id": "p1", "seccion": "1380", "municipio": "García",
                "mecanismo": "cryt_fijo", "estatus": "en_cryt",
                "hora_integracion": now - timedelta(hours=2),
                "hora_salida_casilla": now - timedelta(hours=1, minutes=30),
                "hora_recepcion_cme": None,
                "evento": "sale_casilla", "ubicacion": "Casilla 1380", "hora_evento": now - timedelta(hours=1, minutes=30),
                "responsable": "CAEL-F",
            },
            {
                "paquete_id": "p1", "seccion": "1380", "municipio": "García",
                "mecanismo": "cryt_fijo", "estatus": "en_cryt",
                "hora_integracion": now - timedelta(hours=2),
                "hora_salida_casilla": now - timedelta(hours=1, minutes=30),
                "hora_recepcion_cme": None,
                "evento": "llega_cryt", "ubicacion": "CRyT García Centro", "hora_evento": now - timedelta(hours=1),
                "responsable": "CAEL-F",
            },
            {
                "paquete_id": "p2", "seccion": "0874", "municipio": "Guadalupe",
                "mecanismo": "dat", "estatus": "en_traslado",
                "hora_integracion": now - timedelta(hours=1, minutes=10),
                "hora_salida_casilla": now - timedelta(minutes=35),
                "hora_recepcion_cme": None,
                "evento": "sale_casilla", "ubicacion": "Casilla 0874", "hora_evento": now - timedelta(minutes=35),
                "responsable": "DAT-02",
            },
            {
                "paquete_id": "p3", "seccion": "1247", "municipio": "Escobedo",
                "mecanismo": "cryt_itinerante", "estatus": "recibido_cme",
                "hora_integracion": now - timedelta(hours=3),
                "hora_salida_casilla": now - timedelta(hours=2, minutes=40),
                "hora_recepcion_cme": now - timedelta(hours=1, minutes=15),
                "evento": "llega_cme", "ubicacion": "CME Escobedo", "hora_evento": now - timedelta(hours=1, minutes=15),
                "responsable": "SEL-02",
            },
        ])

    if nombre == "disponibilidad_operativa":
        return pd.DataFrame([
            {"id":"u1","nombre":"María López",   "rol":"cael","disponible":True,  "are":"ARE-03","zore":"ZORE-01","total_casillas":5,"completadas":1,"incidencias_abiertas":2,"indice_carga":0.40},
            {"id":"u2","nombre":"Carlos Reyes",  "rol":"cael","disponible":True,  "are":"ARE-05","zore":"ZORE-02","total_casillas":4,"completadas":0,"incidencias_abiertas":2,"indice_carga":0.50},
            {"id":"u3","nombre":"Ana González",  "rol":"sel", "disponible":True,  "are":"ARE-01","zore":"ZORE-01","total_casillas":6,"completadas":3,"incidencias_abiertas":1,"indice_carga":0.17},
            {"id":"u4","nombre":"Luis Martínez", "rol":"sel", "disponible":True,  "are":"ARE-02","zore":"ZORE-01","total_casillas":5,"completadas":2,"incidencias_abiertas":0,"indice_carga":0.00},
            {"id":"u5","nombre":"Rosa Herrera",  "rol":"cael","disponible":False, "are":"ARE-04","zore":"ZORE-02","total_casillas":4,"completadas":2,"incidencias_abiertas":1,"indice_carga":0.25},
            {"id":"u6","nombre":"Pedro Sánchez", "rol":"cael","disponible":True,  "are":"ARE-06","zore":"ZORE-02","total_casillas":5,"completadas":4,"incidencias_abiertas":0,"indice_carga":0.00},
        ])

    if nombre == "incidencias_activas":
        return pd.DataFrame([
            {
                "id": "i1", "tipo": "robo_material", "prioridad": "critica",
                "descripcion": "Personas armadas llegaron a la casilla y se llevaron el paquete electoral.",
                "estatus": "abierta", "hora_reporte": now - timedelta(minutes=10), "hora_cierre": None,
                "seccion": "0312", "clave": "0312 B", "municipio": "Monterrey",
                "are": "ARE-02", "zore": "ZORE-01", "reportado_por": "María López",
            },
            {
                "id": "i2", "tipo": "falta_funcionariado", "prioridad": "alta",
                "descripcion": "Presidente de casilla no llegó, 25 minutos de retraso.",
                "estatus": "abierta", "hora_reporte": now - timedelta(minutes=28), "hora_cierre": None,
                "seccion": "1205", "clave": "1205 C1", "municipio": "San Nicolás",
                "are": "ARE-03", "zore": "ZORE-01", "reportado_por": "Carlos Reyes",
            },
            {
                "id": "i3", "tipo": "error_actas", "prioridad": "media",
                "descripcion": "Duda en llenado de acta de instalación, CAEL solicita apoyo.",
                "estatus": "en_atencion", "hora_reporte": now - timedelta(minutes=55), "hora_cierre": None,
                "seccion": "0521", "clave": "0521 A", "municipio": "Apodaca",
                "are": "ARE-04", "zore": "ZORE-02", "reportado_por": "Rosa Herrera",
            },
        ])

    return pd.DataFrame()
