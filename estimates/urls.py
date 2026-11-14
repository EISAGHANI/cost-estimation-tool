from django.urls import path
from . import views

app_name = "estimates"

urlpatterns = [
    path("", views.home, name="home"),
]