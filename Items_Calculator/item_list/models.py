from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        
class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Types"
        
class Subtype(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Subtypes"
        
class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='items')
    type = models.ForeignKey(Type, on_delete=models.PROTECT, related_name='items')
    subtype = models.ForeignKey(Subtype, on_delete=models.PROTECT, related_name='items', blank=True, null=True)

    def __str__(self):
        return self.name
    