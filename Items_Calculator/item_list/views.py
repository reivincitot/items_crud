from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Category, Type, Subtype
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Type, Subtype
import json

@csrf_exempt
def ajax_add_category(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            cat, created = Category.objects.get_or_create(name=name)
            return JsonResponse({'id': cat.id, 'name': cat.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def ajax_add_type(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            tipo, created = Type.objects.get_or_create(name=name)
            return JsonResponse({'id': tipo.id, 'name': tipo.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def ajax_add_subtype(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            subt, created = Subtype.objects.get_or_create(name=name)
            return JsonResponse({'id': subt.id, 'name': subt.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def item_list(request):
    items = Item.objects.select_related('category', 'type', 'subtype').all().order_by('name')
    return render(request, 'items/list.html', {'items': items})

def item_create(request):
    if request.method == 'POST':
        item = Item(
            name=request.POST['name'],
            category_id=request.POST['category'],
            type_id=request.POST['type'],
            subtype_id=request.POST.get('subtype', '')
        )
        item.save()
        return redirect('item_list:list')
    categories = Category.objects.all()
    types = Type.objects.all()
    subtypes = Subtype.objects.all()
    return render(request, 'items/create.html', {
        'categories': categories,
        'types': types,
        'subtypes': subtypes
    })

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list:list')
    return render(request, 'items/delete.html', {'item': item})

def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.name = request.POST['name']
        item.category_id = request.POST['category']
        item.type_id = request.POST['type']
        item.subtype_id = request.POST.get('subtype') or None
        item.save()
        return redirect('item_list:list')
    categories = Category.objects.all()
    types = Type.objects.all()
    subtypes = Subtype.objects.all()
    return render(request, 'items/edit.html', {
        'item': item,
        'categories': categories,
        'types': types,
        'subtypes': subtypes
    })
