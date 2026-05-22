from django.db import models
import unicodedata
import re


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
    es_fabricable = models.BooleanField(default=False, help_text = "Marcar si este item se puede fabricar mediante receta" )

    def save(self, *args, **kwargs):
        # Normalizar nombre antes de guardar
        self.name = normalize_string(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    

def normalize_string(nombre):
    # Convertir a minúsculas y eliminar acentos
    nombre = unicodedata.normalize('NFKD',nombre).encode('ASCII','ignore').decode('ASCII')
    # Eliminar signos de puntuación y caracteres especiales (solo letras números y espacios
    nombre = re.sub(r'[^\w\s]', '', nombre)
    # Reemplazar múltiples espacios por uno solo
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    # Poner primera letra de cada palabra en mayúscula
    nombre = nombre.title()
    return nombre