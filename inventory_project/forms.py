from django import forms
from .models import Category, Item, Stock_Transactions

#client side validation  / field client
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

    # server side validation
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


    def clean(self):
        cleaned_data = super().clean()
        quan = cleaned_data.get("Quantity")
        if quan <= 0:
            raise forms.ValidationError("Enter Positive Value.")

        
    