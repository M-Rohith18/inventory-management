from django.contrib import admin
from .models import Category, Item,Stock_Transactions
# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name","description",)
    search_fields = ("Name",)
    list_filter = ("created_at",)

class StockAdmin(admin.ModelAdmin):
    list_display = ("name","type")
    search_fields = ("name",)
    list_filter = ("created_at",)
admin.site.register(Category,ItemAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(Stock_Transactions,StockAdmin)
