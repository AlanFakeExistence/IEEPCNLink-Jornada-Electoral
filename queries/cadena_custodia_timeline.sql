SELECT
  p.id                    AS paquete_id,
  c.seccion,
  c.clave,
  m.nombre                AS municipio,
  p.opcion_entrega        AS mecanismo,
  p.estatus,
  p.hora_integracion,
  p.hora_salida_casilla,
  p.hora_recepcion_cme,
  cc.evento,
  cc.ubicacion,
  cc.hora                 AS hora_evento,
  cc.responsable_nombre   AS responsable
FROM paquetes_electorales p
LEFT JOIN casillas        c  ON c.id  = p.casilla_id
LEFT JOIN municipios      m  ON m.id  = c.municipio_id
LEFT JOIN cadena_custodia cc ON cc.paquete_id = p.id
WHERE p.estatus NOT IN ('en_casilla', 'entregado_cme')
ORDER BY p.id, cc.hora ASC;
