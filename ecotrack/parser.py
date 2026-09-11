"""Estimador de huella de carbono a partir de texto en lenguaje natural.

[IA] Estructura y algoritmo generados a partir de la orquestación descrita
en PROMPTS.md ("que la IA calcule un estimado de CO2" a partir de una frase
como "Hoy comí carne y viajé 20km en bus"). Refinamiento humano: se decidió
un enfoque léxico (stemming + diccionario de factores) en vez de una API de
LLM externa, para que el prototipo no dependa de API keys ni costos de
inferencia. La primera versión usaba solo regex de plurales; se reemplazó
por stemming (NLTK, algoritmo Snowball para español) para cubrir
conjugaciones verbales y variaciones morfológicas ("comí", "comiendo",
"viajando", "buses") sin necesitar un modelo de lenguaje completo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from nltk.stem.snowball import SnowballStemmer

_stemmer = SnowballStemmer("spanish")

# Factores de emisión aproximados (kg CO2e). Fuente: promedios divulgados por
# estudios de huella de carbono (Our World in Data / IPCC) simplificados para
# fines educativos del prototipo, no para reporte oficial.
FOOD_FACTORS: dict[str, float] = {
    "carne": 6.9,
    "res": 6.9,
    "ternera": 6.9,
    "cerdo": 3.8,
    "pollo": 1.1,
    "pescado": 1.5,
    "atún": 1.5,
    "huevo": 0.4,
    "queso": 1.0,
    "leche": 0.6,
    "lácteos": 1.0,
    "arroz": 0.5,
    "vegetales": 0.3,
    "verduras": 0.3,
    "ensalada": 0.3,
    "fruta": 0.2,
    "vegetariano": 0.4,
    "vegano": 0.2,
}

TRANSPORT_FACTORS: dict[str, float] = {
    "auto": 0.192,
    "carro": 0.192,
    "coche": 0.192,
    "moto": 0.113,
    "motocicleta": 0.113,
    "bus": 0.105,
    "autobús": 0.105,
    "colectivo": 0.105,
    "tren": 0.041,
    "metro": 0.041,
    "subte": 0.041,
    "avión": 0.255,
    "vuelo": 0.255,
    "bicicleta": 0.0,
    "bici": 0.0,
    "caminando": 0.0,
    "caminata": 0.0,
    "pie": 0.0,
}

DISTANCE_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:km|kms|kilometros|kilómetros)", re.IGNORECASE
)

TOKEN_PATTERN = re.compile(r"[a-záéíóúñ]+", re.IGNORECASE)


def _build_stem_index(factors: dict[str, float]) -> dict[str, tuple[str, float]]:
    """Mapea el stem de cada palabra clave a (palabra original, factor).

    Se usa el stem en vez de la palabra literal para que coincidan
    variaciones morfológicas: "carne"/"carnes", "viajé"/"viajando", etc.
    """
    index: dict[str, tuple[str, float]] = {}
    for word, factor in factors.items():
        index[_stemmer.stem(word)] = (word, factor)
    return index


FOOD_STEM_INDEX = _build_stem_index(FOOD_FACTORS)
TRANSPORT_STEM_INDEX = _build_stem_index(TRANSPORT_FACTORS)


@dataclass
class ItemEstimate:
    label: str
    category: str  # "comida" | "transporte"
    detail: str
    co2_kg: float


@dataclass
class EstimateResult:
    total_co2_kg: float = 0.0
    items: list[ItemEstimate] = field(default_factory=list)

    def add(self, item: ItemEstimate) -> None:
        self.items.append(item)
        self.total_co2_kg += item.co2_kg


def estimate_co2(text: str) -> EstimateResult:
    """Analiza una frase en lenguaje natural y estima el CO2 asociado.

    Pipeline: tokenizar -> stemmizar cada token (NLTK Snowball español) ->
    buscar cada stem en los índices de comida/transporte -> emparejar
    transporte con distancias en km encontradas en el texto (por orden de
    aparición) -> acumular el resultado.
    """

    tokens = TOKEN_PATTERN.findall(text.lower())
    stems = [_stemmer.stem(token) for token in tokens]
    result = EstimateResult()

    seen_food: set[str] = set()
    for stem in stems:
        if stem in FOOD_STEM_INDEX and stem not in seen_food:
            word, factor = FOOD_STEM_INDEX[stem]
            seen_food.add(stem)
            result.add(
                ItemEstimate(
                    label=word.capitalize(),
                    category="comida",
                    detail="1 porción estimada",
                    co2_kg=round(factor, 2),
                )
            )

    distances = [float(m.group(1).replace(",", ".")) for m in DISTANCE_PATTERN.finditer(text.lower())]
    used_distance_idx = 0
    seen_transport: set[str] = set()
    for stem in stems:
        if stem in TRANSPORT_STEM_INDEX and stem not in seen_transport:
            word, factor = TRANSPORT_STEM_INDEX[stem]
            seen_transport.add(stem)
            distance_km = distances[used_distance_idx] if used_distance_idx < len(distances) else 1.0
            used_distance_idx += 1
            result.add(
                ItemEstimate(
                    label=word.capitalize(),
                    category="transporte",
                    detail=f"{distance_km:g} km",
                    co2_kg=round(factor * distance_km, 2),
                )
            )

    return result
