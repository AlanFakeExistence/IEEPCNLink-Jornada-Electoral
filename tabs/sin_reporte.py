from datetime import datetime

import pandas as pd
import streamlit as st

from config import ESTATUS_LABEL


def render(casillas_silenciosas: pd.DataFrame) -> None:
    st.subheader("Casillas sin reporte hace más de 45 minutos")

    if casillas_silenciosas.empty:
        st.success("Todas las casillas han reportado en los últimos 45 minutos.")
        return

    st.warning(f"**{len(casillas_silenciosas)} casilla(s)** sin actividad.", icon="⏰")

    df_silenciosas = casillas_silenciosas[[
        "seccion", "clave", "municipio", "are", "zore",
        "estatus", "cael_responsable", "minutos_sin_reporte", "ultima_actualizacion"
    ]].copy()
    df_silenciosas["estatus"] = df_silenciosas["estatus"].map(lambda s: ESTATUS_LABEL.get(s, s))
    df_silenciosas = df_silenciosas.sort_values("minutos_sin_reporte", ascending=False).reset_index(drop=True)
    df_silenciosas["minutos_sin_reporte"] = df_silenciosas["minutos_sin_reporte"].apply(
        lambda m: f"{int(m)} min"
    )
    df_silenciosas.columns = [
        "Sección", "Clave", "Municipio", "ARE", "ZORE",
        "Estatus", "CAEL", "Sin reporte", "Último reporte",
    ]

    FILAS_POR_PAGINA = 50
    total_paginas = max(1, -(-len(df_silenciosas) // FILAS_POR_PAGINA))

    if "pagina_silenciosas" not in st.session_state:
        st.session_state.pagina_silenciosas = 1

    pagina_actual = st.session_state.pagina_silenciosas

    VENTANA = 9
    if total_paginas <= VENTANA:
        p_inicio, p_fin = 1, total_paginas
    else:
        p_inicio = max(1, pagina_actual - VENTANA // 2)
        p_fin    = min(total_paginas, p_inicio + VENTANA - 1)
        if p_fin - p_inicio < VENTANA - 1:
            p_inicio = max(1, p_fin - VENTANA + 1)
    paginas_visibles = list(range(p_inicio, p_fin + 1))

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
    st.caption(
        f"Página {pagina} de {total_paginas} · "
        f"Mostrando {inicio + 1}–{min(fin, len(df_silenciosas))} de {len(df_silenciosas)} casillas"
    )
