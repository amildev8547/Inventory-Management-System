from django import forms   
from .models import *




class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['category', 'item_name', 'quantity', 'reorder_level']

    def clean_item_name(self):
        item_name = self.cleaned_data.get('item_name')
        if not item_name:
            raise forms.ValidationError('Please enter an item name')
        return item_name

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if not quantity:
            raise forms.ValidationError('Please enter a quantity')
        elif quantity < 0:
            raise forms.ValidationError('Quantity cannot be negative')
        elif quantity > 10000:
            raise forms.ValidationError('Quantity is too high, please enter a smaller value')
        return quantity
    
    
    def clean_reorder_level(self):
        reorder_level = self.cleaned_data.get('reorder_level')
        if not reorder_level:
            raise forms.ValidationError('Please enter a reorder level')
        elif reorder_level < 0:
            raise forms.ValidationError('Reorder level cannot be negative')
        elif reorder_level > 100:
            raise forms.ValidationError('Reorder level is too high, please enter a smaller value')
        return reorder_level
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        reorder_level = cleaned_data.get('reorder_level')

        if quantity and reorder_level and reorder_level >= quantity:
            raise forms.ValidationError('Reorder level must be less than quantity')

        return cleaned_data

class StockSearchForm(forms.ModelForm):
  export_to_CSV=forms.BooleanField() 
  class Meta:
    model = Inventory
    fields = ['export_to_CSV']

class StockUpdateForm(forms.ModelForm):
   class Meta:
     model = Inventory
     fields=['category', 'item_name', 'quantity', 'reorder_level']

   
class IssueForm(forms.ModelForm):
   class Meta:
      model = Inventory
      fields=['item_name','issue_quantity','issue_to','issue_address','phone_number']

   def clean_issue_to(self):
        issue_to = self.cleaned_data.get('issue_to')
        if not issue_to:
            raise forms.ValidationError('Please enter the correct name')
        return issue_to
  

   

class ReorderLevelForm(forms.ModelForm):
   class Meta:
      model = Inventory
      fields=['reorder_level']
   def clean_reorder_level(self):
      reorder_level = self.cleaned_data.get('reorder_level')
      if not reorder_level:
         raise forms.ValidationError('Please enter a reorder level')
      elif reorder_level < 0:
         raise forms.ValidationError('Reorder level cannot be negative')
      return reorder_level
   


