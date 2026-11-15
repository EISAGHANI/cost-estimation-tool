from dataclasses import dataclass
from decimal import Decimal


AHV_IV_EO_RATE = Decimal("0.053")    # old age, disability, loss of earnings: 4.35% + 0.7% + 0.25%
ALV_RATE = Decimal("0.011")          # unemployment insurance
ALV_CEILING_CHF = Decimal("148200")  # unemployment insurance only on pay up to this amount

DEFAULT_HYPOTHETICAL_INCOME_TAX_CHF = Decimal("0")


@dataclass
class SwissContributions:
    ahv_iv_eo: Decimal
    alv: Decimal

    @property
    def total(self) -> Decimal:
        return self.ahv_iv_eo + self.alv


def social_security_share(gross_pay_chf: Decimal) -> SwissContributions:
    gross = Decimal(gross_pay_chf)
    return SwissContributions(
        ahv_iv_eo=gross * AHV_IV_EO_RATE,
        alv=min(gross, ALV_CEILING_CHF) * ALV_RATE,
    )