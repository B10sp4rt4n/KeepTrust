import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_connection():
    """
    Devuelve conexión a la base de datos (PostgreSQL o SQLite)
    """
    # Intentar PostgreSQL (Neon) primero
    database_url = os.getenv("DATABASE_URL")
    
    # Para Streamlit Cloud secrets
    try:
        import streamlit as st
        if not database_url:
            database_url = st.secrets.get("DATABASE_URL")
    except:
        pass
    
    if database_url:
        # Usar PostgreSQL (Neon)
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor), "postgresql"
    else:
        # Fallback a SQLite local
        return sqlite3.connect("recordia.sqlite", check_same_thread=False), "sqlite"

def init_database(conn, db_type):
    """
    Inicializa la base de datos con las tablas necesarias
    """
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recordia_events (
            id SERIAL PRIMARY KEY,
            event_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            proceso TEXT NOT NULL,
            importancia TEXT NOT NULL,
            hecho TEXT NOT NULL,
            ia_result JSONB,
            decision_usuario TEXT NOT NULL,
            enviado_boveda INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_event_id ON recordia_events(event_id);
        CREATE INDEX IF NOT EXISTS idx_proceso ON recordia_events(proceso);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON recordia_events(timestamp);
        """)
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recordia_events (
            event_id TEXT,
            timestamp TEXT,
            proceso TEXT,
            importancia TEXT,
            hecho TEXT,
            ia_result TEXT,
            decision_usuario TEXT,
            enviado_boveda INTEGER
        )
        """)
    
    conn.commit()
    return cursor

def execute_query(cursor, query, params=None, db_type="sqlite"):
    """
    Ejecuta query adaptando sintaxis según base de datos
    """
    if db_type == "postgresql":
        # Reemplazar ? por %s para PostgreSQL
        query = query.replace("?", "%s")
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    return cursor
