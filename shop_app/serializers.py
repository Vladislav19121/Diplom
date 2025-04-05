from .models import *
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' 
        read_only_fields = ['user']

        
        
class OrderSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('status',) 

    def validate(self, data):
        product = data['product']
        quantity = data['quantity_product']

        if product.stock < quantity or quantity == 0:
            raise serializers.ValidationError("Недостаточно товара на складе")
        return data

    
    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity_product']
        price = product.price * quantity + 100
        validated_data['price'] = price  
        order = Order.objects.create(**validated_data)   
        return order 