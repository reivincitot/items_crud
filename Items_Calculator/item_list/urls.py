from django.urls import path
from . import views

app_name = 'item_list'
urlpatterns = [
    path('', views.item_list, name='list'),
    path('create/', views.item_create, name='create'),
    path('delete/<int:pk>/', views.item_delete, name='delete'),
    path('ajax/add_category/', views.ajax_add_category, name='ajax_add_category'),
    path('ajax/add_type/', views.ajax_add_type, name='ajax_add_type'),
    path('ajax/add_subtype/', views.ajax_add_subtype, name='ajax_add_subtype'),
    path('editar/<int:pk>/', views.item_edit, name='edit')
]
