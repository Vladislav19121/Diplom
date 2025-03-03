from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'city', 'price', 'image', 'category', 'stock', 'discount']
    
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

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254,
                             help_text='Введите свой email')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BuyingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity_product', 'address', 'tel_number', 'payment', 'comment']

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

