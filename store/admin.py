from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'in_stock', 'created_at')
    list_filter = ('category', 'in_stock')
    search_fields = ('title', 'description')
