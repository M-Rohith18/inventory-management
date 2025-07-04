from rest_framework import serializers
from .models import Category, Item, Stock_Transactions

from rest_framework import serializers
from .models import Category

class CategoryAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description']

    def validate_name(self, value):
        user = self.context('user')
        if Category.objects.filter(name__iexact=value.strip(), user=user).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value.strip()



class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class AddItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Item
        fields = ['name', 'category_id', 'unit', 'description', 'current_stock']

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