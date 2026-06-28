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
    recetas = Recipe.objects.all().order_by('recipe_name')
    arbol = None
    materiales_resumen = None
    items_con_receta = {}
    arbol_html = ''
    receta_principal = None
    cantidad = 1

    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        cantidad = int(request.POST.get('cantidad', 1))
        inventario_text = request.POST.get('inventario', '')
        inventario = {}

        # Parsear inventario
        for line in inventario_text.strip().split('\n'):
            if ':' in line:
                nombre, cant_str = line.split(':', 1)
                nombre = nombre.strip()
                try:
                    cant = int(cant_str.strip())
                except:
                    continue
                try:
                    item = Item.objects.get(name__iexact=nombre)
                    inventario[item.id] = inventario.get(item.id, 0) + cant
                except Item.DoesNotExist:
                    pass

        receta_principal = get_object_or_404(Recipe, pk=recipe_id)
        try:
            calculo = calcular_materiales_con_arbol(receta_principal.produced_item.id, cantidad, inventario)

            # --- Obtener todas las recetas de los items intermedios (para mostrar sub-recetas) ---
            items_con_receta = {}
            for item_id in calculo.get('fabricar', {}).keys():
                try:
                    receta_intermedia = Recipe.objects.select_related('produced_item').prefetch_related('ingredients__item').get(produced_item_id=item_id)
                    items_con_receta[item_id] = {
                        'nombre': receta_intermedia.produced_item.name,
                        'ingredientes': [(ing.item.name, ing.quantity) for ing in receta_intermedia.ingredients.all()]
                    }
                except Recipe.DoesNotExist:
                    pass

            # --- Construir lista de materiales totales (para el resumen final) ---
            items_totales = Item.objects.in_bulk(calculo['totales'].keys())
            materiales_resumen = []
            for item_id, cantidad_bruta in calculo['totales'].items():
                item = items_totales.get(item_id)
                if item:
                    inv = inventario.get(item_id, 0)
                    neto = max(0, cantidad_bruta - inv)
                    materiales_resumen.append({
                        'nombre': item.name,
                        'cantidad_bruta': cantidad_bruta,
                        'inventario': inv,
                        'cantidad_neta': neto,
                        'es_fabricable': item.es_fabricable
                    })
            # Ordenar: primero fabricables, luego base, alfabético
            materiales_resumen.sort(key=lambda x: (0 if x['es_fabricable'] else 1, x['nombre']))

            # --- Árbol HTML (para la vista jerárquica) ---
            arbol_html = arbol_a_html(calculo['arbol'])
            arbol = calculo['arbol']  # para el template

        except Exception as e:
            messages.error(request, f'Error en el cálculo: {str(e)}')

    # Contexto para el template
    context = {
        'recetas': recetas,
        'arbol': arbol,
        'materiales_resumen': materiales_resumen,
        'items_con_receta': items_con_receta,
        'arbol_html': arbol_html,
        'receta_principal': receta_principal,
        'cantidad': cantidad,
    }
    return render(request, 'recipes/calcular.html', context)

def recipe_list(request):
    recipes = Recipe.objects.select_related('produced_item').all().order_by('recipe_name')
    ultima_receta = request.session.get('ultima_receta', None)
    return render(request, 'recipes/list.html', {
        'recipes': recipes,
        'ultima_receta': ultima_receta
    })

def recipe_create(request):
    if request.method == 'POST':
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
                    recipe.delete()
                    return redirect('recipe_create')
                Ingredient.objects.create(recipe=recipe, item=item, quantity=int(quantity))
            i += 1
        messages.success(request, 'Receta creada exitosamente.')
        return redirect('recipe_list')
    else:
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
    """Convierte la estructura jerárquica del árbol en HTML anidado con números formateados."""
    if not arbol:
        return ''
    html = '<ul class="tree">'
    for item_id, data in arbol.items():
        nombre = data.get('nombre', 'Desconocido')
        cantidad = data.get('cantidad', 0)
        cantidad_formateada = f"{cantidad:,}".replace(',', '.')
        ingredientes = data.get('ingredientes', {})
        html += f'<li><strong>{nombre}</strong>: {cantidad_formateada}'
        if ingredientes:
            html += arbol_a_html(ingredientes)
        html += '</li>'
    html += '</ul>'
    return html