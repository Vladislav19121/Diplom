from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

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

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254,
                             help_text='Введите свой email')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BuyingForm(forms.Form):
    name = forms.CharField(label='Ваше имя', max_length=100)
    address = forms.CharField(label='Адрес доставки', widget=forms.Textarea)
    quantity = forms.IntegerField(label='Количество', min_value=1)
    payment_method = forms.ChoiceField(label='Способ оплаты', choices=[
        ('cash', 'Наличными при получении'),
        ('card', 'Банковской картой'),
    ])
    comment = forms.CharField(max_length=100, required = False)

    def __init__(self, product, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.product = product

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity > self.product.stock:
            raise forms.ValidationError(f"На складе недостаточно товара. Доступно: {self.product.stock}")
        return quantity

