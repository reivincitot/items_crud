from django.contrib import admin
from django.urls import path, include
from recipe_list import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('calcular/', views.calcular, name='calcular'),
]
