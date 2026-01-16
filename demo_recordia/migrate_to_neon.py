import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os

def migrate_sqlite_to_neon(sqlite_db_path, neon_connection_string):
    """
    Migra datos de SQLite a Neon (PostgreSQL)
    """
    # Conectar a SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conectar a Neon PostgreSQL
    pg_conn = psycopg2.connect(neon_connection_string)
    pg_cursor = pg_conn.cursor()
    
    try:
        # Crear tabla en PostgreSQL
        pg_cursor.execute("""
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
        
        # Leer datos de SQLite
        sqlite_cursor.execute("SELECT * FROM recordia_events")
        rows = sqlite_cursor.fetchall()
        
        if rows:
            # Insertar en PostgreSQL
            insert_query = """
            INSERT INTO recordia_events 
            (event_id, timestamp, proceso, importancia, hecho, ia_result, decision_usuario, enviado_boveda)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            pg_cursor.executemany(insert_query, rows)
            pg_conn.commit()
            
            print(f"✅ Migración exitosa: {len(rows)} registros transferidos")
        else:
            print("ℹ️ No hay datos para migrar")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"❌ Error en migración: {e}")
        raise
    finally:
        sqlite_cursor.close()
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()

if __name__ == "__main__":
    # Configuración
    SQLITE_DB = "recordia.sqlite"
    
    # Obtener de variable de entorno o Streamlit secrets
    NEON_CONNECTION = os.getenv("DATABASE_URL") or os.getenv("NEON_CONNECTION_STRING")
    
    if not NEON_CONNECTION:
        print("❌ Error: Configure DATABASE_URL o NEON_CONNECTION_STRING")
        print("\nEjemplo:")
        print('export DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"')
        exit(1)
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Error: No se encuentra {SQLITE_DB}")
        exit(1)
    
    print(f"🔄 Iniciando migración de {SQLITE_DB} a Neon PostgreSQL...")
    migrate_sqlite_to_neon(SQLITE_DB, NEON_CONNECTION)
    print("🎉 Proceso completado")
