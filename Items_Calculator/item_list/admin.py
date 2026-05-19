from django.contrib import admin
from .models import Item, Category, Type, Subtype

admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Type)
admin.site.register(Subtype)