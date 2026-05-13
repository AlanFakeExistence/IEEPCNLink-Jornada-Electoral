SELECT
  i.id,
  i.tipo,
  i.prioridad,
  i.descripcion,
  i.estatus,
  i.hora_reporte,
  i.hora_cierre,
  c.seccion,
  c.clave,
  m.nombre     AS municipio,
  ar.nombre    AS are,
  z.nombre     AS zore,
  u.nombre     AS reportado_por
FROM incidencias i
LEFT JOIN casillas    c  ON c.id  = i.casilla_id
LEFT JOIN municipios  m  ON m.id  = c.municipio_id
LEFT JOIN ares        ar ON ar.id = c.are_id
LEFT JOIN zores       z  ON z.id  = ar.zore_id
LEFT JOIN usuarios    u  ON u.id  = i.usuario_id
ORDER BY
  CASE i.prioridad
    WHEN 'critica' THEN 1
    WHEN 'alta'    THEN 2
    WHEN 'media'   THEN 3
    ELSE 4
  END,
  i.hora_reporte DESC;
