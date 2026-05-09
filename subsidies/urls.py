from django.urls import path
from . import views

app_name = "subsidies"

urlpatterns = [
    path("diagnosis/", views.diagnosis_form, name="diagnosis_form"),
]