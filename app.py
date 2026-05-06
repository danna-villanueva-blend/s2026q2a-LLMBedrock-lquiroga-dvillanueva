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

# Prompt base mejorado
SYSTEM_PROMPT = """
Eres un experto en AWS Cloud Practitioner.

Tu objetivo es ayudar a estudiantes a entender conceptos de cloud computing de forma clara, sencilla y práctica.

Reglas:
- Explica como profesor
- Usa ejemplos reales
- Responde en español
- Si es posible, usa analogías simples
"""

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("☁️ Asistente AWS Cloud Practitioner")

# Mostrar historial
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input usuario
if prompt := st.chat_input("Haz tu pregunta..."):

    # Guardar mensaje usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    #  Limitar historial (últimos 5 mensajes)
    recent_messages = st.session_state.messages[-5:]

    #  Formato correcto para Claude
    conversation = SYSTEM_PROMPT + "\n\n"

    for msg in recent_messages:
        if msg["role"] == "user":
            conversation += f"Human: {msg['content']}\n\n"
        else:
            conversation += f"Assistant: {msg['content']}\n\n"

    conversation += "Assistant:"

    # Llamada a Bedrock
    body = {
        "prompt": conversation,
        "max_tokens_to_sample": 150,  #  menos costo
        "temperature": 0.5
    }

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    answer = result.get("completion", "")

    # Guardar respuesta
    st.session_state.messages.append({"role": "assistant", "content": answer})

    st.chat_message("assistant").write(answer)
