from django.contrib import admin
from .forms import *
from .models import Inventory
from .models import Category
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

   

admin.site.register(Category)

class InventoryResource(ModelResource):
    class Meta:
        model = Inventory

class StockCreateAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resource_class = InventoryResource
    list_display=['category','item_name','quantity','timestamp','last_updated']
    form=StockCreateForm
    list_filter=['category','item_name']
    search_fields=['category','item_name']
admin.site.register(Inventory,StockCreateAdmin)