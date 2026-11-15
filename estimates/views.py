from django.shortcuts import render

from .calculator import estimate_assignment
from .forms import CostEstimateForm


def cost_estimate(request):
    estimate = None
    if request.method == "POST":
        form = CostEstimateForm(request.POST)
        if form.is_valid():
            try:
                estimate = estimate_assignment(form.to_inputs())
            except ValueError as error:
                form.add_error(None, str(error))
    else:
        form = CostEstimateForm()
    return render(request, "estimates/cost_estimate.html",
                  {"form": form, "estimate": estimate, "active_tab": "cost"})