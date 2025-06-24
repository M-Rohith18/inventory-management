from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import Http404
import random
from inventory_project.forms import AddForm, AddReduceForm
from .models import Category, Item, Stock_Transactions
from django.core.paginator import Paginator
# Create your views here.
def item_list(request):
    items = Item.objects.all().order_by('Category')
    # paginator
    paginator = Paginator(items,5)
    page_no = request.GET.get('page')
    page_obj = paginator.get_page(page_no)
    return render(request,"item_list.html",{"page_obj":page_obj})


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
                    return render(request,"add_reduce.html",{"form":form,"items":items,"redirect_to_transaction":True})
                else:
                    messages.error(request,"Current Stock is Less Than Quantity.")
            else:
                messages.error(request,"Invalid Transaction Type")
    return render(request,"add_reduce.html",{"form":form,"items":items})


def transaction(request):   
    transactions = Stock_Transactions.objects.all()
    return render(request, "transactions.html", {"transactions": transactions})