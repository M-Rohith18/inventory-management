from django import forms
from .models import Category, Item, Stock_Transactions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

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