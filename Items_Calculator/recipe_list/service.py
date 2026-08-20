import math
from django.core.exceptions import ValidationError
from .models import Recipe

def calcular_materiales_con_arbol(item_id, cantidad_deseada, inventario=None, visited=None):
    """
    Devuelve diccionario con 'totales', 'base', 'arbol', 'fabricar'.
    Ahora considera `produces_quantity` de cada receta para calcular lotes.
    """
    if inventario is None:
        inventario = {}
    if visited is None:
        visited = set()

    if item_id in visited:
        raise ValidationError(f"Ciclo detectado en receta del item {item_id}")
    visited.add(item_id)

    try:
        receta = Recipe.objects.select_related('produced_item').prefetch_related('ingredients__item').get(produced_item_id=item_id)
        produces_quantity = receta.produces_quantity  # ← nuevo: rendimiento por lote
    except Recipe.DoesNotExist:
        # Item base: no tiene receta
        return {
            'totales': {item_id: cantidad_deseada},
            'base': {item_id: cantidad_deseada},
            'arbol': {},
            'fabricar': {}
        }

    # Calcular cuántos lotes se necesitan para obtener la cantidad deseada
    lotes = math.ceil(cantidad_deseada / produces_quantity)

    totales = {}
    base = {}
    fabricar = {}
    arbol_ingredientes = {}

    for ing in receta.ingredients.all():
        # Cantidad de este ingrediente necesaria para todos los lotes
        cantidad_ingrediente = ing.quantity * lotes
        sub = calcular_materiales_con_arbol(ing.item_id, cantidad_ingrediente, inventario, visited.copy())

        # Acumular totales
        for k, v in sub['totales'].items():
            totales[k] = totales.get(k, 0) + v
        for k, v in sub['base'].items():
            base[k] = base.get(k, 0) + v
        for k, v in sub['fabricar'].items():
            fabricar[k] = fabricar.get(k, 0) + v

        if sub['arbol']:
            fabricar[ing.item_id] = fabricar.get(ing.item_id, 0) + cantidad_ingrediente

        arbol_ingredientes[ing.item_id] = {
            'nombre': ing.item.name,
            'cantidad': cantidad_ingrediente,
            'cantidad_unitaria': ing.quantity,   # cantidad por lote
            'es_base': not sub['arbol'],
            'sub_receta': sub['arbol'] if sub['arbol'] else None,
            'lotes': lotes,                      # ← para mostrar en plantilla
            'produces_quantity': produces_quantity,
        }

    # Restar inventario
    for item_id, cant_inventario in inventario.items():
        if item_id in totales:
            restar = min(totales[item_id], cant_inventario)
            totales[item_id] -= restar
            if item_id in base:
                base[item_id] = max(0, base.get(item_id, 0) - restar)

    # Eliminar cantidades cero
    totales = {k: v for k, v in totales.items() if v > 0}
    base = {k: v for k, v in base.items() if v > 0}
    fabricar = {k: v for k, v in fabricar.items() if v > 0}

    # Árbol del producto principal
    arbol = {
        item_id: {
            'nombre': receta.produced_item.name,
            'cantidad': cantidad_deseada,
            'cantidad_unitaria': 1,
            'ingredientes': arbol_ingredientes,
            'lotes': lotes,
            'produces_quantity': produces_quantity,
        }
    }

    return {
        'totales': totales,
        'base': base,
        'arbol': arbol,
        'fabricar': fabricar
    }