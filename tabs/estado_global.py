import streamlit as st
import pandas as pd
import plotly.express as px

from config import ESTATUS_COLOR, ESTATUS_LABEL, NIVEL_BADGE


def render(df_casillas: pd.DataFrame, pulso: pd.DataFrame, alertas: pd.DataFrame) -> None:
    col_izq, col_der = st.columns([2, 1], gap="large")

    with col_izq:
        st.subheader("Casillas por estatus")

        busqueda = st.text_input(
            "🔍 Buscar casilla",
            placeholder="Sección, clave, municipio, ARE, CAEL…",
            label_visibility="collapsed",
        )

        df_display = df_casillas[[
            "seccion", "clave", "municipio", "are", "zore",
            "estatus", "cael_responsable", "minutos_sin_reporte"
        ]].copy()
        df_display["estatus"] = df_display["estatus"].map(lambda s: ESTATUS_LABEL.get(s, s))
        df_display["minutos_sin_reporte"] = df_display["minutos_sin_reporte"].apply(
            lambda m: f"{int(m)} min"
        )
        df_display.columns = [
            "Sección", "Clave", "Municipio", "ARE", "ZORE",
            "Estatus", "CAEL", "Sin reporte",
        ]

        if busqueda:
            mask = df_display.apply(
                lambda r: busqueda.lower() in " ".join(r.fillna("").astype(str).str.lower()), axis=1
            )
            df_display = df_display[mask]

        altura = min(38 + len(df_display) * 35, 600) if busqueda else 420
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=altura)

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
            color_discrete_map={r["etiqueta"]: r["color"] for _, r in conteo.iterrows()},
            hole=0.45,
        )
        fig.update_traces(textposition="inside", textinfo="value+percent")
        fig.update_layout(showlegend=True, margin=dict(t=10, b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)

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
