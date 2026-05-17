from django.shortcuts import render
from .models import Recipe
from .service import calcular_materiales
from item_list.models import Item


def home(request):
    return render(request, 'recipe_list/home.html')

def calcular(request):
    resultado = None
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        cantidad = int(request.POST.get('cantidad', 1))
        receta = Recipe.objects.get(id=recipe_id)
        item_producido = receta.produced_item
        try:
            materiales = calcular_materiales(item_producido.id, cantidad)
            items = Item.objects.filter(id__in=materiales.keys())
            resultado = {item.name: materiales[item.id] for item in items}
        except Exception as e:
            resultado = {'error': str(e)}

    recetas = Recipe.objects.all()
    return render(request, 'recipe_list/calcular.html', {'recetas': recetas, 'resultado': resultado})
