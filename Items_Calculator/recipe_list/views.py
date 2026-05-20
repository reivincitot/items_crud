from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, Ingredient
from .service import calcular_materiales
from .forms import RecipeForm, IngredientForm
from item_list.models import Item


def home(request):
    return render(request, 'home.html')

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
    return render(request, 'recipes/calcular.html', {'recetas': recetas, 'resultado': resultado})

def recipe_list(request):
    recipes = Recipe.objects.select_related('produced_item').all()
    return render(request, 'recipes/list.html', {'recipes': recipes})

def recipe_create(request):
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST)
        if recipe_form.is_valid():
            recipe = recipe_form.save()
            i=0
            while f'ingredient_item_{i}' in request.POST:
                item_id = request.POST[f'ingredient_item_{i}']
                quantity = request.POST[f'ingredient_quantity_{i}']
                if item_id and quantity:
                    Ingredient.objects.create(
                        recipe=recipe,
                        item_id=int(item_id),
                        quantity=int(quantity)
                    )
                i += 1
            return redirect('recipe_list')
    else:
        recipe_form = RecipeForm()
    items = Item.objects.all().order_by('name')
    return render(request, 'recipes/create.html', {
        'recipe_form': recipe_form,
        'items': items
        })
                    
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/detail.html', {'recipe': recipe})

def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.recipe_name = request.POST['recipe_name']
        recipe.produced_item_id = request.POST['produced_item']
        recipe.save()
        # Eliminar ingredientes existentes (para reemplazarlos por los nuevos del POST)
        recipe.ingredients.all().delete()
        # Procesar ingredientes dinámicos
        i = 0
        while f'ingredient_item_{i}' in request.POST:
            item_id = request.POST[f'ingredient_item_{i}']
            quantity = request.POST[f'ingredient_quantity_{i}']
            if item_id and quantity:
                Ingredient.objects.create(
                    recipe=recipe,
                    item_id=int(item_id),
                    quantity=int(quantity)
                )
            i += 1
        return redirect('recipe_list')
    items = Item.objects.all().order_by('name')
    return render(request, 'recipes/edit.html', {
        'recipe': recipe,
        'items': items,
    })
