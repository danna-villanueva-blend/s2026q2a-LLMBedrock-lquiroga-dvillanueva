import streamlit as st
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Config AWS
region = os.getenv("AWS_REGION")
model_id = os.getenv("MODEL_ID")

bedrock = boto3.client("bedrock-runtime", region_name=region)

#  Leer prompts desde archivos
def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = load_prompt("prompts/comportamiento.txt")
CONTEXT_TEMPLATE = load_prompt("prompts/contexto.txt")

#  Construir contexto dinámico
def build_context(topic, history, user_input):
    return CONTEXT_TEMPLATE.format(
        topic=topic,
        history=history,
        user_input=user_input
    )

#  Detectar modo (bonus)
def detect_mode(user_input):
    text = user_input.lower().strip()

    if "pregunta" in text or "quiz" in text:
        return "EXAMEN"
    elif text in ["a", "b", "c", "d"]:
        return "CORRECCIÓN"
    else:
        return "EXPLICACIÓN"

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("☁️ Asistente AWS Cloud Practitioner")

# Mostrar historial
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input usuario
if prompt := st.chat_input("Haz tu pregunta..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    #  Limitar historial (evita costos altos)
    recent_messages = st.session_state.messages[-5:]

    history_text = ""
    for msg in recent_messages:
        history_text += f"{msg['role']}: {msg['content']}\n"

    #  Contexto dinámico
    context_prompt = build_context(
        topic="AWS Cloud Practitioner",
        history=history_text,
        user_input=prompt
    )

    #  Detectar modo
    mode = detect_mode(prompt)

    #  Construcción final para Claude
    conversation = f"""
{SYSTEM_PROMPT}

Modo sugerido: {mode}

Human:
{context_prompt}

Assistant:
"""

    # Llamada a Bedrock
    body = {
        "prompt": conversation,
        "max_tokens_to_sample": 150,
        "temperature": 0.5
    }

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    answer = result.get("completion", "")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
