SELECT
  a.id,
  a.prioridad,
  a.tipo_alerta,
  a.mensaje,
  a.created_at,
  i.tipo        AS tipo_incidencia,
  i.estatus     AS inc_estatus,
  c.seccion,
  c.clave,
  m.nombre      AS municipio,
  ar.nombre     AS are,
  z.nombre      AS zore
FROM alertas a
LEFT JOIN casillas   c  ON c.id  = a.casilla_id
LEFT JOIN municipios m  ON m.id  = c.municipio_id
LEFT JOIN ares       ar ON ar.id = c.are_id
LEFT JOIN zores      z  ON z.id  = ar.zore_id
LEFT JOIN incidencias i ON i.id  = a.incidencia_id
ORDER BY
  CASE a.prioridad
    WHEN 'critica' THEN 1
    WHEN 'alta'    THEN 2
    WHEN 'media'   THEN 3
    ELSE 4
  END,
  a.created_at DESC
LIMIT 100;
