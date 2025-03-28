from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
import phonenumbers

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'city', 'price', 'image', 'category', 'stock', 'discount']
        widgets = {
            'discount': forms.NumberInput(attrs=({'placeholder': 'Введите скидку в процентах (0-100)'}))
        }
    def clean_price(self):
        price = self.cleaned_data['price']

        if price <= 0:
            raise forms.ValidationError("Цена должна быть положительной")
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data['stock']

        if stock <= 0:
            raise forms.ValidationError("Количество не может быть равно или меньше нуля")    
        return stock
    
    def clean_discount(self):
        discount = self.cleaned_data['discount']

        if not 0 <= discount <= 100:
            raise forms.ValidationError("Скидка должна находиться в диапозоне от 0 до 100")
        return discount
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'parent']

class DiscountForm(forms.Form):
    discount = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        label="Скидка",
        widget=forms.NumberInput(attrs={'placeholder': 'Введите скидку в процентах (0-100)'})
    )

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        if not (0 <= discount <= 100):
            raise forms.ValidationError("Скидка должна быть в диапазоне от 0 до 100 процентов.")
        return discount
    
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254,
                             help_text='Введите свой email')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError("Пользователь с таким email уже существует")
    #     return email

class BuyingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity_product', 'address', 'tel_number', 'payment', 'comment']

    def clean_tel_number(self):
        tel_number = self.cleaned_data['tel_number']
        if not tel_number:
            raise forms.ValidationError("Укажите номер телефона")
        if not tel_number.startswith('+'):
            raise forms.ValidationError("Номер телефона должен начинаться с '+'")
        
        try:
            parsed_number = phonenumbers.parse(tel_number, "BY")

            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError("Неверный формат номера телефона для Беларуси.")
        except Exception as e:
            raise forms.ValidationError(f"Ошибка при указании номера телефона: {e}")
        
        return tel_number
       

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

