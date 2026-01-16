import json
from collections import Counter
from openai import OpenAI
import os
from datetime import datetime
from database import get_database_connection, execute_query

# ---------- DATASET EXO ----------
def construir_dataset_exo(periodo_inicio=None, periodo_fin=None):
    conn, db_type = get_database_connection()
    c = conn.cursor()

    query = "SELECT timestamp, proceso, importancia, ia_result, enviado_boveda FROM recordia_events"
    execute_query(c, query, db_type=db_type)
    rows = c.fetchall()
    conn.close()

    total_eventos = len(rows)
    
    # Manejar diferencia entre SQLite (tupla) y PostgreSQL (dict)
    if rows and isinstance(rows[0], dict):
        eventos_sellados = sum(r['enviado_boveda'] for r in rows)
    else:
        eventos_sellados = sum(r[4] for r in rows)

    procesos = Counter()
    riesgos = Counter()
    ia_recomienda = 0
    humano_acepta = eventos_sellados

    for row in rows:
        # Compatibilidad SQLite (tupla) y PostgreSQL (dict)
        if isinstance(row, dict):
            proceso = row['proceso']
            importancia = row['importancia']
            ia_result = row['ia_result']
            enviado = row['enviado_boveda']
        else:
            ts, proceso, importancia, ia_result, enviado = row
        
        procesos[proceso] += 1
        riesgos[importancia] += 1

        if ia_result:
            if isinstance(ia_result, str):
                ia_data = json.loads(ia_result)
            else:
                ia_data = ia_result
            
            if ia_data.get("guardar_boveda"):
                ia_recomienda += 1

    dataset = {
        "periodo": {
            "inicio": periodo_inicio or "N/A",
            "fin": periodo_fin or "N/A"
        },
        "eventos_totales": total_eventos,
        "eventos_sellados": eventos_sellados,
        "por_proceso": dict(procesos),
        "por_riesgo": dict(riesgos),
        "ia_vs_humano": {
            "recomendados_ia": ia_recomienda,
            "aceptados_humano": humano_acepta
        },
        "timestamp_reporte": datetime.utcnow().isoformat()
    }

    return dataset

# ---------- PROMPT ----------
SYSTEM_PROMPT = """
Eres un generador de reportes de auditoría y confianza.
No decides, no juzgas, no recomiendas acciones.

Redactas reportes claros, profesionales y neutrales.
No describas mecanismos internos del sistema.
"""

def generar_reporte_keeptrust(dataset_exo, api_key=None, use_mock=False):
    """
    Genera el reporte KeepTrust usando OpenAI o modo MOCK
    """
    if use_mock or not api_key:
        # Modo MOCK
        return f"""
═══════════════════════════════════════════════════════════
        REPORTE DE CONFIANZA KEEPTRUST [MODO MOCK]
═══════════════════════════════════════════════════════════

1. RESUMEN EJECUTIVO
────────────────────────────────────────────────────────────

Período analizado: {dataset_exo['periodo']['inicio']} - {dataset_exo['periodo']['fin']}
Fecha de generación: {dataset_exo['timestamp_reporte']}

Total de eventos registrados: {dataset_exo['eventos_totales']}
Eventos sellados en bóveda: {dataset_exo['eventos_sellados']}

2. ACTIVIDAD REGISTRADA
────────────────────────────────────────────────────────────

Distribución por Proceso:
{chr(10).join(f"  • {k}: {v} eventos" for k, v in dataset_exo['por_proceso'].items())}

Distribución por Nivel de Riesgo:
{chr(10).join(f"  • {k}: {v} eventos" for k, v in dataset_exo['por_riesgo'].items())}

3. EVALUACIÓN ASISTIDA POR IA
────────────────────────────────────────────────────────────

Eventos recomendados para sellado (IA): {dataset_exo['ia_vs_humano']['recomendados_ia']}
Eventos efectivamente sellados (Humano): {dataset_exo['ia_vs_humano']['aceptados_humano']}

La IA actúa como asistente de evaluación, mientras que la decisión
final de sellado permanece bajo control humano.

4. EVIDENCIA SELLADA
────────────────────────────────────────────────────────────

Total de evidencias en bóveda: {dataset_exo['eventos_sellados']}
Cada evidencia cuenta con hash SHA-256 verificable.

5. RELACIONES Y PATRONES
────────────────────────────────────────────────────────────

Este reporte identifica tendencias en la actividad registrada
sin exponer contenido específico de los eventos sellados.

6. DECLARACIÓN DE ALCANCE
────────────────────────────────────────────────────────────

Este reporte fue generado desde registros inmutables del sistema
KeepTrust. La evidencia referenciada permanece sellada y puede ser
verificada mediante hash cuando sea requerido.

═══════════════════════════════════════════════════════════
                    FIN DEL REPORTE
═══════════════════════════════════════════════════════════
"""
    
    # Modo REAL con OpenAI
    client = OpenAI(api_key=api_key)
    
    user_prompt = f"""
Con base en el siguiente dataset estructurado,
genera un REPORTE DE CONFIANZA KEEPTRUST
con la estructura exacta:

1. Resumen Ejecutivo
2. Actividad Registrada
3. Evaluación Asistida por IA
4. Evidencia Sellada
5. Relaciones y Patrones
6. Declaración de Alcance

Dataset:
{json.dumps(dataset_exo, indent=2, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content
