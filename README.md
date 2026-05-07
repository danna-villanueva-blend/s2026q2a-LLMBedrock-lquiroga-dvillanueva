# Asistente conversacional de AWS Cloud Practitioner - CloudMentor

## Enfoque del asistente

Apoyar a estudiantes en la preparación para la certificación *AWS Cloud Practitioner*. El asistente ha sido diseñado como un instructor experto, su comportamiento está orientado a:
* Enseñar conceptos de forma clara y estructurada.
* Adaptarse al nivel del usuario.
* Simular escenarios reales de examen.
* Corregir y retroalimentar respuesta.

## Elección del modelo: Amazon Nova Lite

El asistente usa amazon.nova-lite-v1:0. Esta decisión responde a tres criterios:
1. Ajuste al caso de uso
Nova Lite es un modelo multimodal de bajo costo y latencia optimizada para tareas de razonamiento conversacional. Para un asistente de estudio donde las respuestas son estructuradas y de longitud moderada (< 700 tokens), Nova Lite ofrece el equilibrio correcto entre calidad y velocidad.
2. Costo
Nova Lite tiene uno de los precios más bajos dentro de los modelos disponibles en Bedrock. En un contexto educativo donde el volumen de consultas puede ser alto, esto es determinante para la viabilidad del proyecto.
3. Integración nativa con Bedrock
Al ser un modelo de AWS, Nova Lite se integra directamente con bedrock-runtime sin necesidad de adaptadores adicionales. Usa el formato de mensajes estándar de la API (messages + system), lo que simplifica el código y la gestión del contexto conversacional.

## Prompts

Combina un sistema de prompts estructurado con detección automática de modo para adaptarse al momento del aprendizaje: explicar, examinar o corregir. El diseño del asistente se basa en dos componentes principales:

### Prompt base (comportamiento)

Define quién es el asistente y cómo debe actuar.

* Rol con nombre propio ("CloudMentor"): Anclar la identidad del asistente mejora la coherencia del estilo de respuesta a lo largo de la sesión.
* Dominios basados en el examen CLF-C02 oficial: El examen real distribuye preguntas por dominios con pesos distintos (Seguridad 30%, Tecnología 34%). El prompt refleja esta distribución para que el asistente enfatice lo que más importa.
* Límite de 250 palabras en modo EXPLICACIÓN: Evita respuestas que abrumen al estudiante. El aprendizaje por chunks cortos es más efectivo para retención.
* Regla de no responder fuera del alcance CLF-C02: Previene que el modelo derive hacia temas de certificaciones avanzadas (SAA, DevOps), que confundirían al estudiante.
* Instrucción de corregir errores con amabilidad: El modelo puede detectar malentendidos en el historial y reforzarlos, actuando como un tutor que adapta su enfoque.

### Prompt dinámico (contexto)

Se construye en tiempo de ejecución para cada mensaje. Incluye el tema activo, el modo detectado, el historial reciente y el mensaje del usuario.

* Incluir {mode} en el contexto: El modelo recibe confirmación explícita del modo activo, reduciendo ambigüedad en la respuesta esperada.
* Historial como texto plano en el contexto: Sirve como resumen semántico del hilo. Complementa el historial estructurado en messages para que el modelo tenga dos capas de contexto.
* Instrucción de generar preguntas diferentes al historial: Evita que el modo EXAMEN repita la misma pregunta en una misma sesión.
* Instrucción de evaluar con base en la última pregunta del historial: En modo CORRECCIÓN, ancla la evaluación a la pregunta más reciente, evitando que el modelo evalúe sobre una pregunta diferente.

## Modos de interacción

### Modo explicación

Explica conceptos con ejemplos.

Trigger: Cualquier pregunta conceptual (¿Qué es...?, ¿Cómo funciona...?, Explícame...)

### Modo examen

* Solo una opción correcta
* Las opciones incorrectas deben ser plausibles (no obvias)
* Las preguntas evalúan comprensión, no memorización
* No se revela la respuesta hasta que el usuario responda

Trigger: Palabras clave como pregunta, quiz, examen, practica

### Modo corrección

* Analiza respuestas
* Explica por qué son correctas o incorrectas

Trigger: El usuario responde con a, b, c o d

## Estructura del proyecto
aws-cloud-practitioner-assistant/
├── app.py                  # Aplicación principal
├── prompts/
│   ├── comportamiento      # Prompt de sistema (estático)
│   └── contexto            # Plantilla de contexto dinámico
├── .env                    
└── README.md
