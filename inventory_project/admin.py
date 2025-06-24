from django.contrib import admin
from .models import Category, Item,Stock_Transactions
# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_display = ("Name","Description",)
    search_fields = ("Name",)
    list_filter = ("Created_At",)

class StockAdmin(admin.ModelAdmin):
    list_display = ("Name","Type")
    search_fields = ("Name",)
    list_filter = ("Created_At",)
admin.site.register(Category,ItemAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(Stock_Transactions,StockAdmin)
