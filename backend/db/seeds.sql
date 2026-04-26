-- Seed supported shops
INSERT INTO shops (name, url) VALUES
('Aldi', 'https://www.aldi.co.uk/')
ON CONFLICT DO NOTHING;

-- Seed allowed units
INSERT INTO units VALUES (0, 'DU', 'dummy', 1.0, 0);
INSERT INTO units (name, type, conversion_factor, normalized_unit_id) VALUES
('G', 'mass', 1.0, 0),
('ML', 'volume', 1.0, 0),
('EACH', 'count', 1.0, 0)
ON CONFLICT DO NOTHING;

UPDATE units SET normalized_unit_id = unit_id WHERE normalized_unit_id = 0;

DELETE FROM units WHERE unit_id = 0;

INSERT INTO units (name, type, conversion_factor, normalized_unit_id) VALUES
('KG', 'mass', 1000.0, (SELECT unit_id FROM units WHERE name = 'G')),
('CL', 'volume', 10.0, (SELECT unit_id FROM units WHERE name = 'ML')),
('L', 'volume', 1000.0, (SELECT unit_id FROM units WHERE name = 'ML'));

-- Example user for development
INSERT into users (username, first_name, password_hash) VALUES
('adele123', 'Adele', 'saltedpassword123')
ON CONFLICT DO NOTHING;