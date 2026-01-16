import sqlite3
import json
from datetime import datetime, timedelta

DB_NAME = "recordia.sqlite"

def construir_cadena_documental(event_id, ventana_horas=72):
    """
    Construye una cadena documental AUP-EXO para un evento dado.
    Devuelve una estructura narrativa, no técnica.
    """

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Evento raíz
    evento = c.execute("""
        SELECT event_id, timestamp, proceso, importancia, hecho, ia_result, decision_usuario, enviado_boveda
        FROM recordia_events
        WHERE event_id = ?
    """, (event_id,)).fetchone()

    if not evento:
        conn.close()
        return None

    (
        ev_id, ts, proceso, importancia, hecho,
        ia_result, decision_usuario, enviado_boveda
    ) = evento

    ts_evento = datetime.fromisoformat(ts)

    # Eventos relacionados (mismo proceso, ventana temporal)
    ts_inicio = (ts_evento - timedelta(hours=ventana_horas)).isoformat()
    ts_fin = (ts_evento + timedelta(hours=ventana_horas)).isoformat()

    relacionados = c.execute("""
        SELECT event_id
        FROM recordia_events
        WHERE proceso = ?
          AND timestamp BETWEEN ? AND ?
          AND event_id != ?
        ORDER BY timestamp ASC
    """, (proceso, ts_inicio, ts_fin, ev_id)).fetchall()

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
                "detalle": json.loads(ia_result) if ia_result else {}
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
        "eventos_relacionados": [r[0] for r in relacionados],
        "declaracion": (
            "Esta cadena documental fue generada automáticamente a partir de "
            "registros verificados. El contenido es de solo lectura."
        )
    }

    return cadena
