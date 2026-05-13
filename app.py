"""
IEEPCNLink — Dashboard Operativo de Jornada Electoral
Instituto Estatal Electoral y de Participación Ciudadana de Nuevo León
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path

from db import run_query, run_update, is_demo

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

# ── Colores por estatus y nivel ───────────────────────────────────────────────
ESTATUS_COLOR = {
    "pendiente":         "#6c757d",
    "instalada":         "#0d6efd",
    "en_votacion":       "#198754",
    "cerrada":           "#6f42c1",
    "en_computo":        "#fd7e14",
    "paquete_integrado": "#20c997",
    "en_traslado":       "#0dcaf0",
    "recibida_cme":      "#198754",
}

NIVEL_BADGE = {
    "critica": "🔴",
    "alta":    "🟡",
    "media":   "🟠",
    "baja":    "🟢",
}

ESTATUS_LABEL = {
    "pendiente":         "Pendiente",
    "instalada":         "Instalada",
    "en_votacion":       "En votación",
    "cerrada":           "Cerrada",
    "en_computo":        "En cómputo",
    "paquete_integrado": "Paquete integrado",
    "en_traslado":       "En traslado",
    "recibida_cme":      "Recibida CME",
}

# ── Barra lateral ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🗳️ IEEPCNLink")
    st.caption("Sistema Operativo de Jornada Electoral")
    st.divider()

    if is_demo():
        st.warning("**Modo demo** — datos de ejemplo\nCambia `USE_MOCK_DATA = False` en `db.py` para conectar con PostgreSQL.", icon="⚠️")

    st.divider()

    # Filtros globales
    st.subheader("Filtros")
    df_casillas_sidebar = run_query("casillas_mapa")
    municipios_disponibles = sorted(df_casillas_sidebar["municipio"].unique())
    zores_disponibles      = sorted(df_casillas_sidebar["zore"].unique())

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
    pulso        = run_query("pulso_general")
    alertas      = run_query("alertas_activas")
    casillas     = run_query("casillas_mapa")
    custodia     = run_query("cadena_custodia_timeline")
    disponib     = run_query("disponibilidad_operativa")
    return pulso, alertas, casillas, custodia, disponib

pulso, alertas, df_casillas, custodia, disponib = cargar_datos()

# Aplicar filtros de sidebar
if filtro_municipio:
    df_casillas = df_casillas[df_casillas["municipio"].isin(filtro_municipio)]
if filtro_zore:
    df_casillas = df_casillas[df_casillas["zore"].isin(filtro_zore)]

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

# ── KPIs (pulso_general) ──────────────────────────────────────────────────────
row = pulso.iloc[0] if not pulso.empty else {}

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
c1.metric("📋 Total",             int(row.get("total",              0)))
c2.metric("⏳ Pendientes",        int(row.get("pendientes",         0)))
c3.metric("🏛️ Instaladas",        int(row.get("instaladas",         0)))
c4.metric("🗳️ Votando",           int(row.get("votando",            0)))
c5.metric("🧮 En cómputo",        int(row.get("en_computo",         0)))
c6.metric("📦 Paquete integrado", int(row.get("paquete_integrado",  0)))
c7.metric("🚗 En traslado",       int(row.get("en_traslado",        0)))
c8.metric("✅ Recibidas CME",      int(row.get("recibidas_cme",      0)))

st.divider()

# ── Pestañas principales ──────────────────────────────────────────────────────
casillas_silenciosas = df_casillas[df_casillas["minutos_sin_reporte"].astype(float) > 45]
silenciosas_label = f"⏰ Sin reporte ({len(casillas_silenciosas)})" if not casillas_silenciosas.empty else "⏰ Sin reporte"

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Estado Global",
    silenciosas_label,
    "🚨 Alertas & Incidencias",
    "📦 Paquetes & Custodia",
    "👥 Disponibilidad",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ESTADO GLOBAL
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_izq, col_der = st.columns([2, 1], gap="large")

    with col_izq:
        st.subheader("Casillas por estatus")

        # Tabla de casillas
        df_display = df_casillas[[
            "seccion", "clave", "municipio", "are", "zore",
            "estatus", "cael_responsable", "minutos_sin_reporte"
        ]].copy()
        df_display["estatus"] = df_display["estatus"].map(
            lambda s: ESTATUS_LABEL.get(s, s)
        )
        df_display["minutos_sin_reporte"] = df_display["minutos_sin_reporte"].apply(
            lambda m: f"{int(m)} min"
        )
        df_display.columns = [
            "Sección", "Clave", "Municipio", "ARE", "ZORE",
            "Estatus", "CAEL", "Sin reporte"
        ]

        st.dataframe(df_display, use_container_width=True, hide_index=True, height=420)

    with col_der:
        st.subheader("Distribución de estatus")

        pulso_row = pulso.iloc[0] if not pulso.empty else {}
        conteo = pd.DataFrame([
            {"estatus": k, "total": int(pulso_row.get(v, 0))}
            for k, v in {
                "pendiente":         "pendientes",
                "instalada":         "instaladas",
                "en_votacion":       "votando",
                "en_computo":        "en_computo",
                "paquete_integrado": "paquete_integrado",
                "en_traslado":       "en_traslado",
                "recibida_cme":      "recibidas_cme",
            }.items()
            if int(pulso_row.get(v, 0)) > 0
        ])
        conteo["etiqueta"] = conteo["estatus"].map(lambda s: ESTATUS_LABEL.get(s, s))
        conteo["color"]    = conteo["estatus"].map(lambda s: ESTATUS_COLOR.get(s, "#adb5bd"))

        fig = px.pie(
            conteo,
            values="total",
            names="etiqueta",
            color="etiqueta",
            color_discrete_map={row["etiqueta"]: row["color"] for _, row in conteo.iterrows()},
            hole=0.45,
        )
        fig.update_traces(textposition="inside", textinfo="value+percent")
        fig.update_layout(showlegend=True, margin=dict(t=10, b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)

        # Mini tabla de alertas recientes
        st.subheader("Últimas alertas")
        if alertas.empty:
            st.info("Sin alertas activas")
        else:
            for _, a in alertas.head(4).iterrows():
                badge     = NIVEL_BADGE.get(a["prioridad"], "⚪")
                tipo      = str(a.get("tipo_alerta") or "alerta").replace("_", " ").title()
                seccion   = a.get("seccion")   or "—"
                municipio = a.get("municipio") or "—"
                st.markdown(f"{badge} **{tipo}** — Casilla {seccion} · {municipio}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CASILLAS SIN REPORTE
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Casillas sin reporte hace más de 45 minutos")

    if casillas_silenciosas.empty:
        st.success("Todas las casillas han reportado en los últimos 45 minutos.")
    else:
        st.warning(f"**{len(casillas_silenciosas)} casilla(s)** sin actividad.", icon="⏰")

        df_silenciosas = casillas_silenciosas[[
            "seccion", "clave", "municipio", "are", "zore",
            "estatus", "cael_responsable", "minutos_sin_reporte", "ultima_actualizacion"
        ]].copy()
        df_silenciosas["estatus"] = df_silenciosas["estatus"].map(lambda s: ESTATUS_LABEL.get(s, s))
        df_silenciosas = df_silenciosas.sort_values("minutos_sin_reporte", ascending=False).reset_index(drop=True)
        df_silenciosas["minutos_sin_reporte"] = df_silenciosas["minutos_sin_reporte"].apply(lambda m: f"{int(m)} min")
        df_silenciosas.columns = [
            "Sección", "Clave", "Municipio", "ARE", "ZORE",
            "Estatus", "CAEL", "Sin reporte", "Último reporte"
        ]

        FILAS_POR_PAGINA = 50
        total_paginas = max(1, -(-len(df_silenciosas) // FILAS_POR_PAGINA))

        if "pagina_silenciosas" not in st.session_state:
            st.session_state.pagina_silenciosas = 1

        pagina_actual = st.session_state.pagina_silenciosas

        # Ventana deslizante de 9 botones (estilo Google)
        VENTANA = 9
        if total_paginas <= VENTANA:
            p_inicio, p_fin = 1, total_paginas
        else:
            p_inicio = max(1, pagina_actual - VENTANA // 2)
            p_fin    = min(total_paginas, p_inicio + VENTANA - 1)
            if p_fin - p_inicio < VENTANA - 1:
                p_inicio = max(1, p_fin - VENTANA + 1)
        paginas_visibles = list(range(p_inicio, p_fin + 1))

        # Columnas: < | 9 botones | > | CSV
        cols_nav = st.columns([1] + [1] * len(paginas_visibles) + [1, 1])

        if cols_nav[0].button("‹", use_container_width=True, disabled=pagina_actual == 1):
            st.session_state.pagina_silenciosas = pagina_actual - 1
            st.rerun()

        for i, p in enumerate(paginas_visibles):
            etiqueta = f"**{p}**" if p == pagina_actual else str(p)
            if cols_nav[i + 1].button(etiqueta, key=f"pag_{p}", use_container_width=True):
                st.session_state.pagina_silenciosas = p
                st.rerun()

        if cols_nav[len(paginas_visibles) + 1].button("›", use_container_width=True, disabled=pagina_actual == total_paginas):
            st.session_state.pagina_silenciosas = pagina_actual + 1
            st.rerun()

        cols_nav[len(paginas_visibles) + 2].download_button(
            "⬇️ CSV",
            data=casillas_silenciosas.to_csv(index=False).encode("utf-8"),
            file_name=f"casillas_sin_reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        pagina = st.session_state.pagina_silenciosas
        inicio = (pagina - 1) * FILAS_POR_PAGINA
        fin    = inicio + FILAS_POR_PAGINA
        st.dataframe(df_silenciosas.iloc[inicio:fin], use_container_width=True, hide_index=True)
        st.caption(f"Página {pagina} de {total_paginas} · Mostrando {inicio + 1}–{min(fin, len(df_silenciosas))} de {len(df_silenciosas)} casillas")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ALERTAS & INCIDENCIAS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Alertas activas")

    if alertas.empty:
        st.success("No hay alertas activas en este momento.")
    else:
        # Tarjetas de alerta
        for _, a in alertas.iterrows():
            badge     = NIVEL_BADGE.get(a["prioridad"], "⚪")
            prioridad = str(a["prioridad"]).upper()
            tipo      = str(a.get("tipo_alerta") or "alerta").replace("_", " ").title()
            seccion   = a.get("seccion")   or "—"
            municipio = a.get("municipio") or "—"
            are       = a.get("are")       or "—"
            zore      = a.get("zore")      or "—"
            tiempo    = a["created_at"]
            tiempo_str = tiempo.strftime("%H:%M") if isinstance(tiempo, (datetime, pd.Timestamp)) else str(tiempo)

            with st.container(border=True):
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(
                        f"{badge} **{prioridad}** · {tipo} "
                        f"— Casilla **{seccion}** | {municipio} | {are} | {zore}"
                    )
                    st.caption(a["mensaje"])
                with col_b:
                    st.caption(f"🕐 {tiempo_str}")

        st.divider()

        # Tabla completa
        st.subheader("Detalle de alertas")
        cols_tabla = [c for c in ["prioridad", "tipo_alerta", "seccion", "municipio", "are", "zore", "created_at"] if c in alertas.columns]
        df_alertas_tabla = alertas[cols_tabla].copy()
        df_alertas_tabla.columns = ["Prioridad", "Tipo", "Sección", "Municipio", "ARE", "ZORE", "Registrada"][:len(cols_tabla)]
        st.dataframe(df_alertas_tabla, use_container_width=True, hide_index=True)

    st.divider()

    # ── Acciones del operador ──────────────────────────────────────────────
    st.subheader("Acciones del operador")
    st.caption("Requiere conexión a PostgreSQL para persistir cambios.")

    with st.expander("Cerrar incidencia"):
        inc_id = st.text_input("ID de incidencia", placeholder="uuid de la incidencia")
        if st.button("Cerrar incidencia", type="primary"):
            if inc_id:
                run_update(
                    "UPDATE incidencias SET estatus = 'cerrada', hora_cierre = NOW() WHERE id = :id",
                    {"id": inc_id},
                )
                st.success(f"Incidencia {inc_id} cerrada.")
                st.cache_data.clear()
            else:
                st.warning("Ingresa el ID de la incidencia.")

    with st.expander("Marcar casilla silenciosa como incidencia"):
        casilla_id = st.text_input("ID de casilla", placeholder="uuid de la casilla")
        if st.button("Registrar inactividad", type="secondary"):
            if casilla_id:
                run_update(
                    """
                    INSERT INTO incidencias (casilla_id, tipo, prioridad, descripcion, hora_reporte)
                    VALUES (:cid, 'inactividad', 'alta', 'Sin reporte desde dashboard operativo', NOW())
                    """,
                    {"cid": casilla_id},
                )
                st.success("Incidencia de inactividad registrada.")
                st.cache_data.clear()
            else:
                st.warning("Ingresa el ID de la casilla.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PAQUETES & CADENA DE CUSTODIA
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Paquetes electorales en tránsito")

    if custodia.empty:
        st.info("No hay paquetes activos en tránsito.")
    else:
        # Resumen por paquete (último evento)
        ultimo_evento = (
            custodia.sort_values("hora_evento")
                    .groupby("paquete_id")
                    .last()
                    .reset_index()
        )

        for _, p in ultimo_evento.iterrows():
            mecanismo = str(p.get("mecanismo","")).replace("_", " ").title()
            estatus   = str(p.get("estatus","")).replace("_", " ").title()
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.markdown(f"📦 **Casilla {p['seccion']}** — {p['municipio']}")
                c1.caption(f"Vía: {mecanismo}")
                c2.markdown(f"Último evento: **{str(p['evento']).replace('_',' ').title()}**")
                c2.caption(f"📍 {p['ubicacion']}  ·  {p['responsable']}")
                c3.markdown(f"**{estatus}**")

        st.divider()

        # Timeline completa
        st.subheader("Línea de tiempo — cadena de custodia")
        df_timeline = custodia[[
            "seccion", "municipio", "mecanismo",
            "evento", "ubicacion", "hora_evento", "responsable", "estatus"
        ]].copy()
        df_timeline["evento"]    = df_timeline["evento"].str.replace("_", " ").str.title()
        df_timeline["mecanismo"] = df_timeline["mecanismo"].str.replace("_", " ").str.title()
        df_timeline["estatus"]   = df_timeline["estatus"].str.replace("_", " ").str.title()
        df_timeline.columns = [
            "Sección", "Municipio", "Mecanismo",
            "Evento", "Ubicación", "Hora", "Responsable", "Estatus"
        ]
        st.dataframe(df_timeline, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Exportar bitácora CSV",
            data=custodia.to_csv(index=False).encode("utf-8"),
            file_name=f"bitacora_custodia_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DISPONIBILIDAD CAEL / SEL
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Índice de carga CAEL / SEL")

    if disponib.empty:
        st.info("Sin datos de disponibilidad.")
    else:
        # Gráfica de carga
        fig_carga = px.bar(
            disponib.sort_values("indice_carga", ascending=False),
            x="nombre",
            y="indice_carga",
            color="rol",
            color_discrete_map={"cael": "#0d6efd", "sel": "#6f42c1"},
            labels={"nombre": "Personal", "indice_carga": "Índice de carga", "rol": "Rol"},
            title="Incidencias abiertas / casillas asignadas",
        )
        fig_carga.add_hline(y=0.3, line_dash="dot", line_color="orange",
                            annotation_text="Umbral de atención (0.30)")
        fig_carga.update_layout(margin=dict(t=40, b=20), height=300)
        st.plotly_chart(fig_carga, use_container_width=True)

        # Tabla de disponibilidad
        df_disp = disponib[[
            "nombre", "rol", "are", "zore", "disponible",
            "total_casillas", "completadas", "incidencias_abiertas", "indice_carga"
        ]].copy()
        df_disp["disponible"] = df_disp["disponible"].map({True: "✅ Disponible", False: "⛔ No disponible"})
        df_disp.columns = [
            "Nombre", "Rol", "ARE", "ZORE", "Disponibilidad",
            "Casillas", "Completadas", "Incid. abiertas", "Índice carga"
        ]
        st.dataframe(df_disp, use_container_width=True, hide_index=True)

        st.divider()

        # Acción: reasignar CAEL
        st.subheader("Reasignar CAEL a ARE saturada")
        st.caption("Requiere conexión a PostgreSQL para persistir cambios.")
        with st.expander("Reasignación"):
            cael_id  = st.text_input("ID del CAEL", placeholder="uuid del usuario")
            nueva_are = st.text_input("ID de nueva ARE", placeholder="uuid del are")
            if st.button("Reasignar", type="primary"):
                if cael_id and nueva_are:
                    run_update(
                        "UPDATE usuarios SET are_id = :are, disponible = false WHERE id = :id",
                        {"are": nueva_are, "id": cael_id},
                    )
                    st.success("CAEL reasignado correctamente.")
                    st.cache_data.clear()
                else:
                    st.warning("Completa ambos campos.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Instituto Estatal Electoral y de Participación Ciudadana de Nuevo León (IEEPCNL) · "
    "IEEPCNLink v1.0 · InnovaTecNM 2026 · Uso exclusivo institucional"
)
