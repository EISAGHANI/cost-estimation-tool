from django.shortcuts import render

from . import immigration as immigration_rules
from .calculator import estimate_assignment
from .forms import CostEstimateForm
from .sources import sources


def cost_estimate(request):
    estimate = None
    if request.method == "POST":
        form = CostEstimateForm(request.POST)
        if form.is_valid():
            try:
                estimate = estimate_assignment(form.to_inputs())
            except ValueError as error:
                form.add_error(None, str(error))  # shown at the top of the form, not a crash
    else:
        form = CostEstimateForm()  # pre-filled with the test case from the brief
    return render(request, "estimates/cost_estimate.html",
                  {"form": form, "estimate": estimate, "active_tab": "cost"})


def immigration(request):
    return render(request, "estimates/immigration.html", {
        "groups": immigration_rules.requirements_by_topic(),
        "total_cost": immigration_rules.total_cost(),
        "planning_note": immigration_rules.PLANNING_NOTE,
        "planning_sources": sources(*immigration_rules.PLANNING_SOURCE_KEYS),
        "active_tab": "immigration",
    })