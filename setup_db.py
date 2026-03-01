#!/usr/bin/env python3
"""
Setup script to create the oil_spill_db tables in Postgres.
"""
import os
import psycopg2

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'oil_spill_db')

# SQL commands to create tables (Postgres syntax)
create_users_table_sql = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);
"""

create_history_table_sql = """
CREATE TABLE IF NOT EXISTS detection_history (
    id          SERIAL PRIMARY KEY,
    user_id     INT NOT NULL,
    username    VARCHAR(100) NOT NULL,
    method      VARCHAR(50) NOT NULL,
    filename    VARCHAR(255) NOT NULL,
    area_m2     FLOAT,
    input_image VARCHAR(255),
    output_image VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

create_portal_users_sql = """
CREATE TABLE IF NOT EXISTS portal_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    google_id VARCHAR(255),
    role VARCHAR(50) DEFAULT 'ngo',
    full_name VARCHAR(200),
    organization VARCHAR(200),
    is_active INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_spill_reports_sql = """
CREATE TABLE IF NOT EXISTS spill_reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    severity VARCHAR(50) DEFAULT 'Medium',
    oil_area_m2 FLOAT,
    estimated_volume VARCHAR(255),
    detection_method VARCHAR(100),
    image_path VARCHAR(500),
    created_by INT,
    status VARCHAR(50) DEFAULT 'Active',
    visible_to VARCHAR(500) DEFAULT 'all',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_portal_user FOREIGN KEY (created_by) REFERENCES portal_users(id) ON DELETE SET NULL
);
"""

DATABASE_URL = os.environ.get('DATABASE_URL')

try:
    if DATABASE_URL:
        print(f"Connecting to Postgres using DATABASE_URL...")
        conn = psycopg2.connect(DATABASE_URL)
    else:
        print(f"Connecting to Postgres at {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            database=DB_NAME
        )
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute(create_users_table_sql)
    print("✓ Table 'users' created or already exists.")
    
    # Create detection_history table
    cursor.execute(create_history_table_sql)
    print("✓ Table 'detection_history' created or already exists.")
    
    # Create Portal tables
    cursor.execute(create_portal_users_sql)
    print("✓ Table 'portal_users' created or already exists.")
    
    cursor.execute(create_spill_reports_sql)
    print("✓ Table 'spill_reports' created or already exists.")

    # Create default admin for portal (password: admin123)
    import hashlib
    admin_pw = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute("SELECT id FROM portal_users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO portal_users (username, password_hash, role, full_name, organization)
            VALUES ('admin', %s, 'admin', 'System Administrator', 'Oil Spill Monitoring Authority')
        """, (admin_pw,))
        print("✅ Default portal admin created: username=admin, password=admin123")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✓ Database setup completed successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
