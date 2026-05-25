from django.db import models


class Product(models.Model):
    """Inventory product model."""
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=300)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_color = models.CharField(max_length=7, default='#6366f1', help_text='Hex color for placeholder image')
    image_icon = models.CharField(max_length=50, default='box', help_text='Icon name for placeholder')
    category = models.CharField(max_length=100, default='General')
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title





class Item(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)
    image = models.URLField(max_length=500, blank=True, null=True)
    in_stock = models.BooleanField(default=True)  # ADD THIS
    
    def __str__(self):
        return self.title
