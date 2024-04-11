    CREATE TABLE accelerometer_data (
        id SERIAL PRIMARY KEY,
        x INTEGER,
        y INTEGER,
        z INTEGER,
        time TIMESTAMP
    );

    CREATE TABLE gps_data (
        id SERIAL PRIMARY KEY,
        longitude DOUBLE PRECISION,
        latitude DOUBLE PRECISION,
        time TIMESTAMP
    );

    CREATE TABLE parking_data (
        id SERIAL PRIMARY KEY,
        empty_count INTEGER,
        longitude DOUBLE PRECISION,
        latitude DOUBLE PRECISION,
        time TIMESTAMP
    );
    
