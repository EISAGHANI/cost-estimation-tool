from decimal import Decimal

from django import forms
from django.utils.html import format_html

from .calculator import AssignmentInputs
from .sources import SOURCES
from .tax.swiss import DEFAULT_HYPOTHETICAL_INCOME_TAX_CHF

HOME_COUNTRIES = [("CH", "Switzerland (city of Zurich)")]
HOST_COUNTRIES = [("UK", "United Kingdom (London)")]
DURATIONS = [
    (12, "1 year: 6 April 2026 to 5 April 2027"),
    (24, "2 years: 6 April 2026 to 5 April 2028"),
]


def choice_field(label, choices, initial, help_text, coerce=str):
    return forms.TypedChoiceField(
        label=label, choices=choices, initial=initial, help_text=help_text, coerce=coerce,
        error_messages={
            "required": f"{label}: please choose an option.",
            "invalid_choice": f"{label}: please choose one of the listed options.",
        },
    )


def amount_field(label, initial, help_text, minimum=Decimal("0"), decimal_places=2):
    return forms.DecimalField(
        label=label, initial=initial, help_text=help_text,
        min_value=minimum, max_digits=12, decimal_places=decimal_places,
        error_messages={
            "required": f"{label}: please enter an amount.",
            "invalid": f"{label}: please enter a number, for example 150000 (no letters or currency signs).",
            "min_value": f"{label}: the amount must be at least {minimum}.",
            "max_digits": f"{label}: the amount is too large.",
            "max_whole_digits": f"{label}: the amount is too large.",
            "max_decimal_places": f"{label}: use at most {decimal_places} decimal places.",
        },
    )


class CostEstimateForm(forms.Form):
    home_country = choice_field("Home country", HOME_COUNTRIES, "CH",
                                "Where the employee lives and works today.")
    host_country = choice_field("Host country", HOST_COUNTRIES, "UK",
                                "Where the employee will work during the assignment.")
    duration_months = choice_field(
        "Assignment length", DURATIONS, 24,
        "Full UK tax years. Postings over 2 years change the social security rule and are not covered.",
        coerce=int)

    base_salary_chf = amount_field("Base salary (CHF a year)", Decimal("150000"),
                                   "Swiss salary, as if the employee had stayed in Zurich.",
                                   minimum=Decimal("1"))
    bonus_chf = amount_field("Bonus (CHF a year)", Decimal("20000"), "Paid every year.")
    exchange_rate = amount_field("Exchange rate (CHF per £1)", Decimal("1.10"),
                                 "Used for every conversion, fixed for the whole assignment.",
                                 minimum=Decimal("0.01"), decimal_places=4)

    housing_monthly_gbp = amount_field("Housing in London (£ a month)", Decimal("3000"),
                                       "Rent the employer pays directly to the landlord.")
    relocation_allowance_chf = amount_field("Relocation allowance (CHF, year 1)", Decimal("5000"),
                                            "Cash paid to the employee once.")
    moving_costs_gbp = amount_field("Moving costs (£, year 1)", Decimal("6000"),
                                    "Flights and shipping paid by the employer.")
    temporary_housing_gbp = amount_field("Temporary housing (£, year 1)", Decimal("4000"),
                                         "Serviced apartment for the first 4 weeks.")

    hypothetical_swiss_tax_chf = amount_field(
        "Hypothetical Swiss income tax (CHF a year)", DEFAULT_HYPOTHETICAL_INCOME_TAX_CHF,
        format_html(
            "Federal, cantonal and communal tax a single person in the city of Zurich would pay "
            "on salary + bonus, without church tax. Taken from the "
            '<a href="{}" target="_blank" rel="noopener">official Swiss tax calculator</a>.',
            SOURCES["ch_tax_calculator"].url),
    )

    FIELDSETS = [
        ("Countries and length", ["home_country", "host_country", "duration_months"]),
        ("Home pay", ["base_salary_chf", "bonus_chf", "exchange_rate"]),
        ("Assignment benefits", ["housing_monthly_gbp", "relocation_allowance_chf",
                                 "moving_costs_gbp", "temporary_housing_gbp"]),
        ("Hypothetical Swiss tax", ["hypothetical_swiss_tax_chf"]),
    ]

    def fieldsets(self):
        """The fields in titled groups, so the template can draw one box per group."""
        return [(title, [self[name] for name in names]) for title, names in self.FIELDSETS]

    def to_inputs(self) -> AssignmentInputs:
        """Hand the checked values to the calculator (field names match exactly)."""
        return AssignmentInputs(**self.cleaned_data)