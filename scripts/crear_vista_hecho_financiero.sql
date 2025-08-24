DROP VIEW IF EXISTS hecho_financiero;

CREATE VIEW hecho_financiero AS
SELECT 
    p.usuario_id,
    p.año,
    p.mes,
    c.tipo,
    p.categoria_id,
    'presupuesto' AS escenario,
    p.monto_presupuestado AS monto
FROM presupuesto p
JOIN categoria c ON p.categoria_id = c.id

UNION ALL

SELECT 
    t.usuario_id,
    CAST(STRFTIME('%Y', t.fecha) AS INTEGER) AS año,
    CAST(STRFTIME('%m', t.fecha) AS INTEGER) AS mes,
    t.tipo,
    t.categoria_id,
    'real' AS escenario,
    t.monto AS monto
FROM transaccion t;
