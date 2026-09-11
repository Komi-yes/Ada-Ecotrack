# Log de orquestación de IA

Este documento es la evidencia explícita que pidió la retroalimentación del
curso: qué instrucciones de alto nivel se le dieron al agente de IA en cada
paso, y qué produjo/decidió el agente en respuesta. No son prompts
inventados a posteriori — son la secuencia real de la sesión de trabajo con
el agente (Claude, usado como motor de Vibe Coding en lugar de Cursor, ver
`ECOSYSTEM.md` para el porqué).

---

### Prompt 1 — Arquitectura inicial

**Instrucción dada (resumen del prompt real):**
> "Realiza el ejercicio del Proyecto Integrador 'EcoTrack': una app donde el
> usuario escribe algo como 'Hoy comí carne y viajé 20km en bus' y la IA
> calcula un estimado de CO2. No tengo Cursor ni Replit instalados."

**Lo que decidió y generó el agente (sin especificación línea por línea del
usuario):**
- Elegir Streamlit sobre Next.js para minimizar piezas móviles en un MVP.
- Diseñar un motor de estimación por reglas (diccionarios de emisión +
  regex de distancia) en `ecotrack/parser.py`, separado de la UI (`app.py`),
  como decisión arquitectónica no pedida explícitamente pero necesaria para
  cumplir "código limpio y modular".
- Definir los factores de emisión (kg CO2e por porción/km) a partir de
  cifras públicas conocidas, sin que el usuario especificara ningún valor.
- Generar `.cursorrules`, `.replit`, `README.md` y `VIBE_REPORT.md` como
  artefactos de ecosistema, anticipando los entregables pedidos por la
  consigna sin que el usuario los enumerara uno por uno.
- Verificar el resultado ejecutando la lógica (`python -c "..."`) y
  levantando Streamlit en local antes de reportar éxito.

### Prompt 2 — Commit y despliegue simulado

**Instrucción dada:**
> "Haz el commit, aunque no tengo Cursor ni Replit porque son de pago y no
> tengo acceso a ellas, así que quiero que lo simules."

**Lo que decidió el agente:**
- Rechazar fabricar capturas de pantalla falsas de Cursor/Replit (evidencia
  inventada), y en su lugar documentar honestamente en `VIBE_REPORT.md` que
  se usó Claude Code como agente ejecutor sustituto.
- Señalar que Replit tiene un plan gratuito suficiente para este MVP,
  corrigiendo la premisa de que "son de pago" es un bloqueante real.
- Redactar el mensaje de commit siguiendo la convención del repo.

### Prompt 3 — Push

**Instrucción dada:** "Sí, haz el push."

**Lo que hizo el agente:** `git push` del commit ya preparado, sin cambios
adicionales de código (instrucción puramente operativa).

### Prompt 4 — Profundizar el README

**Instrucción dada:**
> "¿Podrías hacer el README más específico con lo realizado y decir todo el
> detalle de scaffolding y detalles del código? Y posteriormente commitear y
> pushear."

**Lo que generó el agente:**
- Una sección de scaffolding que explica el *por qué* de cada carpeta/archivo
  (no solo qué es cada uno).
- Un walkthrough línea por línea de `parser.py` y `app.py`, incluyendo las
  limitaciones de diseño conocidas (ej. emparejamiento transporte-distancia
  por orden de aparición, no por cercanía textual).
- Commit y push, sin que el usuario tuviera que redactar nada del contenido.

### Prompt 5 — Retroalimentación del curso

**Instrucción dada:** el usuario pegó la evaluación del curso (52/100),
señalando falta de evidencia de orquestación y una implementación "basada
en palabras clave" demasiado simple, y pidió mejorar la implementación y el
entregable, además de instrucciones de cómo revisar el repo completo.

**Lo que decidió y generó el agente:**
- Señalar explícitamente al usuario que la retroalimentación menciona
  tecnologías (FastAPI, spaCy, scikit-learn) ausentes del repo real —
  posible error de evaluación sobre otro artefacto — en vez de fingir que
  esas tecnologías siempre estuvieron.
- Reemplazar el matching por palabra exacta/regex de plurales por
  **stemming en español (NLTK, algoritmo Snowball)**, para cubrir
  conjugaciones verbales y plurales irregulares (ej. "buses", "comiendo")
  que la versión anterior no detectaba. Verificado con un caso de prueba
  específico (`test_stemming_cubre_conjugaciones_y_plurales`).
- Agregar una suite de tests automatizados (`tests/test_parser.py`, 6 casos)
  como evidencia de verificación, donde antes solo había pruebas manuales
  por consola.
- Crear este mismo archivo (`PROMPTS.md`) y `ECOSYSTEM.md` como evidencia
  explícita de configuración de ecosistema y orquestación.
- Agregar una guía de revisión ordenada al `README.md` para que el
  evaluador sepa exactamente qué archivos mirar y en qué secuencia.

---

## Patrón observado en los 5 prompts

En ningún caso el usuario especificó estructuras de datos, algoritmos,
nombres de función o líneas de código. Cada prompt fue una intención de
producto o de proceso ("que calcule CO2", "simulalo", "hazlo más
detallado", "mejora esto"); las decisiones de implementación (Streamlit vs.
Next.js, dataclasses vs. dicts sueltos, regex vs. stemming, dónde separar
capas) las tomó el agente y quedaron documentadas para que sean auditables
después, no solo confiables "porque la IA lo dijo".
