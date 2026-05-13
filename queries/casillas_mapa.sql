SELECT DISTINCT ON (c.id)
  c.id,
  c.seccion,
  c.clave,
  c.tipo,
  c.estatus,
  c.lat,
  c.lng,
  c.updated_at AS ultima_actualizacion,
  m.nombre     AS municipio,
  ar.nombre    AS are,
  z.nombre     AS zore,
  u.nombre     AS cael_responsable,
  EXTRACT(EPOCH FROM (NOW() - c.updated_at)) / 60 AS minutos_sin_reporte
FROM casillas c
LEFT JOIN municipios m  ON m.id  = c.municipio_id
LEFT JOIN ares       ar ON ar.id = c.are_id
LEFT JOIN zores      z  ON z.id  = ar.zore_id
LEFT JOIN usuarios u ON u.are_id = c.are_id AND u.rol = 'cael'
ORDER BY c.id;
