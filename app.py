import streamlit as st
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Config AWS
# ──────────────────────────────────────────────
region = os.getenv("AWS_REGION", "us-east-1")
model_id = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name=region)

# ──────────────────────────────────────────────
# Cargar prompts desde archivos
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_prompt(relative_path: str) -> str:
    full_path = os.path.join(BASE_DIR, relative_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = load_prompt("prompts/comportamiento")
CONTEXT_TEMPLATE = load_prompt("prompts/contexto")

# ──────────────────────────────────────────────
# Construir contexto dinámico
# ──────────────────────────────────────────────
def build_context(topic: str, history: str, user_input: str, mode: str) -> str:
    return CONTEXT_TEMPLATE.format(
        topic=topic,
        history=history,
        user_input=user_input,
        mode=mode,
    )

# ──────────────────────────────────────────────
# Detectar modo
# ──────────────────────────────────────────────
def detect_mode(user_input: str) -> str:
    text = user_input.lower().strip()
    if "pregunta" in text or "quiz" in text or "examen" in text or "practica" in text or "práctica" in text:
        return "EXAMEN"
    elif text in ["a", "b", "c", "d"]:
        return "CORRECCIÓN"
    else:
        return "EXPLICACIÓN"

# ──────────────────────────────────────────────
# Llamada a Bedrock
# ──────────────────────────────────────────────
def call_bedrock(system_text: str, api_messages: list) -> str:
    body = {
        "messages": api_messages,
        "system": [{"text": system_text}],
        "inferenceConfig": {
            "maxTokens": 700,
            "temperature": 0.5,
            "topP": 0.9,
        },
    }

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response["body"].read())
    return result["output"]["message"]["content"][0]["text"]

# ──────────────────────────────────────────────
# Inicializar estado de sesión
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ──────────────────────────────────────────────
# UI – Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("Opciones")
    if st.button("Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("**Modos disponibles:**")
    st.markdown("- **Explicación**: Haz una pregunta conceptual")
    st.markdown("- **Examen**: Pide una pregunta de práctica")
    st.markdown("- **Corrección**: Responde A, B, C o D")

# ──────────────────────────────────────────────
# UI – Título
# ──────────────────────────────────────────────
st.title("☁️ Asistente AWS Cloud Practitioner")
st.caption("Preparación para el examen AWS Cloud Practitioner con IA")

# ──────────────────────────────────────────────
# Mostrar historial de mensajes
# ──────────────────────────────────────────────
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ──────────────────────────────────────────────
# Input del usuario
# ──────────────────────────────────────────────
if prompt := st.chat_input("Haz tu pregunta..."):
    # Agregar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # ── Detectar modo ──
    mode = detect_mode(prompt)

    # ── Construir historial de texto para el contexto ──
    recent_messages = st.session_state.messages[-6:]  # últimos 3 turnos completos
    history_text = ""
    for msg in recent_messages[:-1]:  # excluir el mensaje actual
        role_label = "Usuario" if msg["role"] == "user" else "Asistente"
        history_text += f"{role_label}: {msg['content']}\n"

    # ── Construir el contexto dinámico ──
    mode = detect_mode(prompt)

    context_prompt = build_context(
        topic="AWS Cloud Practitioner",
        history=history_text,
        user_input=prompt,
        mode=mode,
    )

    # ── Construir system prompt final con modo ──
    system_text = f"{SYSTEM_PROMPT}\n\nModo detectado: {mode}"

    # ── Construir lista de mensajes para la API (formato Nova) ──
    # Usamos el historial estructurado + el mensaje actual con contexto
    api_messages = []

    # Agregar historial previo como mensajes alternados (máx. 5 pares)
    history_for_api = st.session_state.messages[:-1]  # sin el mensaje actual
    history_for_api = history_for_api[-10:]            # máx. 10 mensajes (5 turnos)

    for msg in history_for_api:
        api_messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}],
        })

    # Agregar el mensaje actual enriquecido con contexto
    api_messages.append({
        "role": "user",
        "content": [{"text": context_prompt}],
    })

    # ── Llamar a Bedrock con spinner ──
    with st.spinner("Pensando..."):
        try:
            answer = call_bedrock(system_text, api_messages)
        except Exception as e:
            answer = f"❌ Error al conectar con Bedrock: {str(e)}"

    # ── Mostrar y guardar respuesta ──
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
