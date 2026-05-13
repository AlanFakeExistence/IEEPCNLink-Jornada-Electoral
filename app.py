"""
IEEPCNLink — Dashboard Operativo de Jornada Electoral
Instituto Estatal Electoral y de Participación Ciudadana de Nuevo León
"""
import streamlit as st
from datetime import datetime
from pathlib import Path

from db import run_query, is_demo
from config import ESTATUS_LABEL
from tabs import estado_global, sin_reporte, alertas, incidencias, custodia, disponibilidad

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="IEEPCNLink · Jornada Electoral",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Barra lateral ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🗳️ IEEPCNLink")
    st.caption("Sistema Operativo de Jornada Electoral")
    st.divider()

    if is_demo():
        st.warning(
            "**Modo demo** — datos de ejemplo\n"
            "Cambia `USE_MOCK_DATA = False` en `db.py` para conectar con PostgreSQL.",
            icon="⚠️",
        )

    st.divider()
    st.subheader("Filtros")

    df_casillas_sidebar    = run_query("casillas_mapa")
    municipios_disponibles = sorted(df_casillas_sidebar["municipio"].dropna().unique())
    zores_disponibles      = sorted(df_casillas_sidebar["zore"].dropna().unique())

    filtro_municipio = st.multiselect("Municipio", municipios_disponibles)
    filtro_zore      = st.multiselect("ZORE", zores_disponibles)

    st.divider()
    st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    if st.button("🔄 Refrescar datos"):
        st.cache_data.clear()
        st.rerun()

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def cargar_datos():
    return (
        run_query("pulso_general"),
        run_query("alertas_activas"),
        run_query("casillas_mapa"),
        run_query("cadena_custodia_timeline"),
        run_query("disponibilidad_operativa"),
        run_query("incidencias_activas"),
    )

pulso, alertas_df, df_casillas, custodia_df, disponib, incidencias_df = cargar_datos()

# Aplicar filtros globales
if filtro_municipio:
    df_casillas    = df_casillas[df_casillas["municipio"].isin(filtro_municipio)]
    alertas_df     = alertas_df[alertas_df["municipio"].isin(filtro_municipio)]
    incidencias_df = incidencias_df[incidencias_df["municipio"].isin(filtro_municipio)]
if filtro_zore:
    df_casillas    = df_casillas[df_casillas["zore"].isin(filtro_zore)]
    alertas_df     = alertas_df[alertas_df["zore"].isin(filtro_zore)]
    incidencias_df = incidencias_df[incidencias_df["zore"].isin(filtro_zore)]

# ── Encabezado ────────────────────────────────────────────────────────────────
col_titulo, col_estado = st.columns([6, 1])
with col_titulo:
    st.title("🗳️ IEEPCNLink — Jornada Electoral")
    st.caption("Instituto Estatal Electoral y de Participación Ciudadana de Nuevo León · Panel de Control Operativo")
with col_estado:
    if is_demo():
        st.markdown("<br><span style='color:#ffc107;font-weight:600;'>⚠ Demo</span>", unsafe_allow_html=True)
    else:
        st.markdown("<br><span style='color:#198754;font-weight:600;'>🟢 Online</span>", unsafe_allow_html=True)
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
row = pulso.iloc[0] if not pulso.empty else {}
c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
c1.metric("📋 Total",             int(row.get("total",             0)))
c2.metric("⏳ Pendientes",        int(row.get("pendientes",        0)))
c3.metric("🏛️ Instaladas",        int(row.get("instaladas",        0)))
c4.metric("🗳️ Votando",           int(row.get("votando",           0)))
c5.metric("🧮 En cómputo",        int(row.get("en_computo",        0)))
c6.metric("📦 Paquete integrado", int(row.get("paquete_integrado", 0)))
c7.metric("🚗 En traslado",       int(row.get("en_traslado",       0)))
c8.metric("✅ Recibidas CME",      int(row.get("recibidas_cme",     0)))
st.divider()

# ── Pestañas ──────────────────────────────────────────────────────────────────
casillas_silenciosas = df_casillas[df_casillas["minutos_sin_reporte"].astype(float) > 45]
silenciosas_label = (
    f"⏰ Sin reporte ({len(casillas_silenciosas)})"
    if not casillas_silenciosas.empty else "⏰ Sin reporte"
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Estado Global",
    silenciosas_label,
    "🚨 Alertas",
    "📋 Incidencias",
    "📦 Paquetes & Custodia",
    "👥 Disponibilidad",
])

with tab1:
    estado_global.render(df_casillas, pulso, alertas_df)

with tab2:
    sin_reporte.render(casillas_silenciosas)

with tab3:
    alertas.render(alertas_df)

with tab4:
    incidencias.render(incidencias_df)

with tab5:
    custodia.render(custodia_df)

with tab6:
    disponibilidad.render(disponib)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Instituto Estatal Electoral y de Participación Ciudadana de Nuevo León (IEEPCNL) · "
    "IEEPCNLink v1.0 · InnovaTecNM 2026"
)
