-- Seed data para secciones por defecto
-- Este archivo es de referencia. La inicialización se hace desde database/db.py

INSERT INTO section (name, emoji, created_at) VALUES
  ('Refrigerador', '🧊', CURRENT_TIMESTAMP),
  ('Almacén 1', '📦', CURRENT_TIMESTAMP),
  ('Almacén 2', '🏺', CURRENT_TIMESTAMP);

-- Ejemplos de items (opcional, para testing)
-- INSERT INTO item (name, emoji, quantity, unit, threshold, section_id, updated_at) VALUES
--   ('Leche', '🥛', 2, 'L', 1, 1, CURRENT_TIMESTAMP),
--   ('Huevos', '🥚', 6, 'unidades', 3, 1, CURRENT_TIMESTAMP),
--   ('Arroz', '🍚', 5, 'kg', 2, 2, CURRENT_TIMESTAMP);
