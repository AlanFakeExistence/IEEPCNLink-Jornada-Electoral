SELECT
  COUNT(*) FILTER (WHERE c.estatus = 'pendiente')         AS pendientes,
  COUNT(*) FILTER (WHERE c.estatus = 'instalada')         AS instaladas,
  COUNT(*) FILTER (WHERE c.estatus = 'en_votacion')       AS votando,
  COUNT(*) FILTER (WHERE c.estatus = 'cerrada')           AS cerradas,
  COUNT(*) FILTER (WHERE c.estatus = 'en_computo')        AS en_computo,
  COUNT(*) FILTER (WHERE c.estatus = 'paquete_integrado') AS paquete_integrado,
  (SELECT COUNT(*) FROM paquetes_electorales WHERE estatus = 'en_traslado')   AS en_traslado,
  (SELECT COUNT(*) FROM paquetes_electorales WHERE estatus = 'entregado_cme') AS recibidas_cme,
  COUNT(*)                                                                     AS total
FROM casillas c;
