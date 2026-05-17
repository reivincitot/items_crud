from django.core.exceptions import ValidationError
from .models import Recipe

def calcular_materiales(item_id, cantidad_deseada, visited=None):
    """
    Retorna dict {item_id: cantidad_total_necesaria} para ingredientes base.
    """
    if visited is None:
        visited = set()
    
    if item_id in visited:
        raise ValidationError(f"Ciclo detectado en receta del item {item_id}")
    visited.add(item_id)
    
    # Buscar si hay una receta que PRODUZCA este item
    try:
        receta = Recipe.objects.select_related('produced_item').prefetch_related('ingredients__item').get(produced_item_id=item_id)
    except Recipe.DoesNotExist:
        # No hay receta, es ingrediente base
        return {item_id: cantidad_deseada}
    
    materiales = {}
    for ing in receta.ingredients.all():
        # Esta receta produce 1 unidad del item, así que necesitamos 'cantidad_deseada' lotes
        cantidad_ing = ing.quantity * cantidad_deseada
        sub = calcular_materiales(ing.item_id, cantidad_ing, visited.copy())
        for k, v in sub.items():
            materiales[k] = materiales.get(k, 0) + v
    
    return materiales