from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializers):

    class Meta:
        model = Category
        fields = ["id","Name","Description"]