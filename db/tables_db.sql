CREATE TABLE collections_new (
    id SERIAL PRIMARY KEY,
    collections_name VARCHAR(255) NOT NULL UNIQUE
);


CREATE TABLE products_new (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    product_link TEXT NOT NULL UNIQUE,
    product_link_img TEXT,
    price TEXT,
    description TEXT,
    counts_reviews INTEGER DEFAULT 0,
    star_1 INTEGER DEFAULT 0,
    star_2 INTEGER DEFAULT 0,
    star_3 INTEGER DEFAULT 0,
    star_4 INTEGER DEFAULT 0,
    star_5 INTEGER DEFAULT 0,
    
    -- La FK que apunta a colección
    collection_id INT NOT NULL,
    CONSTRAINT fk_product_collection 
        FOREIGN KEY (collection_id) 
        REFERENCES collections_new(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

CREATE TABLE product_store_prices_new (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products_new(id) ON DELETE CASCADE,
    store_name VARCHAR(255) NOT NULL,
    store_price TEXT NOT NULL,  
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Un producto no puede tener dos precios en la misma tienda
    UNIQUE(product_id, store_name)
);

CREATE TABLE product_comments_new (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    title_comments TEXT,
    author_comments TEXT,
    rating_comments INTEGER CHECK (rating_comments IS NULL OR (rating_comments >= 1 AND rating_comments <= 5)),
    message_comments TEXT,
    comment_date DATE,
    page TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- FOREIGN KEY
    CONSTRAINT fk_comment_product 
        FOREIGN KEY (product_id) 
        REFERENCES products_new(id) 
        ON DELETE CASCADE
);

-- Tabla de categorización/análisis de comentarios
CREATE TABLE comment_categories_new (
    id SERIAL PRIMARY KEY,
    comment_id INT NOT NULL UNIQUE,  -- 1:1 con comentarios
    
    -- 1. Difuminación (para bases, polvos, rubores)
    buena_difuminacion BOOLEAN,  -- TRUE = "si", FALSE = "no", NULL = no menciona
    
    -- 2. Aplicación
    aplicacion VARCHAR(10) CHECK (aplicacion IN ('facil', 'dificil', 'regular', NULL)),
    
    -- 3. Textura
    textura VARCHAR(20) CHECK (textura IN ('cremosa', 'suave', 'densa', 'seca', 'pegajosa', NULL)),
    
    -- 4. Aroma
    aroma VARCHAR(30) CHECK (aroma IN ('favorable_con_aroma', 'desfavorable_con_aroma', 
                                        'sin_aroma_conforme', 'sin_aroma_inconforme', NULL)),
    
    -- 5. Comparación con otros productos
    comparacion VARCHAR(10) CHECK (comparacion IN ('mejor', 'peor', NULL)),
    
    -- 6. Cobertura
    buena_cobertura BOOLEAN,  -- TRUE = "si", FALSE = "no", NULL = no menciona
    
    -- 7. Tipo de piel (para bases, polvos, rubores)
    tipo_piel VARCHAR(20) CHECK (tipo_piel IN ('todo_tipo', 'grasa', 'seca', 'mixta', NULL)),
    
    -- 8. Tono de piel
    tono_piel BOOLEAN,  -- TRUE = "si" (le favorece), FALSE = "no" (no le favorece), NULL = no menciona
    
    -- 9. Pigmentación (para labiales, delineadores, rubores)
    pigmentacion_conforme BOOLEAN,  -- TRUE = "si", FALSE = "no", NULL = no menciona
    
    -- 10. Efecto estético (texto libre)
    efecto_estetico TEXT,
    
    -- 11. Conformidad con precio
    precio_conforme BOOLEAN,  -- TRUE = "si", FALSE = "no", NULL = no menciona
    
    -- 12. Recomendación
    recomendacion BOOLEAN,  -- TRUE = "si", FALSE = "no", NULL = no menciona
    
    -- 13. Características favorables (texto con palabras clave)
    caracteristica_favorable TEXT,  -- Ej: "hidratante, brillo"
    
    -- 14. Opinión sobre envase
    envase VARCHAR(15) CHECK (envase IN ('favorable', 'desfavorable', NULL)),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- FOREIGN KEY
    CONSTRAINT fk_category_comment 
        FOREIGN KEY (comment_id) 
        REFERENCES product_comments_new(id) 
        ON DELETE CASCADE
);





CREATE TABLE sentiments (
	id SERIAL PRIMARY KEY, 
	comment_id INT NOT NULL UNIQUE, 
	sentiments TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	    -- FOREIGN KEY
    CONSTRAINT fk_category_comment 
        FOREIGN KEY (comment_id) 
        REFERENCES product_comments_new(id) 
        ON DELETE CASCADE
)



CREATE TABLE traslate (
	id SERIAL PRIMARY KEY, 
	comment_id INT NOT NULL UNIQUE, 
	message_traslate TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	    -- FOREIGN KEY
    CONSTRAINT fk_category_comment 
        FOREIGN KEY (comment_id) 
        REFERENCES product_comments_new(id) 
        ON DELETE CASCADE
)

