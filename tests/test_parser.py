from ecotrack.parser import estimate_co2


def test_carne_y_bus_ejemplo_del_readme():
    result = estimate_co2("Hoy comí carne y viajé 20km en bus")
    assert result.total_co2_kg == 9.0
    labels = {item.label for item in result.items}
    assert labels == {"Carne", "Bus"}


def test_pollo_y_caminando_sin_distancia_explicita():
    result = estimate_co2("Almorcé pollo y fui caminando")
    assert result.total_co2_kg == 1.1


def test_vegetales_y_bici_no_emiten_por_transporte():
    result = estimate_co2("Comí vegetales y viajé 5km en bici")
    bici_item = next(item for item in result.items if item.label == "Bici")
    assert bici_item.co2_kg == 0.0


def test_stemming_cubre_conjugaciones_y_plurales():
    """Antes de introducir stemming, 'buses' y 'comiendo' no se detectaban."""
    result = estimate_co2("Estuve comiendo carnes y viajando 15 km en buses")
    labels = {item.label for item in result.items}
    assert labels == {"Carne", "Bus"}
    assert result.total_co2_kg == 8.47


def test_texto_sin_palabras_clave_no_suma_nada():
    result = estimate_co2("Hoy fue un día tranquilo de trabajo")
    assert result.total_co2_kg == 0.0
    assert result.items == []


def test_multiples_alimentos_se_acumulan():
    result = estimate_co2("Comí pollo, queso y una ensalada")
    labels = {item.label for item in result.items}
    assert labels == {"Pollo", "Queso", "Ensalada"}
