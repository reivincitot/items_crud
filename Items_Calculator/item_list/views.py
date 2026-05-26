from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Item, Category, Type, Subtype

def item_list(request):
    items = Item.objects.select_related('category', 'type', 'subtype').all().order_by('name')
    return render(request, 'items/list.html', {'items': items})

def item_create(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        type_id = request.POST.get('type')
        subtype_id = request.POST.get('subtype') or None
        es_fabricable = 'es_fabricable' in request.POST

        # Crear objeto Item (sin guardar aún)
        item = Item(
            name=name,
            category_id=category_id,
            type_id=type_id,
            subtype_id=subtype_id,
            es_fabricable=es_fabricable
        )
        try:
            item.save()
            messages.success(request, 'Item created successfully.')
            return redirect('item_list:list')
        except IntegrityError:
            messages.error(request, 'An item with this name already exists.')
            # Después del error, debemos recargar el formulario con los datos ingresados
            # y las listas de categorías, tipos, subtipos
            categories = Category.objects.all().order_by('name')
            types = Type.objects.all().order_by('name')
            subtypes = Subtype.objects.all().order_by('name')
            # Renderizar la plantilla con los datos del POST para que el usuario no los pierda
            return render(request, 'items/create.html', {
                'categories': categories,
                'types': types,
                'subtypes': subtypes,
                'form_data': request.POST,  # para repoblar campos (opcional)
            })
    else:
        # GET: mostrar formulario vacío
        categories = Category.objects.all().order_by('name')
        types = Type.objects.all().order_by('name')
        subtypes = Subtype.objects.all().order_by('name')
        return render(request, 'items/create.html', {
            'categories': categories,
            'types': types,
            'subtypes': subtypes,
        })

def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.name = request.POST['name']
        item.category_id = request.POST['category']
        item.type_id = request.POST['type']
        item.subtype_id = request.POST.get('subtype') or None
        item.es_fabricable = 'es_fabricable' in request.POST
        try:
            item.save()
            messages.success(request, 'Item updated successfully.')
            return redirect('item_list:list')
        except IntegrityError:
            messages.error(request, 'An item with this name already exists.')
            # Recargar las listas y mostrar el formulario de edición con los datos actuales del item
            categories = Category.objects.all().order_by('name')
            types = Type.objects.all().order_by('name')
            subtypes = Subtype.objects.all().order_by('name')
            return render(request, 'items/edit.html', {
                'item': item,  # el objeto original (no modificado porque no se guardó)
                'categories': categories,
                'types': types,
                'subtypes': subtypes,
            })
    else:
        categories = Category.objects.all().order_by('name')
        types = Type.objects.all().order_by('name')
        subtypes = Subtype.objects.all().order_by('name')
        return render(request, 'items/edit.html', {
            'item': item,
            'categories': categories,
            'types': types,
            'subtypes': subtypes,
        })

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list:list')
    return render(request, 'items/delete.html', {'item': item})

@csrf_exempt
def ajax_add_category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            cat, _ = Category.objects.get_or_create(name=name)
            return JsonResponse({'id': cat.id, 'name': cat.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def ajax_add_type(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            tipo, _ = Type.objects.get_or_create(name=name)
            return JsonResponse({'id': tipo.id, 'name': tipo.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def ajax_add_subtype(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            subt, _ = Subtype.objects.get_or_create(name=name)
            return JsonResponse({'id': subt.id, 'name': subt.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)