# Configuración del ecosistema de Vibe Coding

Este documento detalla, tal como pide la rúbrica del curso, cómo se
configuró el entorno de desarrollo impulsado por IA para este proyecto —
qué herramientas se usaron realmente, cuáles no estaban disponibles, y qué
se hizo en su lugar.

## Restricción de partida

El estudiante no tenía instalado Cursor ni una cuenta de Replit con acceso
previo. Cursor y Replit tienen planes gratuitos (con límites de uso), por
lo que la barrera no era estrictamente económica sino de tiempo/acceso al
momento de resolver el ejercicio. Ante esa restricción, se optó por
ejecutar el mismo flujo de Vibe Coding —orquestación de un agente de IA
sobre un repositorio real, con reglas de agente explícitas y artefactos de
despliegue listos— usando **Claude Code** como agente ejecutor directo
sobre el sistema de archivos y git, en vez de simular una herramienta que
no se tenía.

## Modelo de IA usado

El agente ejecutor de esta sesión corre sobre **Claude Sonnet 5**
(familia Claude, Anthropic), cumpliendo el requisito de la consigna de usar
un modelo de la clase "Claude 3.5 Sonnet o GPT-4o" como motor de Vibe
Coding — de hecho una generación posterior de la misma familia de modelos.

## Reglas de agente: `.cursorrules`

Aunque no se ejecutó dentro de la app de Cursor, el archivo `.cursorrules`
en la raíz del repo es real y funcional: cualquier instalación de Cursor
que abra este repositorio lo va a leer y aplicar automáticamente. Contiene:

- **Stack preferido**: Streamlit para MVP, Next.js si el proyecto escala
  (instrucción explícita para que el agente no proponga un framework
  distinto sin justificación).
- **Estilo de código**: modular, tipado, sin comentarios redundantes.
- **Flujo de trabajo**: no corregir sintaxis a mano, pegar el traceback
  completo y dejar que el agente proponga el fix — esta regla se siguió
  literalmente en esta sesión (ver `PROMPTS.md`, no hubo ni un caso donde
  el usuario editara código directamente).
- **Regla de arquitectura**: todo cálculo de emisiones vive en
  `ecotrack/parser.py`, nunca en `app.py` — verificable inspeccionando que
  `app.py` no contiene ningún factor de emisión ni lógica de cómputo.

## Configuración de despliegue: `.replit`

El archivo `.replit` define el comando de arranque, el canal de Nix
(`stable-24_05`) y el mapeo de puertos necesario para que, al importar este
repo en un Repl (plan gratuito), la app quede corriendo con un solo click
en "Run" — sin pasos de configuración manual adicionales. No se generó una
captura de pantalla de Replit porque no se llegó a importar el repo en la
plataforma durante esta sesión; el archivo de configuración queda como la
evidencia de que el entorno de despliegue fue diseñado, aunque no
ejecutado end-to-end en la nube.

## Qué se verificó realmente (evidencia de ejecución, no solo de diseño)

- La lógica de `ecotrack/parser.py` se ejecutó por consola contra frases de
  ejemplo antes de reportar cualquier avance como terminado.
- La app Streamlit se levantó en local (`streamlit run app.py`) y se
  confirmó que arrancaba sin errores.
- Se agregó una suite de tests automatizados (`tests/test_parser.py`) que
  corre con `pytest` y pasa (6/6) — ver `README.md`, sección "Cómo revisar
  este repositorio".

## Qué falta para el ecosistema completo (honesto, sin inflar)

- No hay captura de pantalla de Cursor ni de Replit operando, porque no se
  usaron esas herramientas puntuales. Si se requiere estrictamente esa
  evidencia, el siguiente paso es importar este repo en Replit (gratuito)
  y, si se dispone de acceso a Cursor, abrir la carpeta ahí para que lea el
  `.cursorrules` ya presente.
