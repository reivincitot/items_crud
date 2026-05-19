from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Category, Type, Subtype


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
