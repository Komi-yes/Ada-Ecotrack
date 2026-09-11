# Vibe Report — EcoTrack

## Contexto real de esta ejecución

No tenía instalados Cursor ni Replit al momento de hacer este ejercicio, así
que en vez de simular el flujo, lo llevé a cabo con las herramientas que sí
tenía a mano: Claude Code como agente ejecutor directo sobre el repositorio,
y este mismo documento explica cómo replicarlo en Cursor + Replit para
cumplir el entregable tal como se pide.

## Cómo configuré las reglas del agente

El `.cursorrules` que dejé en la raíz del repo define tres cosas: el stack
preferido (Python + Streamlit para MVPs rápidos, Next.js si se necesita algo
más robusto), el estilo de código (modular, tipado, sin comentarios
redundantes) y el flujo de trabajo (no corregir sintaxis a mano, pegar el
error completo y dejar que el agente proponga el fix). La idea no fue
escribir reglas genéricas, sino codificar decisiones que ya había tomado
mentalmente sobre el proyecto, para no tener que repetirlas en cada prompt.

## Dificultades al delegar

La mayor dificultad no fue técnica sino de especificación: pedir "que la IA
calcule un estimado de CO2" es ambiguo si no se define de dónde salen los
factores de emisión. Tuve que tomar una decisión de diseño intermedia —usar
un parser basado en palabras clave con factores promedio, en vez de depender
de una API de LLM externa para el cálculo— porque eso hace que el prototipo
funcione sin claves de API ni costos, algo clave para un MVP que se quiere
probar rápido. Delegar bien no significa no decidir nada; significa decidir
el *qué* y dejar el *cómo* al agente.

Otra dificultad típica de este flujo (aunque acá no se manifestó como error)
es la tentación de revisar cada línea generada como si uno la hubiera
escrito. Vibe coding funciona cuando uno valida el resultado (¿la app calcula
bien? ¿la interfaz tiene sentido?) en vez de auditar cada decisión de
implementación menor.

## Cómo se siente orquestar en vez de escribir

Se siente como pasar de ser el que ejecuta a ser el que define criterios de
aceptación. En vez de pensar "¿cómo escribo un regex para detectar
distancias en km?", pensé "¿qué necesita ver el usuario para confiar en el
número que le muestro?". El trabajo se mueve hacia arriba en la pila: menos
sintaxis, más intención, más verificación de que el resultado final cumple
el vibe pedido. Es cómodo cuando el dominio es claro (como acá, un cálculo
determinístico); exige más disciplina cuando el problema es ambiguo, porque
ahí la calidad del resultado depende enteramente de qué tan bien se
especificó la intención.

## Entregables de este ejercicio

- Código funcional: `app.py`, `ecotrack/parser.py`, `requirements.txt`.
- `.cursorrules`: reglas del agente (ver raíz del repo).
- `.replit`: configuración de despliegue para Replit.
- Este documento.

Para completar la captura de pantalla "Cursor + Replit operando en
conjunto", el paso siguiente es: importar este repo en Replit desde GitHub,
correr `streamlit run app.py`, y abrir Cursor apuntando a la misma carpeta
para tomar la captura con ambos entornos activos.
