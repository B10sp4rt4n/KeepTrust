import streamlit as st
import json
import uuid
from datetime import datetime
import hashlib
import os
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
from report_keeptrust import construir_dataset_exo, generar_reporte_keeptrust
from recordia_chain import construir_cadena_documental
from database import get_database_connection, init_database, execute_query

# ---------- CONFIG ----------
HOT_VAULT_PATH = "hot_vault"
os.makedirs(HOT_VAULT_PATH, exist_ok=True)

# ---------- DB ----------
conn, db_type = get_database_connection()
c = init_database(conn, db_type)

st.sidebar.info(f"🗄️ Base de datos: **{db_type.upper()}**")

# Verificar si hay API key disponible
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Para Streamlit Cloud, también revisar secrets
if not OPENAI_API_KEY:
    try:
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
    except:
        pass

# Si no hay API key en el entorno, pedir en la UI
if not OPENAI_API_KEY and "openai_key" in st.session_state:
    OPENAI_API_KEY = st.session_state["openai_key"]

USE_REAL_IA = bool(OPENAI_API_KEY)

if USE_REAL_IA:
    client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- SISTEMA PROMPT ----------
SYSTEM_PROMPT = """
Eres un asistente de análisis de eventos de negocio.
Tu función NO es modificar hechos, solo evaluarlos.

Debes:
- Clasificar el evento
- Estimar nivel de riesgo
- Sugerir un tipo de recipiente
- Recomendar si debe guardarse como evidencia

Responde EXCLUSIVAMENTE en JSON válido.
No agregues texto adicional.
"""

