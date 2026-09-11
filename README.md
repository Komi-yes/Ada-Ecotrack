# EcoTrack 🌱

Prototipo (MVP) de EcoTrack: una app web donde el usuario describe su día en
lenguaje natural (ej. *"Hoy comí carne y viajé 20km en bus"*) y la app estima
su huella de carbono asociada.

Proyecto realizado como ejercicio de **Vibe Coding**: configuración de un
ecosistema de desarrollo asistido por IA (reglas de agente + despliegue en
la nube) y orquestación de agentes para pasar de una idea de alto nivel a un
prototipo funcional, sin escribir cada línea a mano.

## Scaffolding del proyecto

```
Ada-Ecotrack/
├── app.py                   # Interfaz Streamlit (única capa de presentación)
├── ecotrack/
│   ├── __init__.py           # Marca el paquete; vacío a propósito
│   └── parser.py             # Motor de estimación de CO2 (toda la lógica de negocio)
├── requirements.txt          # Única dependencia externa: streamlit
├── .replit                   # Config de ejecución/despliegue para Replit
├── .cursorrules              # Reglas de personalidad/estilo para el agente en Cursor
├── VIBE_REPORT.md            # Reflexión sobre el proceso de Vibe Coding
└── README.md                 # Este archivo
```

**Por qué esta estructura y no otra:**

- Se separó `app.py` (interfaz) de `ecotrack/parser.py` (lógica) para que la
  regla del `.cursorrules` de "no mezclar UI con lógica de negocio" sea
  verificable a simple vista: si alguien agrega un cálculo dentro de
  `app.py`, está rompiendo la convención del proyecto.
- Se armó como paquete Python (`ecotrack/`) en vez de un solo script para
  poder testear `estimate_co2()` de forma aislada (ver sección de pruebas
  manuales más abajo) sin tener que levantar Streamlit.
- No hay carpeta `tests/` todavía porque el MVP se validó con pruebas
  manuales por consola (ver más abajo); es lo primero que se agregaría en
  una siguiente iteración.
- Se eligió **Streamlit sobre Next.js** para este prototipo puntual porque
  el objetivo era validar la idea con el mínimo de piezas móviles: un solo
  proceso Python, sin build step, sin `package.json`, desplegable en
  Replit con un solo comando. El `.cursorrules` deja Next.js como alternativa
  explícita si el proyecto crece y necesita una UI más compleja.

## Detalle del código

### `ecotrack/parser.py` — el motor de estimación

Es un estimador **basado en reglas** (diccionarios de palabras clave +
regex), no una llamada a un LLM externo. Se decidió así para que el
prototipo funcione sin API keys ni costos de inferencia, algo importante
para un MVP que se quiere poder correr y compartir de inmediato.

Piezas del archivo:

- `FOOD_FACTORS: dict[str, float]` — mapea palabras clave de alimentos
  (`"carne"`, `"pollo"`, `"vegetales"`, etc.) a un factor de emisión en
  **kg de CO2e por porción**. Los valores son promedios simplificados
  (ej. carne roja ≈ 6.9 kg, pollo ≈ 1.1 kg, vegetales ≈ 0.3 kg), tomados de
  cifras divulgadas por estudios de huella de carbono (Our World in
  Data/IPCC) y redondeados para fines educativos, no para un reporte
  certificado.
- `TRANSPORT_FACTORS: dict[str, float]` — mapea modos de transporte
  (`"bus"`, `"auto"`, `"bici"`, `"avion"`, etc.) a un factor en
  **kg de CO2 por km recorrido** (ej. auto ≈ 0.192 kg/km, bus ≈ 0.105 kg/km,
  bici/caminando = 0 kg/km).
- `DISTANCE_PATTERN` — una regex (`\d+(?:[.,]\d+)?\s*(?:km|kms|kilometros|kilómetros)`)
  que extrae números seguidos de "km" o variantes, para asociarlos al modo
  de transporte detectado.
- `_strip_accents(text)` — normaliza tildes y la ñ antes de buscar palabras
  clave, para que "comí" y "comi" o "avión" y "avion" matcheen igual. Es
  necesario porque el texto del usuario puede venir con o sin acentos.
- `ItemEstimate` (dataclass) — representa un ítem detectado individual:
  etiqueta (`label`), categoría (`"comida"` o `"transporte"`), detalle
  legible (`"1 porción estimada"` o `"20 km"`) y el CO2 calculado
  (`co2_kg`).
- `EstimateResult` (dataclass) — acumula una lista de `ItemEstimate` y un
  `total_co2_kg` corriendo; expone `.add()` para sumar un ítem y actualizar
  el total en un solo paso.
- `estimate_co2(text: str) -> EstimateResult` — función pública principal:
  1. Normaliza el texto (minúsculas + sin acentos).
  2. Recorre `FOOD_FACTORS` y, por cada palabra clave que aparece como
     palabra completa (`\b...\b`, con o sin "s" al final para plurales),
     agrega un `ItemEstimate` de categoría `"comida"` asumiendo **una
     porción**.
  3. Extrae todas las distancias en km mencionadas en el texto con
     `DISTANCE_PATTERN`.
  4. Recorre `TRANSPORT_FACTORS` y, por cada modo detectado, le asigna la
     siguiente distancia disponible de la lista extraída (o `1.0 km` como
     valor por defecto si no hay ninguna distancia en el texto), calcula
     `factor * distancia` y agrega el `ItemEstimate` de categoría
     `"transporte"`.
  5. Devuelve el `EstimateResult` con el desglose completo y el total.

Limitación de diseño conocida (documentada en el propio código): si el
texto menciona dos modos de transporte y dos distancias, el emparejamiento
se hace por **orden de aparición en los diccionarios**, no por proximidad
textual real entre el modo y su distancia. Para el alcance del MVP (una
actividad de comida + una de transporte por frase) es suficiente.

### `app.py` — la interfaz

Contiene únicamente lógica de presentación de Streamlit, sin ningún cálculo
propio:

- `st.session_state.history` — lista en memoria de sesión que guarda cada
  `(texto_ingresado, EstimateResult)` para poder mostrar un historial sin
  necesidad de base de datos.
- Un `st.form` con `st.text_area` + botón de submit, para que la app solo
  reaccione cuando el usuario confirma el texto (evita recalcular en cada
  tecla).
- Al enviar, llama a `estimate_co2(text)` (única dependencia hacia
  `ecotrack/parser.py`) y guarda el resultado en el historial.
- Renderiza el total con `st.metric`, el desglose ítem por ítem con un
  ícono según la categoría (🍽️ comida / 🚗 transporte), y un
  `st.expander` con el historial de la sesión completa.
- Un pie de página (`st.caption`) aclara que las estimaciones son
  educativas, no un cálculo certificado — transparencia sobre la limitación
  del modelo de datos.

### `.cursorrules` — reglas del agente

Define, en este orden: el stack preferido (Streamlit para MVP, Next.js si
el proyecto escala), el estilo de código (modular, tipado, sin comentarios
redundantes), el flujo de trabajo esperado con el agente (pegar errores
completos en vez de corregir sintaxis a mano) y una regla de arquitectura
explícita: *todo cálculo de emisiones vive en `ecotrack/parser.py`*, nunca
en `app.py`. Esta última regla es la que mantiene separadas las dos capas
descriptas arriba.

### `.replit` — configuración de despliegue

Declara el comando de arranque (`streamlit run app.py --server.port 8080
--server.address 0.0.0.0`, necesario porque Replit expone la app por un
puerto fijo y una IP no-local), el canal de Nix (`stable-24_05`) para que
Replit resuelva el entorno de Python automáticamente a partir de
`requirements.txt`, y el mapeo de puertos (`8080` interno → `80` externo)
para que el deploy quede accesible por HTTP estándar.

## Cómo funciona (resumen)

- `ecotrack/parser.py`: motor de estimación. Detecta palabras clave de
  comida y transporte en el texto (y distancias en km) y aplica factores de
  emisión promedio (kg CO2e) por porción o por kilómetro.
- `app.py`: interfaz en Streamlit. Solo maneja la UI y el estado de sesión;
  toda la lógica de cálculo vive en `ecotrack/parser.py`.

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre en `http://localhost:8501`.

## Probar solo la lógica (sin levantar la UI)

```bash
python -c "
from ecotrack.parser import estimate_co2
r = estimate_co2('Hoy comí carne y viajé 20km en bus')
print(r.total_co2_kg)
for i in r.items:
    print(i)
"
```

Salida esperada: `9.0` (6.9 kg por la carne + 2.1 kg por 20 km en bus a
0.105 kg/km).

## Desplegar en Replit

1. Crear un nuevo Repl importando este repositorio (`Import from GitHub`).
2. Replit detecta `.replit` y `requirements.txt` automáticamente.
3. Presionar **Run** (o **Deploy** para una URL pública persistente).
4. La app queda accesible en la URL pública que asigna Replit.

## Ejemplos de entrada

| Texto | Desglose | CO2 estimado |
|---|---|---|
| "Hoy comí carne y viajé 20km en bus" | carne 6.9 kg + bus·20km 2.1 kg | ~9.0 kg |
| "Almorcé pollo y fui caminando" | pollo 1.1 kg + caminando 0 kg | ~1.1 kg |
| "Comí vegetales y viajé 5km en bici" | vegetales 0.3 kg + bici·5km 0 kg | ~0.3 kg |

## Limitaciones (MVP)

- Los factores de emisión son promedios simplificados con fines educativos,
  no un cálculo certificado.
- El parser es por palabras clave y regex (no usa un LLM externo), por lo
  que frases muy ambiguas, sinónimos no incluidos en los diccionarios, o
  redacciones fuera de español no se detectan.
- Si una frase menciona más de un alimento o más de un transporte, cada
  palabra clave detectada se cuenta como una porción/trayecto independiente
  (no hay deduplicación semántica más allá de evitar contar la misma
  palabra clave dos veces).
- El emparejamiento entre un modo de transporte y su distancia es por orden
  de aparición en los diccionarios internos, no por cercanía real en el
  texto (ver limitación documentada en `ecotrack/parser.py`).
