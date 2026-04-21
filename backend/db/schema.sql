-- This file contains the database schema

-- Some utility tables
CREATE TABLE IF NOT EXISTS shops (
    shop_id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL,
    url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS brands (
    brand_id SERIAL PRIMARY KEY,
    name VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    first_name VARCHAR(60),
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS units (
    unit_id SERIAL PRIMARY KEY,
    name VARCHAR(4) UNIQUE NOT NULL,
    type VARCHAR(20) NOT NULL
);

-- Main tables
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    brand_id INT NOT NULL REFERENCES brands(brand_id),

    price NUMERIC(8, 2) NOT NULL,

    quantity NUMERIC(10, 3) NOT NULL,
    unit_id INT NOT NULL REFERENCES units(unit_id),
    
    normalized_quantity NUMERIC(10, 3) NOT NULL,
    normalized_unit_id INT NOT NULL REFERENCES units(unit_id),

    product_url VARCHAR(255) NOT NULL UNIQUE,
    shop_id INT NOT NULL REFERENCES shops(shop_id) ON DELETE RESTRICT,

    -- Handle removal of products (e.g. when it is not found during repeated scraping) to notify users that they need to update their recipes
    last_updated TIMESTAMP NOT NULL,
    not_found BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE (product_url, shop_id)
);

CREATE TABLE IF NOT EXISTS recipes (
    recipe_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id),
    name varchar(120) NOT NULL,
    number_of_portions NUMERIC(5,1) NOT NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Junction table to handle ingredients in recipes
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_ingredient_id SERIAL PRIMARY KEY,
    recipe_id INT NOT NULL REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    ingredient_id INT NOT NULL REFERENCES ingredients(ingredient_id),

    quantity NUMERIC(10, 3) NOT NULL,
    unit_id INT NOT NULL REFERENCES units(unit_id),

    normalized_quantity NUMERIC(10, 3) NOT NULL,
    normalized_unit_id INT NOT NULL REFERENCES units(unit_id),

    UNIQUE (recipe_id, ingredient_id)
);
