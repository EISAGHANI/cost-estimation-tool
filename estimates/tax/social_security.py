from dataclasses import dataclass

DETACHED_WORKER_LIMIT_MONTHS = 24


@dataclass
class SocialSecurityDecision:
    country: str      
    uk_nic_due: bool
    rule: str       


def applicable_social_security(home: str, host: str, months: int) -> SocialSecurityDecision:
    if home == "CH" and host == "UK" and months <= DETACHED_WORKER_LIMIT_MONTHS:
        return SocialSecurityDecision(
            country="CH",
            uk_nic_due=False,
            rule=(
                f"Swiss social security applies. A Swiss employer is posting the employee to work "
                f"temporarily in the UK for {months} months, which is within the 2-year limit for "
                f"detached workers. With a certificate of coverage from the Swiss AHV office, the "
                f"employee and employer keep paying AHV/IV/EO and unemployment insurance in "
                f"Switzerland, and no UK National Insurance is due."
            ),
        )
    return SocialSecurityDecision(
        country="UK",
        uk_nic_due=True,
        rule="UK National Insurance applies from the first day: the posting is longer than 2 years.",
    )