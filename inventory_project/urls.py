from . import views
from django.urls import path

app_name="inventory_project"

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('add_new',views.add_new_item, name='add_new_item'),
    path('add_reduce',views.add_reduce, name= 'add_reduce'),
    path('transaction_stock',views.transaction, name= 'transaction'),
    path("register",views.register,name="register"),
    path("login",views.login,name="login"),
    path("forget_password",views.forget_password,name="forget_password"),
    path('reset_password',views.reset_password,name="reset_password"),
]


