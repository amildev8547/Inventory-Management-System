from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re

category_choice=(
('Food', 'Food'),
('Clothes', 'Clothes'),
('Electronics','Electronics'),
('Home', 'Home'),
('Grocery', 'Grocery'),
)
class Category (models.Model):
 name=models.CharField(max_length=50, blank=True,null=True)
 def __str__(self):
     return self.name
 
def validate_phone_number(value):
    pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    if not pattern.match(value):
        raise ValidationError('Invalid phone number')
 
class Inventory (models.Model):
  category=models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
  item_name=models.CharField(max_length=50, blank=True, null=True)
  quantity = models.PositiveSmallIntegerField(null=True)
  issue_quantity=models.PositiveSmallIntegerField(null=True)
  issue_by=models.CharField(max_length=50,blank=True, null=True)
  issue_to=models.CharField(max_length=50,blank=True,null=True)
  issue_address=models.CharField(max_length=50,blank=True,null=True)
  phone_number = models.CharField(max_length=14, blank=True, null=True, validators=[validate_phone_number])
  created_by=models.CharField(max_length=50, blank=True, null=True) 
  reorder_level=models.PositiveSmallIntegerField(null=True)
  last_updated=models.DateTimeField(auto_now_add=False,auto_now=True)
  timestamp=models.DateTimeField(auto_now_add=True, auto_now=False  ) #date=models.DateTimeField(auto_now_add=False, auto_now=False)
  export_to_CSV=models.BooleanField(default=False)
  
  def __str__(self):
    return self.item_name +" "+"("+(str(self.quantity))+")"
  
  
  
class StockHistory (models.Model):
  category=models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
  item_name=models.CharField(max_length=50,blank=True,null=True) 
  quantity=models.IntegerField(default='0',blank=True,null=True)
  issue_quantity=models.IntegerField(default='0',blank=True, null=True)
  issue_by=models.CharField(max_length=50,blank=True,null=True)
  issue_to=models.CharField(max_length=50,blank=True,null=True)
  phone_number=models.CharField(max_length=50, blank=True, null=True)
  created_by=models.CharField(max_length=50, blank=True, null=True)
  reorder_level=models.IntegerField(default='0',blank=True,null=True)
  last_updated=models.DateTimeField(auto_now_add=False,auto_now=False, null=True)
  timestamp=models.DateTimeField(auto_now_add=False,auto_now=False,null=True)
  mobile_number=models.IntegerField(default='+91 ',blank=True, null=True)
  

