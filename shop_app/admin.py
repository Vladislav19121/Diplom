from django.contrib import admin

from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'parent')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'price', 'user', 'stock')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'quantity')