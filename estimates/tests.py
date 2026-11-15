from decimal import Decimal
from django.test import SimpleTestCase
from .tax.gross_up import gross_up
from .tax.uk import personal_allowance, uk_income_tax
from .tax import swiss
from .tax.social_security import applicable_social_security

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