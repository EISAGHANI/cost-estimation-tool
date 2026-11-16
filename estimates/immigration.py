from dataclasses import dataclass
from decimal import Decimal

from .sources import sources


@dataclass(frozen=True)
class Requirement:
    topic: str            # Work permit / Business visit / Passport / Employer duties
    title: str
    detail: str
    time: str
    cost_gbp: Decimal     # 0 when there is no fee
    cost_note: str
    source_keys: tuple

    @property
    def sources(self):
        return sources(*self.source_keys)


SWITZERLAND_TO_UK = [
    Requirement(
        topic="Work permit",
        title="Senior or Specialist Worker visa (Global Business Mobility)",
        detail=("The route for an employee sent to a UK branch or subsidiary of their employer. "
                "Needs a certificate of sponsorship from a licensed UK sponsor, a job on the "
                "eligible list, and pay of at least £52,500 or the job's going rate, whichever is "
                "higher. The employee must have worked for the employer outside the UK for 12 months, "
                "unless paid £73,900 or more. This employee has 3 years with the employer."),
        time="Apply up to 3 months before the start date; usually decided within 3 weeks from outside the UK.",
        cost_gbp=Decimal("819"),
        cost_note="Application fee for a stay of up to 3 years.",
        source_keys=("uk_gbm_visa", "uk_gbm_eligibility", "uk_gbm_costs"),
    ),
    Requirement(
        topic="Work permit",
        title="Immigration health surcharge",
        detail="Paid with the visa application, for each year of the visa.",
        time="Paid when applying.",
        cost_gbp=Decimal("2070"),
        cost_note="£1,035 per year × 2 years.",
        source_keys=("uk_health_surcharge",),
    ),
    Requirement(
        topic="Business visit",
        title="No visa for a short business visit, but an ETA is needed",
        detail=("Swiss citizens can visit for meetings, events and conferences without a visa, "
                "for up to 6 months, but need an electronic travel authorisation (ETA) before "
                "travelling. Visitors may not do paid or unpaid work for a UK company."),
        time="Decision usually within a day, at most 3 working days. Valid for 2 years or until the passport expires.",
        cost_gbp=Decimal("20"),
        cost_note="ETA fee.",
        source_keys=("uk_visit_swiss", "uk_eta", "uk_eta_apply"),
    ),
    Requirement(
        topic="Passport",
        title="Passport valid for the whole stay",
        detail=("Swiss citizens need a passport to visit; a national ID card is accepted only in "
                "special cases (for example EU Settlement Scheme status). It must be valid for the "
                "whole time in the UK. The ETA is linked to the passport used to apply."),
        time="Check before booking the business visit.",
        cost_gbp=Decimal("0"),
        cost_note="No UK fee.",
        source_keys=("uk_visit_swiss", "uk_eta_apply"),
    ),
    Requirement(
        topic="Passport",
        title="Valid passport for the visa application",
        detail="The visa application needs a valid passport or other document showing identity and nationality.",
        time="Needed when applying.",
        cost_gbp=Decimal("0"),
        cost_note="No UK fee.",
        source_keys=("uk_gbm_documents",),
    ),
    Requirement(
        topic="Employer duties",
        title="UK subsidiary gets a sponsor licence",
        detail="Only a licensed sponsor can assign a certificate of sponsorship.",
        time="Most decisions within 8 weeks; priority decision within 10 working days for an extra £750.",
        cost_gbp=Decimal("1682"),
        cost_note="Worker licence, medium or large sponsor (£611 if small or charitable).",
        source_keys=("uk_sponsor_licence",),
    ),
    Requirement(
        topic="Employer duties",
        title="Assign a certificate of sponsorship",
        detail="An electronic record with the job and salary. The employee must apply for the visa within 3 months of getting it.",
        time="Once the licence is granted.",
        cost_gbp=Decimal("525"),
        cost_note="Per certificate, paid by the sponsor.",
        source_keys=("uk_certificate_of_sponsorship", "uk_gbm_eligibility"),
    ),
    Requirement(
        topic="Employer duties",
        title="Pay the immigration skills charge",
        detail=("Due when assigning the certificate for a Senior or Specialist Worker. The "
                "exemption for transferred workers covers EU nationals, not Swiss nationals."),
        time="Paid when assigning the certificate.",
        cost_gbp=Decimal("2640"),
        cost_note="Medium or large sponsor: £1,320 for the first 12 months + £660 × 2 further 6-month periods (£960 if small).",
        source_keys=("uk_skills_charge",),
    ),
    Requirement(
        topic="Employer duties",
        title="Keep sponsor duties during the assignment",
        detail=("Do right-to-work checks and keep copies of documents, report significant changes "
                "within 20 working days, and tell UK Visas and Immigration if the worker breaks "
                "the visa conditions."),
        time="Throughout the assignment.",
        cost_gbp=Decimal("0"),
        cost_note="No fee.",
        source_keys=("uk_sponsor_duties",),
    ),
    Requirement(
        topic="Employer duties",
        title="Request a Swiss certificate of coverage (social security)",
        detail="Keeps the employee in Swiss social security for up to 2 years, so no UK National Insurance is due.",
        time="Before the assignment starts.",
        cost_gbp=Decimal("0"),
        cost_note="No UK fee.",
        source_keys=("uk_ss_from_switzerland",),
    ),
]

TOPICS = ["Work permit", "Business visit", "Passport", "Employer duties"]


def requirements_by_topic(requirements=SWITZERLAND_TO_UK):
    """Group the requirements under the four topics, in a fixed order."""
    return [(topic, [r for r in requirements if r.topic == topic]) for topic in TOPICS]


def total_cost(requirements=SWITZERLAND_TO_UK) -> Decimal:
    return sum((r.cost_gbp for r in requirements), Decimal("0"))


PLANNING_NOTE = (
    "Start about 3 months before 6 April 2026: the sponsor licence can take up to 8 weeks, "
    "then the certificate of sponsorship is assigned, and the visa decision takes about 3 weeks. "
    "The visa can be applied for at most 3 months before the start date."
)
PLANNING_SOURCE_KEYS = ("uk_sponsor_licence", "uk_gbm_visa")