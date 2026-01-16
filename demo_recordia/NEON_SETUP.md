# 🗄️ Configuración de Base de Datos Neon

## Pasos para configurar Neon PostgreSQL

### 1. Crear cuenta en Neon

Ve a [neon.tech](https://neon.tech) y crea una cuenta gratuita.

### 2. Crear un nuevo proyecto

- Nombre: `keeptrust-recordia`
- Región: Elige la más cercana
- PostgreSQL versión: 16 (recomendado)

### 3. Obtener Connection String

En tu dashboard de Neon, copia la connection string:

```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
```

### 4. Configurar en Streamlit Cloud

En Streamlit Cloud → App settings → Secrets:

```toml
DATABASE_URL = "postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require"
OPENAI_API_KEY = "sk-tu-clave-aqui"  # opcional
```

### 5. Migrar datos existentes (si los tienes)

Si ya tienes datos en SQLite local:

```bash
# Instalar dependencias
pip install psycopg2-binary

# Configurar variable de entorno
export DATABASE_URL="postgresql://username:password@host/db?sslmode=require"

# Ejecutar migración
python migrate_to_neon.py
```

### 6. Desplegar en Streamlit Cloud

La aplicación detectará automáticamente si hay `DATABASE_URL` configurado:
- ✅ Con DATABASE_URL → Usa PostgreSQL (Neon)
- ✅ Sin DATABASE_URL → Usa SQLite local (fallback)

## Ventajas de Neon

- ✅ **Serverless:** Se escala automáticamente
- ✅ **Gratuito:** 500MB storage + 100 horas de compute/mes
- ✅ **Rápido:** Branching instantáneo de bases de datos
- ✅ **Persistente:** Los datos no se pierden al reiniciar la app
- ✅ **PostgreSQL completo:** JSON, índices, transacciones

## Estructura de la tabla

```sql
CREATE TABLE recordia_events (
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

-- Índices para performance
CREATE INDEX idx_event_id ON recordia_events(event_id);
CREATE INDEX idx_proceso ON recordia_events(proceso);
CREATE INDEX idx_timestamp ON recordia_events(timestamp);
```

## Testing local con PostgreSQL

Si quieres probar localmente con PostgreSQL:

```bash
# Opción 1: Docker
docker run -d \
  --name postgres-recordia \
  -e POSTGRES_PASSWORD=yourpass \
  -e POSTGRES_DB=recordia \
  -p 5432:5432 \
  postgres:16

export DATABASE_URL="postgresql://postgres:yourpass@localhost:5432/recordia"

# Opción 2: PostgreSQL local
# Instalar PostgreSQL en tu sistema y configurar DATABASE_URL
```

## Monitoring

Neon dashboard muestra:
- Uso de storage
- Conexiones activas
- Queries ejecutados
- Performance metrics

## Costos

Plan gratuito de Neon:
- Storage: 500 MB
- Compute: 100 horas/mes
- Connections: Ilimitadas

**Suficiente para ~50,000 eventos** con la estructura actual.

Para producción:
- Plan Pro: $19/mes (3GB storage, siempre activo)
- Plan Enterprise: Custom pricing

## Troubleshooting

### Error: "connection refused"
- Verifica que la connection string sea correcta
- Asegúrate que incluye `?sslmode=require`

### Error: "SSL required"
- Neon requiere SSL, agrega `?sslmode=require` al final de la URL

### Error: "password authentication failed"
- Regenera el password en Neon dashboard
- Actualiza la connection string en secrets

### La app sigue usando SQLite
- Verifica que DATABASE_URL esté configurado en Streamlit Cloud secrets
- Reinicia la app después de configurar secrets
- Chequea el sidebar: debe mostrar "🗄️ Base de datos: POSTGRESQL"
