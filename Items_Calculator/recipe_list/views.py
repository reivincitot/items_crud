from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Recipe, Ingredient
from .service import calcular_materiales_con_arbol
from .forms import RecipeForm
from item_list.models import Item

def home(request):
    return render(request, 'home.html')

def calcular(request):
    resultado = None
    arbol = None
    fabricar = None
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        cantidad = int(request.POST.get('cantidad', 1))
        inventario_text = request.POST.get('inventario', '')
        inventario = {}
        # Parsear el inventario formato "nombre_item:cantidad" por linea
        for line in inventario_text.strip().split('\n'):
            if ':' in line:
                nombre, cant_str = line.split(':', 1)
                nombre = nombre.strip()
                try:
                    cant = int(cant_str.strip())
                except:
                    continue
                # Buscar item por nombre (exacto, normalizado)
                try:
                    item = Item.objects.get(name__iexact=nombre)
                    inventario[item.id] = inventario.get(item.id, 0) + cant
                except Item.DoesNotExist:
                    pass  # Ignorar nombres no encontrados

        receta = get_object_or_404(Recipe, pk=recipe_id)
        try:
            calculo = calcular_materiales_con_arbol(receta.produced_item.id, cantidad, inventario)
            # Convertir IDs a nombres para mostrar
            items = Item.objects.in_bulk(calculo['base'].keys())
            resultado_base = {items[item_id].name: cant for item_id, cant in calculo['base'].items() if item_id in items}
            # Estructura para fabricar (subproductos)
            items_fabricar = Item.objects.in_bulk(calculo['fabricar'].keys())
            fabricar = {items_fabricar[item_id].name: cant for item_id, cant in calculo['fabricar'].items() if item_id in items_fabricar}
            # Árbol jerárquico (podemos pasarlo a la plantilla como JSON)
            arbol = calculo['arbol']
            resultado = resultado_base
        except Exception as e:
            resultado = {'error': str(e)}
    recetas = Recipe.objects.all()
    arbol_html = arbol_a_html(calculo['arbol']) if calculo.get('arbol') else ''
    return render(request, 'recipes/calcular.html', {
        'recetas': recetas,
        'resultado': resultado,
        'fabricar': fabricar,
        'arbol_html': arbol_html
    })
    

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
    
def arbol_a_html(arbol):
    """Convierte la estructura jerárquica del árbol en HTML anidado."""
    if not arbol:
        return ''
    html = '<ul class="tree">'
    for item_id, data in arbol.items():
        nombre = data.get('nombre', 'Desconocido')
        cantidad = data.get('cantidad', 0)
        ingredientes = data.get('ingredientes', {})
        html += f'<li><strong>{nombre}</strong>: {cantidad}'
        if ingredientes:
            html += arbol_a_html(ingredientes)
        html += '</li>'
    html += '</ul>'
    return html