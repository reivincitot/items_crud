from django.contrib import admin
from django.urls import path, include
from recipe_list import views as recipe_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('calcular/', recipe_views.calcular, name='calcular'),
    path('', recipe_views.home, name='home'),
    path('items/', include('item_list.urls')),
    path('recetas/', include('recipe_list.urls')),
]