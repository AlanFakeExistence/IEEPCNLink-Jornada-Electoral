"""
Constantes compartidas del dashboard.
"""

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

COLORES_PRIORIDAD = {
    "critica": "#dc3545",
    "alta":    "#ffc107",
    "media":   "#fd7e14",
    "baja":    "#198754",
}
