from django import forms
from .models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'stock', 'discount']
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'parent']

class DiscountForm(forms.Form):
    discount = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        label="Скидка"
    )