from django import forms
from .models import Category, Item, Stock_Transactions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class ItemForm(forms.Form):
      Category = forms.ModelChoiceField(queryset = Category.objects.all(),label="Select Category")

      class Meta:
          model = Category
          fields = ["Category"]

#client side validation  / field  validation
class AddForm(forms.ModelForm):
    Name = forms.CharField(label = "Item Name",required= True,max_length= 50)
    Category = forms.ModelChoiceField(queryset = Category.objects.all(),label="Category")
    Sku = forms.CharField(required=False)
    Unit = forms.CharField(label = "Unit",required=True ,max_length=10)
    Current_Stock = forms.IntegerField(label = "Current Stock",required=False)
    Description = forms.CharField(label = "Description",required=False, max_length=100)

    class Meta:
        model = Item
        fields = ["Name","Category","Unit","Sku","Description","Current_Stock"]

    # server side validation / non field.
    def clean(self):
        cleaned_data = super().clean()
        unit_name = cleaned_data.get("Unit")
        curr_stock = cleaned_data.get("Current_Stock")
        item_name = str(cleaned_data.get("Name"))
        item_name = item_name.title()
        if Item.objects.filter(Name=item_name).exists():
            raise forms.ValidationError("This Item Already Exists In Inventory")
        if unit_name == None:
            raise forms.ValidationError("Enter unit value.")
        else:
            if unit_name.isdigit():
                raise forms.ValidationError("Invalid unit value.")
        if curr_stock <= 0:
            raise forms.ValidationError("Enter Positive Value.")


class AddReduceForm(forms.ModelForm):
    Name = forms.ModelChoiceField(queryset=Item.objects.all(),label="Item", required=True)
    Transaction_type = forms.CharField(label = "Transcation Type",required=True)
    Quantity = forms.IntegerField(label = "Quantity", required = True)
    Notes = forms.CharField(label="Notes", required=False)
    Reference_note = forms.IntegerField(required=False)

    class Meta:
        model = Stock_Transactions
        fields = ["Name","Transaction_type","Quantity","Notes","Reference_note"]


class CategoryForm(forms.ModelForm):
    Name = forms.CharField(label="Category Name",max_length=30,required=True)
    Description = forms.CharField(label="Description",max_length=100,required=False)

    class Meta:
        model = Category
        fields = ["Name","Description"]
        
    def clean(self):
        cleaned_data = super().clean()
        name = str(cleaned_data.get("Name"))
        name = name.title()
        if Category.objects.filter(Name=name).exists():
            raise forms.ValidationError("This Item Already Exists In Inventory")


class RegisterForm(forms.ModelForm):
    username = forms.CharField(label = "Full Name", max_length=100, required=True)
    email = forms.EmailField(label = "Email address",max_length=50,required=True)
    password = forms.CharField(label = "Password",max_length=30,required=True)
    password_confirm = forms.CharField(label = "Confirm Password",max_length=30,required=True)

    class Meta:
        model = User
        fields = ["username","email","password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        Name = cleaned_data.get("username")

        if(password and password_confirm and password != password_confirm):
            raise forms.ValidationError("password doesn't match")
        
class LoginForm(forms.Form):
    username = forms.CharField(label="UserName", max_length=20, required=True)
    password = forms.CharField(label="Password", max_length=20, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid username or password")
            
class Forget_Password_Form(forms.Form):
    email = forms.EmailField(label = "Email Address", required=True)

    def clean(self):
        cleaned_data= super().clean()
        email = cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("there is no registered with this email")
        

class Reset_Password_Form(forms.Form):
    new_password = forms.CharField(label = "New_password", required = True)
    confirm_password = forms.CharField(label = "Confirm_password", required = True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Password doesn't match")