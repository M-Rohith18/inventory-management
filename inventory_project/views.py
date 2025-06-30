from itertools import count
from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import Http404
import random ,csv
from .forms import CategoryForm, Forget_Password_Form, LoginForm,  RegisterForm, Reset_Password_Form
from inventory_project.forms import AddForm, AddReduceForm,ItemForm
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


def login(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, "Login Successful")
                return render(request,"login.html",{"form":form,"redirect_to_item_list":True})
    return render(request,"login.html",{"form":form})


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


def item_list(request):
    categorys = Category.objects.all()
    items = Item.objects.all()
    form = ItemForm()
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            category_id = request.POST.get('Category')
            items = Item.objects.select_related('category_id')
            items = Item.objects.filter(Category = category_id)
            return render(request,"item_list.html",{"categorys":categorys,"form":form,"items":items})
            # paginator
            # paginator = Paginator(items,5)
            # page_no = request.GET.get('page')
            # page_obj = paginator.get_page(page_no)
    return render(request,"item_list.html",{"categorys":categorys,"form":form})

def add_category(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            name = str(form.cleaned_data["Name"]).title()
            description = form.cleaned_data["Description"] or None
            Category.objects.create(Name=name, Description=description)
            messages.success(request, "Category added successfully!")
            return render(request, "category.html",{"redirect_to_home":True})
    return render(request,"category.html",{"form":form})


def add_new_item(request):
    categories = Category.objects.all()
    form = AddForm()
    if request.method == "POST":
        form = AddForm(request.POST)
        if form.is_valid():
            item = form.save(commit = False)
            description = form.cleaned_data["Description"] or None
            current_stock = form.cleaned_data["Current_Stock"] or 0
            sku = ""
            category = str(form.cleaned_data["Category"])
            item_name = str(form.cleaned_data["Name"])
            sku += category[0:2].lower()+item_name[0:2].lower()
            digit = str(random.randint(1000,999999))
            sku += digit
            item.Name = item_name.title()
            item.Sku = sku
            item.Description = description
            item.Current_Stock = current_stock
            item.save()
            messages.success(request,"Item Added To Inventory Successfully")
            return render(request,"add_item.html",{"form":form,"categories":categories,"redirect_to_home":True})
    return render(request,"add_item.html",{"form":form,"categories":categories})




def add_reduce(request): 
    items = Item.objects.all().order_by("Name")
    form = AddReduceForm()
    if request.method == "POST":
        form = AddReduceForm(request.POST)
        if form.is_valid():
            item_id = request.POST['Name']
            transaction_type = str(request.POST['Transaction_type']).upper()
            item = Item.objects.get(pk = item_id)
            current_stock = item.Current_Stock
            quantity = form.cleaned_data['Quantity']
            if transaction_type == 'IN':
                item.Current_Stock += quantity
                messages.success(request,"Quantity Added Succesffuly")
                item.save()
                transaction = form.save(commit = False)
                Ref_note = random.randint(10000000,999999999)
                transaction.Type = transaction_type
                transaction.Reference_note = Ref_note
                transaction.Notes = form.cleaned_data["Notes"] or None
                transaction.save()
                if item.Current_Stock < 20:
                        user_email = "mrohith481@gmail.com"
                        subject = "Low Stock Alert Mail"
                        message = render_to_string('stock_alert_mail.html', {'item_name': item.Name, 'item_Quantity': item.Current_Stock, 'item_minimum_stock': 20, 'user': request.user})
                        send_mail(subject, message, user_email, [request.user.email])
                return render(request,"add_reduce.html",{"form":form,"items":items,"redirect_to_transaction":True})
            elif transaction_type == 'OUT':
                if current_stock > quantity:
                    item.Current_Stock -= quantity
                    messages.success(request,"Quantity Reduced Succesfully")
                    item.save()
                    transaction = form.save(commit = False)
                    Ref_note = random.randint(10000000,999999999)
                    transaction.Reference_note = Ref_note
                    transaction.Type = transaction_type
                    transaction.Notes = form.cleaned_data["Notes"] or None
                    transaction.save()  
                    if item.Current_Stock < 20:
                        user_email = "mrohith481@gmail.com"
                        subject = "Low Stock Alert Mail"
                        message = render_to_string('stock_alert_mail.html', {'item_name': item.Name, 'item_Quantity': item.Current_Stock, 'item_minimum_stock': 20, 'user': request.user})
                        send_mail(subject, message, user_email, [request.user.email])
                    return render(request,"add_reduce.html",{"form":form,"items":items,"redirect_to_transaction":True})
                else:
                    messages.error(request,"Current Stock is Less Than Quantity.")
            else:
                messages.error(request,"Invalid Transaction Type")
    return render(request,"add_reduce.html",{"form":form,"items":items})


def transaction(request):   
    transactions = Stock_Transactions.objects.all().order_by('-Created_At')
    #paginator
    paginator = Paginator(transactions,5)
    page_no = request.GET.get('page')
    page_obj = paginator.get_page(page_no)
    return render(request, "transaction.html", {"page_obj":page_obj})

def download_reports(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
    writer = csv.writer(response)

    # Header
    writer.writerow(['Item', 'Type', 'Quantity', 'Reference', 'Date'])

    # Transaction rows
    transactions = Stock_Transactions.objects.select_related('Name')
    for tx in transactions:
        writer.writerow([
            tx.Name.Name,
            tx.Type,
            tx.Quantity,
            tx.Reference_note,
            tx.Created_At,
        ])

    writer.writerow([])
    writer.writerow(['--- Summary ---'])

    # Aggregates for 'Add' transactions
    add_qs = Stock_Transactions.objects.filter(Type__iexact='IN')
    add_stats = add_qs.aggregate(
        total=Sum('Quantity'),
        count=Count('id'),
        avg=Avg('Quantity'),
        max_qty=Max('Quantity'),
        min_qty=Min('Quantity')
    )

    # Aggregates for 'Reduce' transactions
    reduce_qs = Stock_Transactions.objects.filter(Type__iexact='OUT')
    reduce_stats = reduce_qs.aggregate(
        total=Sum('Quantity'),
        count=Count('id'),
        avg=Avg('Quantity'),
        max_qty=Max('Quantity'),
        min_qty=Min('Quantity')
    )

    # Find items for max/min quantities
    def get_item(qs, qty_field, stats, key):
        val = stats[key]
        if val is None:
            return 'N/A'
        item = qs.filter(Quantity=val).select_related('Name').first()
        return f"{val} (Item: {item.Name.Name})" if item else f"{val} (Item: N/A)"



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


