from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from config import COLORES_PRIORIDAD, NIVEL_BADGE


def render(alertas: pd.DataFrame) -> None:
    col_titulo_tab, col_filtro = st.columns([3, 2])
    with col_titulo_tab:
        st.subheader("Alertas activas")
    with col_filtro:
        filtro_prioridad = st.multiselect(
            "Filtrar por nivel",
            ["critica", "alta", "media", "baja"],
            format_func=lambda p: {
                "critica": "🔴 Crítica", "alta": "🟡 Alta",
                "media": "🟠 Media",    "baja": "🟢 Baja",
            }[p],
            label_visibility="collapsed",
        )

    alertas_tab = alertas[alertas["prioridad"].isin(filtro_prioridad)] if filtro_prioridad else alertas

    if alertas_tab.empty:
        st.success("No hay alertas activas en este momento.")
        return

    col_cards, col_pie = st.columns([3, 2], gap="large")

    with col_cards:
        for _, a in alertas_tab.iterrows():
            badge      = NIVEL_BADGE.get(a["prioridad"], "⚪")
            prioridad  = str(a["prioridad"]).upper()
            tipo       = str(a.get("tipo_alerta") or "alerta").replace("_", " ").title()
            seccion    = a.get("seccion")   or "—"
            municipio  = a.get("municipio") or "—"
            are        = a.get("are")       or "—"
            zore       = a.get("zore")      or "—"
            tiempo     = a["created_at"]
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

    with col_pie:
        st.subheader("Por tipo de alerta")
        conteo_tipo = alertas_tab["tipo_alerta"].value_counts().reset_index()
        conteo_tipo.columns = ["tipo", "total"]
        conteo_tipo["tipo"] = conteo_tipo["tipo"].str.replace("_", " ").str.title()
        fig_pie = px.pie(conteo_tipo, values="total", names="tipo", hole=0.4)
        fig_pie.update_traces(textposition="inside", textinfo="value+percent")
        fig_pie.update_layout(showlegend=True, margin=dict(t=10, b=10), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Por prioridad")
        conteo_prio = alertas_tab["prioridad"].value_counts().reset_index()
        conteo_prio.columns = ["prioridad", "total"]
        fig_prio = px.pie(
            conteo_prio,
            values="total",
            names="prioridad",
            color="prioridad",
            color_discrete_map=COLORES_PRIORIDAD,
            hole=0.4,
        )
        fig_prio.update_traces(textposition="inside", textinfo="value+percent")
        fig_prio.update_layout(showlegend=True, margin=dict(t=10, b=10), height=280)
        st.plotly_chart(fig_prio, use_container_width=True)

    st.divider()

    st.subheader("Detalle de alertas")
    cols_tabla = [
        c for c in ["prioridad", "tipo_alerta", "seccion", "municipio", "are", "zore", "created_at"]
        if c in alertas_tab.columns
    ]
    df_alertas_tabla = alertas_tab[cols_tabla].copy()
    df_alertas_tabla.columns = ["Prioridad", "Tipo", "Sección", "Municipio", "ARE", "ZORE", "Registrada"][:len(cols_tabla)]
    st.dataframe(df_alertas_tabla, use_container_width=True, hide_index=True)
