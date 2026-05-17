from django.db import models
from item_list.models import Item


class Recipe(models.Model):
    recipe_name = models.CharField(max_length=100)
    produced_item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name='recipe')

    def __str__(self):
        return self.recipe_name
    
class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('recipe', 'item')

    def __str__(self):
        return f"{self.quantity} x {self.item.name} for {self.recipe.recipe_name}"