from rest_framework import serializers
from .models import Category, Item, Stock_Transactions

class CategoryAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class AddItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'unit', 'description', 'current_stock']

class StockTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock_Transactions
        fields = ['name', 'type', 'quantity', 'notes']

class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.Name', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'category_name', 'current_stock']

class StockTransactionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock_Transactions
        fields = '__all__'