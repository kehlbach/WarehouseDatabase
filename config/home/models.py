from django.db import models

# Create your models here.

class Item_Category(models.Model):
    name = models.TextField(unique=True)
    def __str__(self):
        return f'{self.name}'

class Item(models.Model):
    vendor_code = models.TextField(unique=True)
    category = models.ForeignKey(Item_Category, on_delete=models.CASCADE)
    name = models.TextField(unique=True)
    units = models.TextField(default='шт')
    def __str__(self):
        return f'{self.vendor_code}:{self.name}'