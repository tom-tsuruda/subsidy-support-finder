from django.urls import path
from . import views

app_name = "inquiries"

urlpatterns = [
    path("contact/", views.contact_form, name="contact_form"),
]