from django.shortcuts import render

def home(request):
    context = {
        "project_name": "Cost Estimation",
        "item_count": 0,
    }
    return render(request, "estimates/home.html", context)