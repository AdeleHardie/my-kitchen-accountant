-- Seed supported shops
INSERT INTO shops (name, url) VALUES
('Aldi', 'https://www.aldi.co.uk/')
ON CONFLICT DO NOTHING;

-- Seed allowed units
INSERT INTO units (name, type) VALUES
('G', 'mass'),
('KG', 'mass'),
('ML', 'volume'),
('L', 'volume'),
('EACH', 'count')
ON CONFLICT DO NOTHING;

-- TODO: add example user for recipe creation and testing