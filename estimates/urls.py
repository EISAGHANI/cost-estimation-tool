from django.urls import path
from . import views

app_name = "estimates"

urlpatterns = [
    path("", views.cost_estimate, name="cost_estimate"),
    path("immigration/", views.immigration, name="immigration"),
]