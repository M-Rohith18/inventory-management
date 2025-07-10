from rest_framework import serializers
from .models import Category, Item, Stock_Transactions

from rest_framework import serializers
from .models import Category

class CategoryAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        value = value.title()
        user = self.context['user']
        if Category.objects.filter(name__iexact=value, user=user).exists():
            raise serializers.ValidationError("You already have a category with this name.")
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        

class ItemListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Item
        fields = '__all__'


class AddItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Item
        fields = ['name', 'category_id', 'unit', 'description', 'current_stock']

    def validate_name(self, value):
        value = value.title()
        user = self.context.get('user')
        if Item.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Item with this name already exists.")
        return value
    

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
    item_name = serializers.CharField(source='name.name', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Stock_Transactions
        fields = ['item_name', 'type', 'quantity', 'created_at']
