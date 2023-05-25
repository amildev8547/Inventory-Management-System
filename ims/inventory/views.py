from django.shortcuts import render,redirect,get_object_or_404
from .models import Inventory
from django.http import HttpResponse
import csv
import datetime
from django.contrib import messages
from .forms import *
from twilio.rest import Client
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
from datetime import datetime, date


#Stock Table
def stock(request):
    form= StockSearchForm(request.POST or None)
    queryset=Inventory.objects.all()
    p= Paginator(Inventory.objects.all(), 10)
    page=request.GET.get('page')
    pages=p.get_page(page)
    if request.method == 'POST':
        if form.is_valid():
            category = form.cleaned_data.get('category')
            item_name = form.cleaned_data.get('item_name')
            if category and item_name:
                queryset = Inventory.objects.filter(
                    category__startswith=category,
                    item_name__startswith=item_name
                )
            elif category:
                queryset = Inventory.objects.filter(category__startswith=category)
            elif item_name:
                queryset = Inventory.objects.filter(item_name__startswith=item_name)
            if form.cleaned_data.get('export_to_CSV'):
                response=HttpResponse(content_type='text/csv')
                response['Content-Disposition']='attachment; filename="List of stock.csv"'
                writer=csv.writer(response)
                writer.writerow(['CATEGORY','ITEM NAME','QUANTITY','STOCK CREATED','STOCK UPDATED'])
                for inventory in queryset:
                    writer.writerow([inventory.category,inventory.item_name,inventory.quantity,inventory.timestamp.strftime('%m/%d/%Y %H:%M:%S'),inventory.last_updated.strftime('%m/%d/%Y %H:%M:%S'),inventory.created_by])
                return response
    context={
        "queryset":queryset,
        "form":form,
        "pages":pages
    }
    return render(request, "stock.html",context)


#Home Page
def inventory(request):
    labels=[]
    data=[]
    queryset=Inventory.objects.order_by('-quantity')
    for item in queryset:
        labels.append(item.item_name)
        data.append(item.quantity)
        context={ 'labels':labels,'data':data}
    return render(request, "index.html",context)


#Login View
def home(request):
    return render(request, "base.html")
def pdf(request):
    return render(request, "pdf_template.html")

#Product View
def per_product_view(request,pk):
    queryset= Inventory.objects.get(id=pk)
    context={
        "title":queryset.item_name,
        "queryset":queryset,
    }
    return render(request, "per_product.html",context)


#Chart View
def chart(request):
    labels=[]
    data=[]
    queryset=Inventory.objects.order_by('-quantity')
    for item in queryset:
        labels.append(item.item_name)
        data.append(item.quantity)
        context={ 'labels':labels,'data':data}
    return render(request, "chart.html",context)

#Add Items
def add_items(request):
    form=StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request,'Stock is Successfully Added!!')
        return redirect('/stock')
    context={
        "form":form,
        "title":"Add Item",
    }
    form = StockCreateForm()

    # Add the cleared form to the context
    context['form'] = form

    return render(request,"add_items.html",context)


#Update View
def update_items(request,pk):
    queryset=Inventory.objects.get(id=pk)
    form=StockUpdateForm(instance=queryset)
    if request.method=='POST':
        form = StockUpdateForm(request.POST,instance=queryset)
        if form.is_valid():    
          form.save()
          messages.success(request,'Stock is Successfully Updated!!')
          return redirect('/stock')
    context={
        "form":form,
        "title":"Update Item",
    }
    return render(request,"update_items.html",context)


#Delete View
def delete_items(request,pk):
      up=Inventory.objects.filter(id=pk)
      up.delete()
      messages.success(request,'Stock is Successfully Deleted!!')
      return redirect('/stock')

