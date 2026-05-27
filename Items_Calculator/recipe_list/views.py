from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Recipe, Ingredient
from .service import calcular_materiales_con_arbol
from .forms import RecipeForm
from item_list.models import Item

def home(request):
    ultima_receta = request.session.get('ultima_receta', None)
    return render(request, 'home.html', {'ultima_receta': ultima_receta})

def calcular(request):
    resultado = None
    arbol = None
    fabricar = None
    arbol_html = ''
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
            arbol_html = arbol_a_html(calculo['arbol'])
            resultado = resultado_base
        
        except Exception as e:
            resultado = {'error': str(e)}
    
    recetas = Recipe.objects.all().order_by('recipe_name')
    
    return render(request, 'recipes/calcular.html', {
        'recetas': recetas,
        'resultado': resultado,
        'fabricar': fabricar,
        'arbol_html': arbol_html
    })
    
def recipe_list(request):
    recipes = Recipe.objects.select_related('produced_item').all().order_by('recipe_name')
    ultima_receta = request.session.get('ultima_receta', None)
    return render(request, 'recipes/list.html', {'recipes': recipes, 
                                                'ultima_receta': ultima_receta
                                                })

def recipe_create(request):
    if request.method == 'POST':
        # Mejor procesar manualmente
        recipe_name = request.POST.get('recipe_name')
        produced_item_name = request.POST.get('produced_item_name')
        try:
            produced_item = Item.objects.get(name=produced_item_name, es_fabricable=True)
        except Item.DoesNotExist:
            messages.error(request, f'El item "{produced_item_name}" no existe o no es fabricable.')
            return redirect('recipe_create')
        # Crear receta
        try:
            recipe = Recipe(recipe_name=recipe_name, produced_item=produced_item)
            recipe.save()
            request.session['ultima_receta'] = recipe.recipe_name
        except IntegrityError:
            messages.error(request, 'Ya existe una receta con ese nombre.')
            return redirect('recipe_create')
        # Procesar ingredientes
        i = 0
        while f'ingredient_item_{i}' in request.POST:
            item_nombre = request.POST[f'ingredient_item_{i}'].strip()
            quantity = request.POST.get(f'ingredient_quantity_{i}')
            if item_nombre and quantity:
                try:
                    item = Item.objects.get(name=item_nombre)
                except Item.DoesNotExist:
                    messages.error(request, f'El ingrediente "{item_nombre}" no existe.')
                    # Opcional: eliminar la receta creada para evitar huérfanos
                    recipe.delete()
                    return redirect('recipe_create')
                Ingredient.objects.create(recipe=recipe, item=item, quantity=int(quantity))
            i += 1
        messages.success(request, 'Receta creada exitosamente.')
        return redirect('recipe_list')
    else:
        # GET: mostrar formulario
        fabricable_items = Item.objects.filter(es_fabricable=True).order_by('name')
        all_items = Item.objects.all().order_by('name')
        return render(request, 'recipes/create.html', {
            'fabricable_items': fabricable_items,
            'items': all_items,
        })
        
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/detail.html', {'recipe': recipe})

def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        recipe.recipe_name = request.POST['recipe_name']
        produced_item_name = request.POST.get('produced_item_name')
        try:
            produced_item = Item.objects.get(name=produced_item_name, es_fabricable=True)
        except Item.DoesNotExist:
            messages.error(request, f'El item "{produced_item_name}" no existe o no es fabricable.')
            return redirect('recipe_edit', pk=pk)
        recipe.produced_item = produced_item
        recipe.save()
        # Reemplazar ingredientes
        recipe.ingredients.all().delete()
        i = 0
        while f'ingredient_item_{i}' in request.POST:
            item_nombre = request.POST[f'ingredient_item_{i}'].strip()
            quantity = request.POST.get(f'ingredient_quantity_{i}')
            if item_nombre and quantity:
                try:
                    item = Item.objects.get(name=item_nombre)
                except Item.DoesNotExist:
                    messages.error(request, f'El ingrediente "{item_nombre}" no existe.')
                    return redirect('recipe_edit', pk=pk)
                Ingredient.objects.create(recipe=recipe, item=item, quantity=int(quantity))
            i += 1
        messages.success(request, 'Receta actualizada exitosamente.')
        return redirect('recipe_list')
    else:
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