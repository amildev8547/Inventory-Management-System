from django.urls import path
from .views import *



urlpatterns = [
    path("",home,name="home"),
    path("inventory/",inventory,name="inventory"),
    path("stock",stock,name="stock"),
    path('checkout/', stockhistory, name='checkout'),
    path("chart",chart,name="chart"),
    path("pdf",pdf,name="pdf"),
    path("add_items",add_items,name="add_items"),
    path("update_items/<str:pk>",update_items,name="update_items"),
    path("delete_items/<str:pk>",delete_items,name="delete_items"),
    path("reorder_level/<str:pk>",reorder_level,name="reorder_level"),
    path("issue_items/<int:pk>",issue_items,name="issue_items"),
    path("per_product/<int:pk>",per_product_view,name="per_product"),
    path('issue_items/<int:pk>/pdf/', generate_pdf, name='generate_pdf'),
    







]
