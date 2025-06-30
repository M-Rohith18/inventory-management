from . import views
from django.urls import path

app_name="inventory_project"

urlpatterns = [
    path("",views.login,name="login"),
    path("register",views.register,name="register"),
    path("forget_password",views.forget_password,name="forget_password"),
    path('reset_password/<uidb64>/<token>',views.reset_password,name="reset_password"),
    path('logout',views.logout,name="logout"),
    path('item_list', views.item_list, name='item_list'),
    path('add_category', views.add_category, name='add_category'),
    path('add_new',views.add_new_item, name='add_new_item'),
    path('add_reduce',views.add_reduce, name= 'add_reduce'),
    path('transaction_stock',views.transaction, name= 'transaction'),
    path('download',views.download_reports, name= 'download'),  
]



