from datetime import datetime

import pandas as pd
import streamlit as st

from config import NIVEL_BADGE
from db import run_update


def render(incidencias: pd.DataFrame) -> None:
    col_titulo_inc, col_filtro_inc, col_filtro_estatus = st.columns([3, 2, 2])
    with col_titulo_inc:
        st.subheader("Incidencias registradas")
    with col_filtro_inc:
        filtro_prioridad_inc = st.multiselect(
            "Filtrar por nivel",
            ["critica", "alta", "media", "baja"],
            format_func=lambda p: {
                "critica": "🔴 Crítica", "alta": "🟡 Alta",
                "media": "🟠 Media",    "baja": "🟢 Baja",
            }[p],
            label_visibility="collapsed",
            key="filtro_prioridad_inc",
        )
    with col_filtro_estatus:
        filtro_estatus_inc = st.multiselect(
            "Filtrar por estatus",
            ["abierta", "en_atencion", "cerrada"],
            format_func=lambda s: {
                "abierta": "🟢 Abierta", "en_atencion": "🟡 En atención", "cerrada": "⚫ Cerrada",
            }[s],
            label_visibility="collapsed",
            key="filtro_estatus_inc",
        )

    inc_filtradas = incidencias.copy()
    if filtro_prioridad_inc:
        inc_filtradas = inc_filtradas[inc_filtradas["prioridad"].isin(filtro_prioridad_inc)]
    if filtro_estatus_inc:
        inc_filtradas = inc_filtradas[inc_filtradas["estatus"].isin(filtro_estatus_inc)]

    if inc_filtradas.empty:
        st.info("No hay incidencias registradas.")
    else:
        for _, i in inc_filtradas.iterrows():
            badge     = NIVEL_BADGE.get(i["prioridad"], "⚪")
            prioridad = str(i["prioridad"]).upper()
            tipo      = str(i.get("tipo")    or "—").replace("_", " ").title()
            estatus   = str(i.get("estatus") or "—").replace("_", " ").title()
            hora      = i["hora_reporte"]
            hora_str  = hora.strftime("%H:%M") if isinstance(hora, (datetime, pd.Timestamp)) else str(hora)

            with st.container(border=True):
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(
                        f"{badge} **{prioridad}** · {tipo} "
                        f"— Casilla **{i.get('seccion','—')}** | {i.get('municipio','—')} "
                        f"| {i.get('are','—')} | {i.get('zore','—')}"
                    )
                    st.caption(f"{i.get('descripcion','—')}  ·  Reportado por: {i.get('reportado_por','—')}")
                with col_b:
                    st.caption(f"🕐 {hora_str}")
                    st.caption(f"_{estatus}_")

    st.divider()
    st.subheader("Acciones")
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
