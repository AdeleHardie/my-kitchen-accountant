-- Seed supported shops
INSERT INTO shops (name, url) VALUES
('Aldi', 'https://www.aldi.co.uk/')
ON CONFLICT DO NOTHING;

-- Seed allowed units
INSERT INTO units (name, type) VALUES
('G', 'mass'),
('KG', 'mass'),
('ML', 'volume'),
('CL', 'volume'),
('L', 'volume'),
('EACH', 'count')
ON CONFLICT DO NOTHING;

-- Example user for development
INSERT into users (username, first_name, password_hash) VALUES
('adele123', 'Adele', 'saltedpassword123')
ON CONFLICT DO NOTHING;