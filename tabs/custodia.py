from datetime import datetime

import pandas as pd
import streamlit as st


def render(custodia: pd.DataFrame) -> None:
    col_titulo_cust, col_busqueda_cust = st.columns([3, 3])
    with col_titulo_cust:
        st.subheader("Paquetes electorales en tránsito")
    with col_busqueda_cust:
        busqueda_cust = st.text_input(
            "Buscar paquete",
            placeholder="Clave, sección, municipio…",
            label_visibility="collapsed",
            key="busqueda_cust",
        )

    custodia_filtrada = custodia.copy()
    if busqueda_cust:
        term = busqueda_cust.lower()
        mask = (
            custodia_filtrada["clave"].fillna("").str.lower().str.contains(term, regex=False) |
            custodia_filtrada["seccion"].fillna("").astype(str).str.lower().str.contains(term, regex=False) |
            custodia_filtrada["municipio"].fillna("").str.lower().str.contains(term, regex=False)
        )
        custodia_filtrada = custodia_filtrada[mask]

    if custodia_filtrada.empty:
        st.info("No hay paquetes activos en tránsito." if custodia.empty else "Sin resultados para la búsqueda.")
        return

    # Resumen por paquete (último evento con hora registrada)
    ultimo_evento = (
        custodia_filtrada.dropna(subset=["hora_evento"])
                .sort_values("hora_evento")
                .groupby("paquete_id")
                .last()
                .reset_index()
    )

    if ultimo_evento.empty:
        st.info("Sin eventos de custodia registrados para los paquetes en tránsito.")
    else:
        for _, p in ultimo_evento.iterrows():
            mecanismo = str(p.get("mecanismo") or "—").replace("_", " ").title()
            estatus   = str(p.get("estatus")   or "—").replace("_", " ").title()
            clave     = str(p.get("clave")      or p.get("seccion") or "—")
            municipio = str(p.get("municipio")  or "—")
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                c1.markdown(f"📦 **{clave}** — {municipio}")
                c1.caption(f"Vía: {mecanismo}")
                c2.markdown(f"Último evento: **{str(p.get('evento','—')).replace('_',' ').title()}**")
                c2.caption(f"📍 {p.get('ubicacion','—')}  ·  {p.get('responsable','—')}")
                c3.markdown(f"**{estatus}**")

    st.divider()

    st.subheader("Línea de tiempo — cadena de custodia")
    df_timeline = custodia_filtrada[[
        "seccion", "municipio", "mecanismo",
        "evento", "ubicacion", "hora_evento", "responsable", "estatus"
    ]].copy()
    df_timeline["evento"]    = df_timeline["evento"].str.replace("_", " ").str.title()
    df_timeline["mecanismo"] = df_timeline["mecanismo"].str.replace("_", " ").str.title()
    df_timeline["estatus"]   = df_timeline["estatus"].str.replace("_", " ").str.title()
    df_timeline.columns = [
        "Sección", "Municipio", "Mecanismo",
        "Evento", "Ubicación", "Hora", "Responsable", "Estatus",
    ]
    st.dataframe(df_timeline, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Exportar bitácora CSV",
        data=custodia_filtrada.to_csv(index=False).encode("utf-8"),
        file_name=f"bitacora_custodia_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )
