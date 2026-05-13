import pandas as pd
import plotly.express as px
import streamlit as st

from db import run_update


def render(disponib: pd.DataFrame) -> None:
    st.subheader("Índice de carga CAEL / SEL")

    if disponib.empty:
        st.info("Sin datos de disponibilidad.")
        return

    fig_carga = px.bar(
        disponib.sort_values("indice_carga", ascending=False),
        x="nombre",
        y="indice_carga",
        color="rol",
        color_discrete_map={"cael": "#0d6efd", "sel": "#6f42c1"},
        labels={"nombre": "Personal", "indice_carga": "Índice de carga", "rol": "Rol"},
        title="Incidencias abiertas / casillas asignadas",
    )
    fig_carga.add_hline(
        y=0.3, line_dash="dot", line_color="orange",
        annotation_text="Umbral de atención (0.30)",
    )
    fig_carga.update_layout(margin=dict(t=40, b=20), height=300)
    st.plotly_chart(fig_carga, use_container_width=True)

    df_disp = disponib[[
        "nombre", "rol", "are", "zore", "disponible",
        "total_casillas", "completadas", "incidencias_abiertas", "indice_carga",
    ]].copy()
    df_disp["disponible"] = df_disp["disponible"].map({True: "✅ Disponible", False: "⛔ No disponible"})
    df_disp.columns = [
        "Nombre", "Rol", "ARE", "ZORE", "Disponibilidad",
        "Casillas", "Completadas", "Incid. abiertas", "Índice carga",
    ]
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Reasignar CAEL a ARE saturada")
    st.caption("Requiere conexión a PostgreSQL para persistir cambios.")
    with st.expander("Reasignación"):
        cael_id   = st.text_input("ID del CAEL",    placeholder="uuid del usuario")
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
