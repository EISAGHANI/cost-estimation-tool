from decimal import Decimal
from django.test import SimpleTestCase
from django.urls import reverse
from .forms import CostEstimateForm
from .tax.gross_up import gross_up
from .tax.uk import personal_allowance, uk_income_tax
from .tax.social_security import applicable_social_security
from .tax import benefits, swiss
from .calculator import AssignmentInputs, estimate_assignment


# The test case from the brief, as the form receives it.
TEST_CASE = {
    "home_country": "CH",
    "host_country": "UK",
    "duration_months": "24",
    "base_salary_chf": "150000",
    "bonus_chf": "20000",
    "exchange_rate": "1.10",
    "housing_monthly_gbp": "3000",
    "relocation_allowance_chf": "5000",
    "moving_costs_gbp": "6000",
    "temporary_housing_gbp": "4000",
    "hypothetical_swiss_tax_chf": "25000",
}

class UKIncomeTaxTests(SimpleTestCase):

    def test_no_tax_up_to_personal_allowance(self):
        self.assertEqual(uk_income_tax(Decimal("12570")).total, Decimal("0"))

    def test_top_of_basic_rate_band(self):
        # 37,700 x 20% = 7,540
        self.assertEqual(uk_income_tax(Decimal("50270")).total, Decimal("7540"))

    def test_allowance_is_tapered_above_100k(self):
        self.assertEqual(personal_allowance(Decimal("110000")), Decimal("7570"))
        self.assertEqual(personal_allowance(Decimal("125140")), Decimal("0"))

    def test_additional_rate(self):
        # 7,540 + 87,440 x 40% + 24,860 x 45% = 53,703
        self.assertEqual(uk_income_tax(Decimal("150000")).total, Decimal("53703"))


class GrossUpTests(SimpleTestCase):

    def test_tax_satisfies_t_equals_uktax_of_i_plus_t(self):
        result = gross_up(Decimal("120000"))
        tax_on_grossed_up = uk_income_tax(result.grossed_up_income).total
        self.assertAlmostEqual(tax_on_grossed_up, result.tax, delta=Decimal("0.01"))

    def test_zero_income_gives_zero_tax(self):
        self.assertEqual(gross_up(Decimal("0")).tax, Decimal("0"))

class SocialSecurityTests(SimpleTestCase):

    def test_two_year_posting_stays_in_swiss_system(self):
        decision = applicable_social_security("CH", "UK", 24)
        self.assertEqual(decision.country, "CH")
        self.assertFalse(decision.uk_nic_due)

    def test_longer_posting_moves_to_uk_system(self):
        self.assertTrue(applicable_social_security("CH", "UK", 36).uk_nic_due)

    def test_swiss_contributions_on_test_case_pay(self):
        share = swiss.social_security_share(Decimal("170000"))
        self.assertEqual(share.ahv_iv_eo, Decimal("9010.000"))  # 5.3% of 170,000
        self.assertEqual(share.alv, Decimal("1630.2000"))       # 1.1% of the 148,200 ceiling    

class BenefitTests(SimpleTestCase):

    def test_removal_costs_share_one_8000_exemption(self):
        moving, temporary = benefits.removal_costs(Decimal("6000"), Decimal("4000"))
        self.assertEqual(moving.taxable, Decimal("0"))
        self.assertEqual(temporary.taxable, Decimal("2000"))
        self.assertEqual(moving.treatment, benefits.NOT_TAXABLE)    

class CalculatorTests(SimpleTestCase):

    def setUp(self):
        inputs = AssignmentInputs(
            home_country="CH", host_country="UK", duration_months=24,
            exchange_rate=Decimal("1.10"),
            base_salary_chf=Decimal("150000"), bonus_chf=Decimal("20000"),
            housing_monthly_gbp=Decimal("3000"), relocation_allowance_chf=Decimal("5000"),
            moving_costs_gbp=Decimal("6000"), temporary_housing_gbp=Decimal("4000"),
            hypothetical_swiss_tax_chf=Decimal("25000"),
        )
        self.estimate = estimate_assignment(inputs)

    def test_test_case_gives_a_table_for_both_years(self):
        self.assertEqual([year.year for year in self.estimate.years], [1, 2])

    def test_one_off_benefits_only_in_year_one(self):
        year1, year2 = self.estimate.years
        self.assertEqual(len(year1.benefits), 4)
        self.assertEqual(len(year2.benefits), 1)

    def test_year_one_taxable_pay_before_tax(self):
        # home pay 154,545.46 - hypothetical tax 22,727.27 - hypothetical social security 9,672.91
        # + taxable benefits (36,000 + 4,545.45 + 2,000) = 164,690.73
        self.assertEqual(self.estimate.years[0].taxable_pay_before_tax, Decimal("164690.73"))

    def test_total_is_sum_of_sections(self):
        year = self.estimate.years[0]
        expected = (year.home_pay_total + year.benefits_total
                    + year.host_tax_total - year.deductions_total)
        self.assertEqual(year.total_cost, expected)

class FormErrorTests(SimpleTestCase):

    def test_missing_salary_gives_a_clear_message(self):
        data = {**TEST_CASE, "base_salary_chf": ""}
        form = CostEstimateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("please enter an amount", form.errors["base_salary_chf"][0])

    def test_letters_instead_of_a_number_give_a_clear_message(self):
        form = CostEstimateForm({**TEST_CASE, "bonus_chf": "twenty thousand"})
        self.assertFalse(form.is_valid())
        self.assertIn("please enter a number", form.errors["bonus_chf"][0])

    def test_unknown_country_is_rejected(self):
        form = CostEstimateForm({**TEST_CASE, "host_country": "FR"})
        self.assertFalse(form.is_valid())


class PageTests(SimpleTestCase):

    def test_cost_page_shows_the_test_case_form(self):
        response = self.client.get(reverse("estimates:cost_estimate"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Calculate")

    def test_valid_post_shows_the_cost_table(self):
        response = self.client.post(reverse("estimates:cost_estimate"), TEST_CASE)
        self.assertContains(response, "Total employer cost")
        self.assertContains(response, "Year 2 in detail")

    def test_bad_input_shows_a_message_not_a_crash(self):
        response = self.client.post(reverse("estimates:cost_estimate"),
                                    {**TEST_CASE, "exchange_rate": "abc"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "please enter a number")        