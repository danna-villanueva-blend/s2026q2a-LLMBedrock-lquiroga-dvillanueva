# Asistente conversacional de AWS Cloud Practitioner

## Enfoque del asistente

Apoyar a estudiantes en la preparación para la certificación *AWS Cloud Practitioner*. El asistente ha sido diseñado como un instructor experto, su comportamiento está orientado a:
* Enseñar conceptos de forma clara y estructurada.
* Adaptarse al nivel del usuario.
* Simular escenarios reales de examen.
* Corregir y retroalimentar respuesta.

## Alcance del conocimiento

* Fundamentos de Cloud Computing.
* Modelos de despliegue.
* Serviciios principales de AWS.
  * EC2
  * S3
  * RDS
  * Lambda
  * VPC
* Seguridad.
* Facturación y costos.

## Prompts

El diseño del asistente se basa en dos componenetes principales:

### Prompt base (comportamiento)

* Rol del asistente
* Alcance del conocimiento
* Estilo de respuesta
* Reglas de comportamiento

### Prompt dinámico (contexto)

* Mantener historial de conversación
* Generar respuestas coherentes
* Simular memoria conversacional

## Modos de interacción

### Modo explicación

Explica conceptos con ejemplos.

### Modo examen

* Genera preguntas tipo AWS Cloud Practitioner
* Incluye opciones múltiples
* Evalúa respuestas de usuario

### Modo corrección

* Analiza respuestas
* Explica por qué son correctas o incorrectas


