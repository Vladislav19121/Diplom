from django.db import models
from django.contrib.auth.models import User
from pathlib import Path
from django.urls import reverse

BASE_DIR = Path(__file__).resolve().parent.parent

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение категории")   
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL, verbose_name="Родительская категория")
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название товара')
    description = models.TextField(blank=True, verbose_name="Описание товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tel_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    image = models.ImageField(upload_to='products/',  blank=True, null=True, verbose_name="Изображение товара")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0, verbose_name="Количество")
    is_available = models.BooleanField(default=True, verbose_name="В наличии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def discounted_price(self):
        return self.price * (1 - self.discount)
    
    def discount_percent(self):
        return self.discount * 100
    
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart', verbose_name="Продукт из корзины")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.quantity} товаров в корзине'

    def total_price(self):
        return self.quantity * self.product.price
    
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order', verbose_name='Продукт для заказа')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity_product = models.PositiveIntegerField(verbose_name="Количество товара")
    address = models.TextField()
    tel_number = models.CharField(verbose_name='Номер телефона', max_length=20)

    PAYMENT_METHODS = (
        ('cash', 'Наличными при получении'),
        ('card', 'Банковской картой'),
    )

    STATUS_CHOICES = (
        ('queue', 'Ваш заказ в очереди'),
        ('on_the_way', 'Заказ уже на пути к вам'),
        ('arrived', 'Курьер приехал, готов отдать заказ'),
    )

    status = models.CharField(verbose_name='Статус заказа', choices = STATUS_CHOICES, default='queue', max_length=150)
    payment = models.CharField(verbose_name='Способ оплаты', choices=PAYMENT_METHODS, default='cash', max_length=100)
    comment = models.CharField(max_length=255, verbose_name='Комментарий к заказу')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['id']
    
    def __str__(self):
        return f"Заказ #{self.pk} - {self.product.name} ({self.quantity_product})"
    
    def total_price(self):
        return self.price