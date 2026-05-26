from django.core.exceptions import ValidationError
from .models import Recipe

def calcular_materiales_con_arbol(item_id, cantidad_deseada, inventario=None, visited=None):
    """
    Devuelve un diccionario con:
    - 'totales': {item_id: cantidad_necesaria} para todos los items (base e intermedios)
    - 'base': {item_id: cantidad_necesaria} solo items base (sin receta)
    - 'arbol': estructura jerárquica de la receta
    - 'fabricar': {item_id: cantidad_a_fabricar} para items con receta (excluyendo el item final)
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
    except Recipe.DoesNotExist:
        # Item base: no tiene receta
        return {
            'totales': {item_id: cantidad_deseada},
            'base': {item_id: cantidad_deseada},
            'arbol': {item_id: {'nombre': None, 'cantidad': cantidad_deseada, 'ingredientes': {}}},
            'fabricar': {}
        }

    # Procesar ingredientes de la receta
    totales = {}
    base = {}
    fabricar = {}
    arbol_ingredientes = {}

    for ing in receta.ingredients.all():
        sub = calcular_materiales_con_arbol(ing.item_id, ing.quantity * cantidad_deseada, inventario, visited.copy())
        # Acumular totales
        for k, v in sub['totales'].items():
            totales[k] = totales.get(k, 0) + v
        for k, v in sub['base'].items():
            base[k] = base.get(k, 0) + v
        for k, v in sub['fabricar'].items():
            fabricar[k] = fabricar.get(k, 0) + v
        arbol_ingredientes[ing.item_id] = {
            'nombre': ing.item.name,
            'cantidad': ing.quantity * cantidad_deseada,
            'es_base': not sub['arbol'],
            'ingredientes': sub['arbol'].get(ing.item_id, {}).get('ingredientes', {}) if sub['arbol'] else {}
        }
        # Si el ingrediente tiene receta, añadirlo a fabricar
        if sub['arbol']:
            fabricar[ing.item_id] = fabricar.get(ing.item_id, 0) + ing.quantity * cantidad_deseada

    # Restar inventario de los totales (solo para items base? mejor restar de todos)
    # Aplicamos inventario restando de totales y base (pero sin dejar cantidades negativas)
    for item_id, cant_inventario in inventario.items():
        if item_id in totales:
            restar = min(totales[item_id], cant_inventario)
            totales[item_id] -= restar
            if item_id in base:
                base[item_id] = max(0, base.get(item_id, 0) - restar)
            if restar > 0:
                # También reducir en el árbol? Por simplicidad, no modificamos el árbol visual.
                pass

    # Eliminar items con cantidad 0
    totales = {k: v for k, v in totales.items() if v > 0}
    base = {k: v for k, v in base.items() if v > 0}
    fabricar = {k: v for k, v in fabricar.items() if v > 0}

    arbol = {
        item_id: {
            'nombre': receta.produced_item.name,
            'cantidad': cantidad_deseada,
            'ingredientes': arbol_ingredientes
        }
    }

    return {
        'totales': totales,
        'base': base,
        'arbol': arbol,
        'fabricar': fabricar
    }