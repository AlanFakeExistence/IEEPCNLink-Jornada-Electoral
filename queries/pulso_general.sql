SELECT
  COUNT(*) FILTER (WHERE estatus = 'pendiente')         AS pendientes,
  COUNT(*) FILTER (WHERE estatus = 'instalada')         AS instaladas,
  COUNT(*) FILTER (WHERE estatus = 'en_votacion')       AS votando,
  COUNT(*) FILTER (WHERE estatus = 'cerrada')           AS cerradas,
  COUNT(*) FILTER (WHERE estatus = 'en_computo')        AS en_computo,
  COUNT(*) FILTER (WHERE estatus = 'paquete_integrado') AS paquete_integrado,
  COUNT(*) FILTER (WHERE estatus = 'en_traslado')       AS en_traslado,
  COUNT(*) FILTER (WHERE estatus = 'recibida_cme')      AS recibidas_cme,
  COUNT(*)                                              AS total
FROM casillas;
