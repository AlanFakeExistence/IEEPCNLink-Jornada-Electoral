SELECT
  u.id,
  u.nombre,
  u.rol,
  u.disponible,
  ar.nombre   AS are,
  z.nombre    AS zore,
  COUNT(DISTINCT c.id)                                                   AS total_casillas,
  COUNT(c.id) FILTER (WHERE c.estatus = 'recibida_cme')                 AS completadas,
  COUNT(i.id) FILTER (WHERE i.estatus = 'abierta')                      AS incidencias_abiertas,
  ROUND(
    COUNT(i.id) FILTER (WHERE i.estatus = 'abierta')::numeric /
    NULLIF(COUNT(DISTINCT c.id), 0),
  2) AS indice_carga
FROM usuarios u
JOIN ares  ar ON ar.id = u.are_id
JOIN zores z  ON z.id  = ar.zore_id
LEFT JOIN casillas    c ON c.are_id    = u.are_id
LEFT JOIN incidencias i ON i.casilla_id = c.id
WHERE u.rol IN ('cael', 'sel')
  AND u.activo = true
GROUP BY u.id, u.nombre, u.rol, u.disponible, ar.nombre, z.nombre
ORDER BY indice_carga DESC NULLS LAST
LIMIT 100;
