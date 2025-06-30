from django.db import models

# Create your models here.
class Category(models.Model):
    Name = models.CharField(max_length=100)
    Description = models.TextField(blank=True,null=True)
    Created_At = models.DateTimeField(auto_now_add=True)

    def __str__ (self):
        return self.Name

class Item(models.Model):
    Name = models.CharField(max_length=100)
    Category = models.ForeignKey(Category,on_delete=models.CASCADE)
    Sku = models.CharField(max_length = 10)
    Description = models.TextField(blank=True,null=True)
    Unit = models.CharField(max_length=20)
    Current_Stock = models.PositiveIntegerField(default=0)
    Created_At = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Name
    
class Stock_Transactions(models.Model):
    Name = models.ForeignKey(Item,on_delete=models.CASCADE)
    Type = models.CharField(max_length=100)
    Quantity = models.PositiveIntegerField()
    Reference_note = models.IntegerField()
    Notes = models.CharField(max_length=100,blank=True,null=True)
    Created_At = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Type