# ---------- IA REAL CON OPENAI ----------
def evaluar_con_ia(hecho, proceso, importancia):
    if not USE_REAL_IA:
        # Modo MOCK si no hay API key
        if importancia == "Crítico":
            return {
                "clasificacion": "Evento Crítico",
                "nivel_riesgo": "Alto",
                "recipiente_sugerido": "Evidencia Crítica",
                "guardar_boveda": True,
                "justificacion": "Alta relevancia para auditoría o seguimiento [MODO MOCK]"
            }
        elif proceso in ["Legal / Cumplimiento", "RH"]:
            return {
                "clasificacion": "Evento Sensible",
                "nivel_riesgo": "Medio",
                "recipiente_sugerido": "Evidencia Operativa",
                "guardar_boveda": True,
                "justificacion": "Evento sensible por naturaleza del proceso [MODO MOCK]"
            }
        else:
            return {
                "clasificacion": "Registro Informativo",
                "nivel_riesgo": "Bajo",
                "recipiente_sugerido": "Registro",
                "guardar_boveda": False,
                "justificacion": "Evento sin impacto crítico inmediato [MODO MOCK]"
            }
    
    # Modo REAL con OpenAI
    user_prompt = f"""
Evento:
\"\"\"{hecho}\"\"\"

Proceso: {proceso}
Importancia percibida por el usuario: {importancia}

Evalúa el evento y responde en el siguiente formato JSON:

{{
  "clasificacion": "",
  "nivel_riesgo": "",
  "recipiente_sugerido": "",
  "guardar_boveda": true | false,
  "justificacion": ""
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content
    return json.loads(content)

# ---------- HOT VAULT ----------
def guardar_en_hot_vault(evento):
    contenido = json.dumps(evento, indent=2, ensure_ascii=False)
    hash_evento = hashlib.sha256(contenido.encode()).hexdigest()
    filename = f"{HOT_VAULT_PATH}/{evento['event_id']}_{hash_evento}.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(contenido)
    return hash_evento

# ---------- UI ----------
st.title("🧠 Demo Recordia + IA + Hot Vault")

# Configuración de API Key en sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    if not USE_REAL_IA:
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Ingresa tu API key de OpenAI para usar IA real"
        )
        
        if st.button("Conectar API"):
            if api_key_input:
                st.session_state["openai_key"] = api_key_input
                st.rerun()
            else:
                st.error("Ingresa una API key válida")
    else:
        st.success("✅ OpenAI conectado")
        if "openai_key" in st.session_state:
            if st.button("Desconectar"):
                del st.session_state["openai_key"]
                st.rerun()

# Mostrar modo de operación
if USE_REAL_IA:
    st.info("🤖 Modo IA Real activo")
else:
    st.warning("⚠️ Modo MOCK - Ingresa tu API key en el sidebar para usar IA real")

st.header("📋 Registrar evento")

# Contador para resetear el formulario
if "form_counter" not in st.session_state:
    st.session_state["form_counter"] = 0

hecho = st.text_area("¿Qué ocurrió?", key=f"hecho_{st.session_state['form_counter']}")
proceso = st.selectbox(
    "Proceso involucrado",
    ["Operaciones", "Ventas", "RH", "Legal / Cumplimiento", "Otro"],
    key=f"proceso_{st.session_state['form_counter']}"
)
importancia = st.selectbox(
    "Importancia percibida",
    ["Informativo", "Relevante", "Crítico"],
    key=f"importancia_{st.session_state['form_counter']}"
)

if st.button("Evaluar con IA"):
    if hecho.strip() == "":
        st.warning("Describe el evento")
    else:
        event_id = f"EVT-{uuid.uuid4()}"
        timestamp = datetime.utcnow().isoformat()

        ia_result = evaluar_con_ia(hecho, proceso, importancia)

        st.session_state["ia_result"] = ia_result
        st.session_state["event_id"] = event_id
        st.session_state["timestamp"] = timestamp

if "ia_result" in st.session_state:
    st.subheader("🤖 Evaluación IA")
    st.json(st.session_state["ia_result"])

    guardar = st.checkbox(
        "Guardar en Hot Vault",
        value=st.session_state["ia_result"]["guardar_boveda"]
    )

    if st.button("Confirmar decisión"):
        enviado = 0
        hash_boveda = None

        if guardar:
            evento_boveda = {
                "event_id": st.session_state["event_id"],
                "timestamp": st.session_state["timestamp"],
                "hecho": hecho,
                "proceso": proceso,
                "importancia": importancia,
                "ia_result": st.session_state["ia_result"],
                "decision_usuario": "Guardar en bóveda"
            }
            hash_boveda = guardar_en_hot_vault(evento_boveda)
            enviado = 1

        execute_query(c, """
        INSERT INTO recordia_events VALUES (?,?,?,?,?,?,?,?)
        """, (
            st.session_state["event_id"],
            st.session_state["timestamp"],
            proceso,
            importancia,
            hecho,
            json.dumps(st.session_state["ia_result"]),
            "Guardar" if guardar else "No guardar",
            enviado
        ), db_type)
        conn.commit()

        st.success("Evento registrado en Recordia")
        if enviado:
            st.info(f"Evidencia sellada en Hot Vault\nHash: {hash_boveda}")
        
        del st.session_state["ia_result"]
        del st.session_state["event_id"]
        del st.session_state["timestamp"]
        
        # Mostrar botón destacado inmediatamente después de registro
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🆕 AGREGAR NUEVA EVIDENCIA", type="primary", use_container_width=True):
                # Incrementar contador para resetear formulario
                st.session_state["form_counter"] += 1
                st.rerun()

# ---------- DASHBOARD ----------
st.divider()
st.header("📊 Estadísticas de Recordia")

df = pd.read_sql("SELECT * FROM recordia_events", conn)

if df.empty:
    st.info("Aún no hay eventos registrados")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Eventos Totales", len(df))
    with col2:
        st.metric("Enviados a Hot Vault", df["enviado_boveda"].sum())

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Eventos por Proceso")
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        proceso_counts = df["proceso"].value_counts()
        ax1.pie(proceso_counts, labels=proceso_counts.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

    with col_chart2:
        st.subheader("Eventos por Importancia")
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        importancia_counts = df["importancia"].value_counts()
        colors = {'Crítico': '#ff4b4b', 'Relevante': '#ffa500', 'Informativo': '#4b9eff'}
        pie_colors = [colors.get(label, '#cccccc') for label in importancia_counts.index]
        ax2.pie(importancia_counts, labels=importancia_counts.index, autopct='%1.1f%%', 
                startangle=90, colors=pie_colors)
        ax2.axis('equal')
        st.pyplot(fig2)

    st.subheader("Eventos acumulados en el tiempo")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_sorted = df.sort_values("timestamp")
    df_sorted["acumulado"] = range(1, len(df_sorted) + 1)

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.plot(df_sorted["timestamp"], df_sorted["acumulado"], marker='o', linewidth=2)
    ax3.set_xlabel("Tiempo", fontsize=12)
    ax3.set_ylabel("Eventos acumulados", fontsize=12)
    ax3.grid(True, alpha=0.3)
    # Rotar etiquetas para mejor legibilidad
    plt.xticks(rotation=45, ha='right')
    fig3.tight_layout()
    st.pyplot(fig3)

# ---------- REVISIÓN DE BÓVEDA ----------
st.divider()
st.header("🧾 Revisión de Bóveda — Reporte KeepTrust")

st.info("Genera un reporte estructurado desde registros inmutables sin exponer evidencia sellada")

if st.button("📄 Generar Reporte de Confianza", type="primary"):
    with st.spinner("Generando reporte..."):
        dataset_exo = construir_dataset_exo()
        reporte = generar_reporte_keeptrust(
            dataset_exo, 
            api_key=OPENAI_API_KEY,
            use_mock=not USE_REAL_IA
        )

        st.subheader("📋 Reporte Generado")
        st.text_area("Reporte KeepTrust", reporte, height=500, key="reporte_output")

        st.download_button(
            "⬇️ Descargar reporte (.txt)",
            reporte,
            file_name=f"KeepTrust_Reporte_Confianza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# ---------- CADENA DOCUMENTAL ----------
st.divider()
st.header("🧬 Cadena Documental de Evidencia (Recordia)")

st.info("Revisa la trazabilidad completa de un evento: desde el registro hasta la evidencia sellada")

# Recargar df para asegurar que esté disponible
df = pd.read_sql("SELECT * FROM recordia_events", conn)
event_ids = df["event_id"].tolist() if not df.empty else []

if event_ids:
    selected_event = st.selectbox(
        "Selecciona un evento para revisar su cadena documental",
        event_ids
    )

    if st.button("🔍 Ver cadena documental"):
        cadena = construir_cadena_documental(selected_event)

        if cadena:
            st.subheader(f"📄 Caso {cadena['caso_id']}")

            st.markdown(f"**Proceso:** {cadena['proceso']}")
            st.markdown(f"**Evento raíz:** `{cadena['evento_raiz']}`")

            st.markdown("### 🕒 Línea de tiempo")
            for i, paso in enumerate(cadena["linea_tiempo"], 1):
                with st.expander(f"{i}. {paso['titulo']}", expanded=(i==1)):
                    if paso.get('timestamp'):
                        st.markdown(f"**⏰ Timestamp:** {paso['timestamp']}")
                    if paso.get('descripcion'):
                        st.markdown(f"**📝 Descripción:**")
                        st.write(paso['descripcion'])
                    if paso.get("detalle"):
                        st.markdown("**📊 Detalle:**")
                        if isinstance(paso["detalle"], dict):
                            st.json(paso["detalle"])
                        else:
                            st.write(paso["detalle"])

            st.markdown("### 🔗 Eventos relacionados")
            if cadena["eventos_relacionados"]:
                st.markdown(f"_Eventos en el mismo proceso dentro de 72 horas:_")
                for ev in cadena["eventos_relacionados"]:
                    st.markdown(f"- `{ev}`")
            else:
                st.markdown("_No se detectaron eventos relacionados en la ventana temporal._")

            st.success(cadena["declaracion"])
        else:
            st.error("No se pudo construir la cadena documental para este evento")
else:
    st.warning("No hay eventos disponibles para revisión documental.")
