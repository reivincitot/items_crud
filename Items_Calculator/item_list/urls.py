from django.urls import path
from . import views

app_name = 'item_list'
urlpatterns = [
    path('', views.item_list, name='list'),
    path('create/', views.item_create, name='create'),
    path('delete/<int:pk>/', views.item_delete, name='delete'),
]
