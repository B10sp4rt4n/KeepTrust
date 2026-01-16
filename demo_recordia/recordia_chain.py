import json
from datetime import datetime, timedelta
from database import get_database_connection, execute_query

def construir_cadena_documental(event_id, ventana_horas=72):
    """
    Construye una cadena documental AUP-EXO para un evento dado.
    Devuelve una estructura narrativa, no técnica.
    """

    conn, db_type = get_database_connection()
    c = conn.cursor()

    # Evento raíz
    query = """
        SELECT event_id, timestamp, proceso, importancia, hecho, ia_result, decision_usuario, enviado_boveda
        FROM recordia_events
        WHERE event_id = ?
    """
    execute_query(c, query, (event_id,), db_type)
    evento = c.fetchone()

    if not evento:
        conn.close()
        return None

    # Compatibilidad SQLite (tupla) y PostgreSQL (dict)
    if isinstance(evento, dict):
        ev_id = evento['event_id']
        ts = str(evento['timestamp'])
        proceso = evento['proceso']
        importancia = evento['importancia']
        hecho = evento['hecho']
        ia_result = evento['ia_result']
        decision_usuario = evento['decision_usuario']
        enviado_boveda = evento['enviado_boveda']
    else:
    query_rel = """
        SELECT event_id
        FROM recordia_events
        WHERE proceso = ?
          AND timestamp BETWEEN ? AND ?
          AND event_id != ?
        ORDER BY timestamp ASC
    """
    execute_query(c, query_rel, (proceso, ts_inicio, ts_fin, ev_id), db_type)
    relacionados = c.fetchall()

    conn.close()

    # Construcción narrativa (EXO)
    cadena = {
        "caso_id": f"CASE-{ev_id}",
        "evento_raiz": ev_id,
        "proceso": proceso,
        "linea_tiempo": [
            {
                "tipo": "evento",
                "titulo": "Evento registrado",
                "timestamp": ts,
                "descripcion": hecho
            },
            {
                "tipo": "ia",
                "titulo": "Evaluación asistida por IA",
                "detalle": json.loads(ia_result) if isinstance(ia_result, str) else ia_result if ia_result else {}
            },
            {
                "tipo": "decision",
                "titulo": "Decisión humana registrada",
                "detalle": decision_usuario
            },
            {
                "tipo": "evidencia",
                "titulo": "Estado de evidencia",
                "detalle": "Sellada en Hot Vault" if enviado_boveda else "No enviada a bóveda"
            }
        ],
        "eventos_relacionados": [r['event_id'] if isinstance(r, dict) else on_usuario
            },
            {
                "tipo": "evidencia",
                "titulo": "Estado de evidencia",
                "detalle": "Sellada en Hot Vault" if enviado_boveda else "No enviada a bóveda"
            }
        ],
        "eventos_relacionados": [r[0] for r in relacionados],
        "declaracion": (
            "Esta cadena documental fue generada automáticamente a partir de "
            "registros verificados. El contenido es de solo lectura."
        )
    }

    return cadena
