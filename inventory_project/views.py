from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse
import csv
from .forms import  Forget_Password_Form,  RegisterForm, Reset_Password_Form
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from .models import Category, Item, Stock_Transactions
from django.core.paginator import Paginator
from django.db.models import Sum,Count,Avg,Max,Min
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import AddItemSerializer, CategoryAddSerializer, CategoryListSerializer, ItemListSerializer, ItemSerializer, StockTransactionListSerializer
import jwt
from django.conf import settings

# Create your views here.

def register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)#user data created
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request,"Registration Successfull, You can Login")
            return render(request,"register.html",{"form":form,"redirect_to_login":True})
    return render(request, "register.html",{"form":form})

def forget_password(request):
    form = Forget_Password_Form()
    if request.method == "POST":
        form = Forget_Password_Form(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email = email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            current_site = get_current_site(request)
            domain = current_site.domain
            subject = "reset password requested"
            message = render_to_string('reset_password_email.html',{"domain":domain,"uid":uid,"token":token})
            send_mail(subject,message,"mrohith481@gmail.com",[email])
            messages.success(request,"email sent successfully")
    return render(request,"forget_password.html",{"form":form,"redirect":True})

def reset_password(request,uidb64,token):
    form = Reset_Password_Form()
    if request.method == "POST":
        form = Reset_Password_Form(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(id=uid)
            except (TypeError,ValueError,OverflowError,User.DoesNotExist):
                user = None
            if (user is not None and default_token_generator.check_token(user,token)):
                user.set_password(new_password)
                user.save()
                messages.success(request,"YOUR PASSWORD RESET SUCCESSFULLY")
                return render(request,"reset_password.html",{'redirect_to_login':True})
    return render(request,"reset_password.html")

def logout(request):
    auth_logout(request)
    return redirect("inventory_project:login")

def login(request):
    return render(request,"login.html")

def dashboard(request):
    return render(request,"dashboard.html")

class CategoryListAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = User.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'detail': 'Token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        categories = Category.objects.filter(user=user).all()
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ItemListAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = User.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'detail': 'Token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        category_id = request.GET.get('category_id')
        if not category_id:
            return Response({'detail': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        items = Item.objects.filter(user=user, category_id=category_id)
        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def add_category(request):
    return render(request,"category.html")

class AddCategoryAPIView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = User.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'detail': 'Token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategoryAddSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'message': 'Category added successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def add_item(request):
    return render(request,"add_item.html")

class AddItemAPIView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Missing or invalid token'}, status=401)
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload.get('user_id'))
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token expired'}, status=401)
        except jwt.DecodeError:
            return Response({'detail': 'Token invalid'}, status=401)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)
        category_id = request.data.get('category_id')
        if not category_id:
            return Response({'detail': 'Category is required'}, status=400)
        try:
            category = Category.objects.get(id=category_id, user=user)
        except Category.DoesNotExist:
            return Response({'detail': 'Invalid category'}, status=400)
        item_count = Item.objects.filter(user=user).count() + 1
        sku = f"ITEM-{item_count:03d}"
        serializer = AddItemSerializer(data=request.data)
        if serializer.is_valid():
            Item.objects.create(
                user=user,
                category=category,
                sku=sku,
                **serializer.validated_data
            )
            return Response({'message': 'Item added successfully'}, status=201)
        return Response(serializer.errors, status=400)

def add_reduce_item(request): 
    return render(request,"add_reduce.html")

class StockTransactionAPIView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Missing or invalid token'}, status=401)
        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload.get('user_id'))
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token expired'}, status=401)
        except jwt.DecodeError:
            return Response({'detail': 'Token invalid'}, status=401)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)
        item_id = request.data.get('item')

        try:
            item = Item.objects.get(id=item_id, user=user)
        except Item.DoesNotExist:
            return Response({'detail': 'Item not found or not yours'}, status=400)
        trans_type = request.data.get('type')
        quantity = int(request.data.get('quantity', 0))
        notes = request.data.get('notes', '')

        if trans_type == 'OUT' and quantity > item.current_stock:
            return Response({'detail': 'Not enough stock to reduce'}, status=400)
        if trans_type == 'IN':
            item.current_stock += quantity
        elif trans_type == 'OUT':   
            item.current_stock -= quantity
        item.save()

        if item.current_stock < 20:
            user_email = "mrohith481@gmail.com"
            subject = "Low Stock Alert Mail"
            message = render_to_string('stock_alert_mail.html', {'item_name': item.name, 'item_Quantity': item.current_stock, 'item_minimum_stock': 20, 'user': request.user})
            send_mail(subject, message, user_email, [user.email])

        txn = Stock_Transactions.objects.create(
            name=item,
            user=user,
            type=trans_type,
            quantity=quantity,
            reference_note=0, 
            notes=notes
        )
        txn.reference_note = txn.id
        txn.save()
        return Response({
            'message': 'Stock updated successfully',
            'reference_note': txn.reference_note
        }, status=201)
    
class ItemListAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = User.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'detail': 'Token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        category_id = request.GET.get('category_id')
        if category_id:
            items = Item.objects.filter(user=user, category_id=category_id)
        else:
            items = Item.objects.filter(user=user)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
def transaction(request):   
    return render(request, "transaction.html")

class StockTransactionListAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'detail': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            user = User.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'detail': 'Token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        transactions = Stock_Transactions.objects.filter(user=user).order_by('-created_at')
        serializer = StockTransactionListSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def download_reports(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
    writer = csv.writer(response)

    # Header
    writer.writerow(['Item', 'Type', 'Quantity', 'Reference', 'Date'])

    # Transaction rows
    transactions = Stock_Transactions.objects.select_related('name')
    for tx in transactions:
        writer.writerow([
            tx.name.name,
            tx.type,
            tx.quantity,
            tx.created_at,
        ])

    writer.writerow([])
    writer.writerow(['--- Summary ---'])

    # Aggregates for 'Add' transactions
    add_qs = Stock_Transactions.objects.filter(type='IN')
    add_stats = add_qs.aggregate(
        total=Sum('quantity'),
        count=Count('id'),
        avg=Avg('quantity'),
        max_qty=Max('quantity'),
        min_qty=Min('quantity')
    )

    # Aggregates for 'Reduce' transactions
    reduce_qs = Stock_Transactions.objects.filter(type='OUT')
    reduce_stats = reduce_qs.aggregate(
        total=Sum('quantity'),
        count=Count('id'),
        avg=Avg('quantity'),
        max_qty=Max('quantity'),
        min_qty=Min('quantity')
    )

    # Find items for max/min quantities
    def get_item(qs, qty_field, stats, key):
        val = stats[key]
        if val is None:
            return 'N/A'
        item = qs.filter(quantity=val).select_related('name').first()
        return f"{val} (Item: {item.name.name})" if item else f"{val} (Item: N/A)"



    # Add summary section
    writer.writerow(['--- Add Transactions ---'])
    writer.writerow(['Total Quantity', add_stats['total'] or 0])
    writer.writerow(['Transaction Count', add_stats['count'] or 0])
    writer.writerow(['Average Quantity', round(add_stats['avg'] or 0, 2)])
    writer.writerow(['Maximum Quantity', get_item(add_qs, 'max_qty', add_stats, 'max_qty')])
    writer.writerow(['Minimum Quantity', get_item(add_qs, 'min_qty', add_stats, 'min_qty')])
    writer.writerow([])

    # Reduce summary section
    writer.writerow(['--- Reduce Transactions ---'])
    writer.writerow(['Total Quantity', reduce_stats['total'] or 0])
    writer.writerow(['Transaction Count', reduce_stats['count'] or 0])
    writer.writerow(['Average Quantity', round(reduce_stats['avg'] or 0, 2)])
    writer.writerow(['Maximum Quantity', get_item(reduce_qs, 'max_qty', reduce_stats, 'max_qty')])
    writer.writerow(['Minimum Quantity', get_item(reduce_qs, 'min_qty', reduce_stats, 'min_qty')])
    writer.writerow([])


    return response


