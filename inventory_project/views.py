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
from .authentication import JWTAuthenticationMixin

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


class CategoryListAPIView(JWTAuthenticationMixin,APIView):
    def get(self, request):
        user, error_response = self.authenticate(request)
        if error_response:
            return error_response

        categories = Category.objects.filter(user=user)
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ItemListAPIView(JWTAuthenticationMixin,APIView):
    def get(self, request):
        user, error_response = self.authenticate(request)
        if error_response:
            return error_response
      
        category_id = request.GET.get('category_id')
        if category_id:
            items = Item.objects.filter(user=request.user, category_id=category_id)
        else:
            items = Item.objects.filter(user=request.user)

        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



def add_category(request):
    return render(request,"category.html")

class AddCategoryAPIView(JWTAuthenticationMixin,APIView):
    def post(self, request):
        user, error_response = self.authenticate(request)
        if error_response:
            return error_response
        
        serializer = CategoryAddSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'Category added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def add_item(request):
    return render(request,"add_item.html")


class AddItemAPIView(JWTAuthenticationMixin,APIView):
    def post(self, request):
        user, error_response = self.authenticate(request)
        if error_response:
            return error_response
        
        serializer = AddItemSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            item_count = Item.objects.filter(user=request.user).count() + 1
            sku = f"ITEM-{item_count:03d}"

            try:
                category = Category.objects.get(id=request.data['category_id'], user=request.user)
            except Category.DoesNotExist:
                return Response({'category_id': ['Invalid or unauthorized category ID.']}, status=400)

            Item.objects.create(
                user=request.user,
                sku=sku,
                category=category,
                **serializer.validated_data
            )
            return Response({'message': 'Item added successfully'}, status=201)

        return Response(serializer.errors, status=400)


def add_reduce_item(request): 
    return render(request,"add_reduce.html")

class StockTransactionAPIView(JWTAuthenticationMixin,APIView):
    def post(self, request):
        user, error_response = self.authenticate(request)
        if error_response:
            return error_response

        item_id = request.data.get('item')
        if not item_id:
            return Response({'detail': 'Item ID is required'}, status=400)

        try:
            item = Item.objects.get(id=item_id, user=request.user)
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
            message = render_to_string('stock_alert_mail.html', {
                'item_name': item.name,
                'item_Quantity': item.current_stock,
                'item_minimum_stock': 20,
                'user': request.user
            })
            send_mail(subject, message, user_email, [request.user.email])

        txn = Stock_Transactions.objects.create(
            name=item,
            user=request.user,
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


class ItemListAPIView(JWTAuthenticationMixin,APIView):
    def get(self, request):
        user, error_response = self.authenticate(request)
        if error_response:
            return error_response

        category_id = request.GET.get('category_id')
        if category_id:
            items = Item.objects.filter(user=request.user, category_id=category_id)
        else:
            items = Item.objects.filter(user=request.user)

        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
def transaction(request):   
    return render(request, "transaction.html")

class StockTransactionListAPIView(JWTAuthenticationMixin,APIView):
    def get(self, request):
        user, error_response = self.authenticate(request)
        if error_response:
            return error_response

        transactions = Stock_Transactions.objects.filter(user=request.user).order_by('-created_at')
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


