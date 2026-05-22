from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Recipe, Ingredient
from .service import calcular_materiales
from .forms import RecipeForm
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
            try:
                recipe = recipe_form.save()
            except IntegrityError:
                messages.error(request, 'A recipe with this name already exists.')
                return render(request, 'recipes/create.html', {
                    'recipe_form': recipe_form,
                    'items': Item.objects.all().order_by('name'),
                })
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
    else:
        recipe_form = RecipeForm()
        recipe_form.fields['produced_item'].queryset = Item.objects.filter(es_fabricable=True)
    
    all_items = Item.objects.all().order_by('name')
    return render(request, 'recipes/create.html', {
        'recipe_form': recipe_form,
        'items': all_items,
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
        recipe.ingredients.all().delete()
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
    
    fabricable_items = Item.objects.filter(es_fabricable=True).order_by('name')
    all_items = Item.objects.all().order_by('name')
    return render(request, 'recipes/edit.html', {
        'recipe': recipe,
        'fabricable_items': fabricable_items,
        'all_items': all_items,
    })