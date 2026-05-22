from django import forms
from .models import Recipe, Ingredient


from django import forms
from .models import Recipe, Ingredient
from item_list.models import Item

from django import forms
from .models import Recipe
from item_list.models import Item

class RecipeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produced_item'].queryset = Item.objects.filter(es_fabricable=True)

    class Meta:
        model = Recipe
        fields = ['recipe_name', 'produced_item']
        
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['item', 'quantity']
        