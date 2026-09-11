"""Estimador de huella de carbono a partir de texto en lenguaje natural.

Enfoque basado en reglas (keywords + regex) para no depender de una API
externa de pago: detecta menciones de comida y transporte en español y
aplica factores de emisión promedio (kg CO2e) por porción o por km.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

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
    "atun": 1.5,
    "huevo": 0.4,
    "huevos": 0.4,
    "queso": 1.0,
    "leche": 0.6,
    "lacteos": 1.0,
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
    "autobus": 0.105,
    "colectivo": 0.105,
    "tren": 0.041,
    "metro": 0.041,
    "subte": 0.041,
    "avion": 0.255,
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


def _strip_accents(text: str) -> str:
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n",
    }
    for accented, plain in replacements.items():
        text = text.replace(accented, plain)
    return text


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
    """Analiza una frase en lenguaje natural y estima el CO2 asociado."""

    normalized = _strip_accents(text.lower())
    result = EstimateResult()

    # 1. Comida: cualquier palabra clave mencionada suma una porción.
    seen_food: set[str] = set()
    for word, factor in FOOD_FACTORS.items():
        if word in seen_food:
            continue
        pattern = re.compile(rf"\b{re.escape(word)}s?\b")
        if pattern.search(normalized):
            seen_food.add(word)
            result.add(
                ItemEstimate(
                    label=word.capitalize(),
                    category="comida",
                    detail="1 porción estimada",
                    co2_kg=round(factor, 2),
                )
            )

    # 2. Transporte: se busca un modo de transporte y, cerca, una distancia.
    #    Si hay varias distancias en el texto pero un solo modo, se usa la
    #    primera distancia encontrada como aproximación del MVP.
    distances = [float(m.group(1).replace(",", ".")) for m in DISTANCE_PATTERN.finditer(normalized)]
    used_distance_idx = 0
    seen_transport: set[str] = set()
    for word, factor in TRANSPORT_FACTORS.items():
        if word in seen_transport:
            continue
        pattern = re.compile(rf"\b{re.escape(word)}\b")
        if pattern.search(normalized):
            seen_transport.add(word)
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
