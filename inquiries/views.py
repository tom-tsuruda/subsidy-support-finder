from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def contact_form(request):
    return render(request, "inquiries/contact_form.html")