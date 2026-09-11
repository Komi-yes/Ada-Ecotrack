# EcoTrack 🌱

Prototipo (MVP) de EcoTrack: una app web donde el usuario describe su día en
lenguaje natural (ej. *"Hoy comí carne y viajé 20km en bus"*) y la app estima
su huella de carbono asociada.

Proyecto realizado como ejercicio de **Vibe Coding**: configuración de un
ecosistema Cursor + Replit y orquestación de agentes de IA para pasar de una
idea de alto nivel a un prototipo funcional.

## Cómo funciona

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

## Desplegar en Replit

1. Crear un nuevo Repl importando este repositorio (`Import from GitHub`).
2. Replit detecta `.replit` y `requirements.txt` automáticamente.
3. Presionar **Run** (o **Deploy** para una URL pública persistente).
4. La app queda accesible en la URL pública que asigna Replit.

## Ejemplos de entrada

| Texto | CO2 estimado |
|---|---|
| "Hoy comí carne y viajé 20km en bus" | ~9.0 kg |
| "Almorcé pollo y fui caminando" | ~1.1 kg |
| "Comí vegetales y viajé 5km en bici" | ~0.3 kg |

## Estructura

```
app.py                  # Interfaz Streamlit
ecotrack/parser.py       # Lógica de estimación de CO2
requirements.txt        # Dependencias
.replit                 # Config de despliegue en Replit
.cursorrules            # Reglas del agente de IA en Cursor
VIBE_REPORT.md           # Reflexión sobre el proceso de Vibe Coding
```

## Limitaciones (MVP)

Los factores de emisión son promedios simplificados con fines educativos,
no un cálculo certificado. El parser es por palabras clave (no usa un LLM
externo), por lo que frases muy ambiguas o fuera de las palabras clave
soportadas no se detectan.