#Reordering Item
def reorder_level(request,pk):
    queryset=Inventory.objects.get(id=pk)
    form=StockUpdateForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.save()
        messages.success(request,"Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))
        return redirect("/stock")
    context={
        "form":form,
        "instance":queryset,
    }
    return render(request,"update_items.html",context)

#issue Item
def issue_items(request,pk):
    queryset= Inventory.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit= False)
        instance.receive_quantity=0
        instance.quantity -= instance.issue_quantity
        messages.success(request, "Issued Successfully " + str(instance.quantity)+" "+ str(instance.item_name)+"s now left in the store")
        instance.timestamp = datetime.now()
        instance.save()
         # Store data in session
  
        issued_items = request.session.get('issued_items', [])
        issued_items.append({
            'issue_to': instance.issue_to,
            'issue_quantity': instance.issue_quantity,
            'item_name': instance.item_name,
            'issue_address':instance.issue_address,
            'phone_number': instance.phone_number,
            'timestamp':str(instance.timestamp.strftime('%Y-%m-%d   %H:%M'))  
         })
        request.session['issued_items'] = issued_items
        request.session['username'] = str(request.user)
        #Generate password
        pdf_file = generate_pdf(instance)
        #Generate message to the user
        account_sid = "ACae1781d3bdacfb73b1dad05ba35bf29d"
        auth_token = "979ed60aa48df52d659065c50c7d506f"
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="Mr/Mrs {0},{3} We have issued {1} {2}s from INVENTO Warehouse. Thank You ".format(instance.issue_to, instance.issue_quantity, instance.item_name, instance.issue_address),
            from_="+12545365406",
            to=instance.phone_number)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
        return response
    context={
        "title": 'Issue '+ str(queryset.item_name),
        "queryset":queryset,
        "form":form,
        "username":'Issued By: '+str(request.user),

    }
    return render(request,"issue_items.html", context)


#Stock History
def stockhistory(request):
    issued_items = request.session.get('issued_items')

    # Use the data in your template or in your view logic

    context = {
        'issued_items': issued_items
    }

    return render(request, 'stock_history.html', context)


from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

def generate_pdf(instance):
    # Create a file-like buffer to receive PDF data.
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)

    # Register the Arial font.
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

    # Set the font style.
    p.setFont("Arial", 14)

    # Add watermark text.
    watermark_text = 'CONFIDENTIAL'
    p.setFont("Arial", 60, leading=28)
    p.setFillColorRGB(0.7, 0.7, 0.7)  # Adjust the color to achieve the desired opacity
    p.rotate(45)
    p.drawString(290, 230, watermark_text)
    p.rotate(-45)

    # Add a header.
    header_text = 'INVENTO WAREHOUSE LTD'
    p.setFillColor(colors.HexColor("#424242"))
    p.setFont("Arial", 30, leading=28)
    p.drawString(100, 750, header_text)

    # Add a decorative line below the header.
    p.setLineWidth(2)
    p.setStrokeColor(colors.HexColor("#D3D3D3"))
    p.line(50, 730, 550, 730)

    # Add a subheader.
    subheader_text = 'STOCK ISSUED RECEIPT'
    p.setFont("Arial", 20)
    p.drawString(200, 600, subheader_text)

    # Add a thank you message.
    p.setFont("Arial", 14)
    p.setFillColor(colors.HexColor("#424242"))
    p.drawString(260, 400, 'THANK YOU')
    p.setFont("Arial", 12)
    p.drawString(255, 380, 'Have A Nice Day')

    # Add date and location.
    p.setFont("Arial", 12)
    p.drawString(472, 700, str(date.today()))
    p.drawString(462, 680, 'Pathanamthitta')

    # Create table data.
    table_data = [
        ['Item Name:', instance.item_name],
        ['Issued Quantity:', str(instance.issue_quantity)],
        ['Issued Date:', str(date.today())],
        ['Issued To:', instance.issue_to],
        ['Place:', instance.issue_address],
        ['Phone Number:', instance.phone_number]
    ]

    # Set table style.
    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#D3D3D3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#424242")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Create the table.
    table = Table(table_data, colWidths=[100, 300])
    table.setStyle(table_style)

    # Get the table width and height.
    table_width, table_height = table.wrap(0, 0)

    # Calculate the positioning of the table.
    x = (600 - table_width) / 2  # Center the table horizontally.
    y = 600 - table_height - 30  # Position the table below the header.

    # Draw the table on the canvas.
    table.drawOn(p, x, y)

    # Add a footer.
    footer_text = 'Page %s' % p.getPageNumber()
    p.drawString(450, 50, footer_text)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer
