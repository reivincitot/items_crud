from django import forms
from .models import Recipe, Ingredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['recipe_name', 'produced_item']
        
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['item', 'quantity']
        