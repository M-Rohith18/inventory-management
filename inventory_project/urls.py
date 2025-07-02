from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

app_name="inventory_project"

urlpatterns = [
    path("",views.register,name="register"),
    path("forget_password/",views.forget_password,name="forget_password"),
    path('reset_password/<uidb64>/<token>/',views.reset_password,name="reset_password"),

    # Login Template
    path("login/",views.login,name="login"),
    # Token Generation API
    path("api/token/", TokenObtainPairView.as_view(), name='token_obtain_pair'),


    path('logout/',views.logout,name="logout"),

    # Dashboard Template
    path('dashboard/', views.dashboard, name='dashboard'),
    # Dashboard Category API
    path('api/categories/', views.CategoryListAPIView.as_view(), name='api_category_list'),
    # Dashboard Item API
    path('api/items/', views.ItemListAPIView.as_view(), name='api_items_list'),

    # Adding Category Template
    path('add_category/', views.add_category, name='add_category'),
    # Adding Category API
    path('api/add-category/', views.AddCategoryAPIView.as_view(), name='api_add_category'),

    # Adding Item Template
    path('add_item/',views.add_item, name='add_item'),
    # Adding Item API
    path('api/add-item/', views.AddItemAPIView.as_view(), name='api_add_item'),

    # Adding Reduce Item Template
    path('add_reduce_item/',views.add_reduce_item, name= 'add_reduce_item'),
    # Item API
    path('api/item/', views.ItemListAPIView.as_view(), name='api_item_list'),
    # Adding Reduce Item API
    path('api/stock-add-reduce/', views.StockTransactionAPIView.as_view(), name='api_stock_add_reduce'),
    
    # Stock Transaction Template
    path('transaction_stock/',views.transaction, name= 'transaction'),
    # Stock Transaction API
    path('api/stock-transactions/', views.StockTransactionListAPIView.as_view(), name='api_stock_transactions'),

    path('download/',views.download_reports, name= 'download'),
]




