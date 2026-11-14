from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    title: str
    url: str


SOURCES = {
    # --- UK income tax and tax on tax ---
    "uk_income_tax_rates": Source(
        "GOV.UK: Income Tax rates and Personal Allowances",
        "https://www.gov.uk/income-tax-rates"),
    "uk_allowance_taper": Source(
        "GOV.UK: Personal Allowance if you earn more than £100,000",
        "https://www.gov.uk/income-tax-rates/income-over-100000"),
    "uk_employer_rates": Source(
        "GOV.UK: Rates and thresholds for employers 2026 to 2027",
        "https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027"),
    "hmrc_gross_up": Source(
        "HMRC PAYE Manual PAYE72028: how to gross up",
        "https://www.gov.uk/hmrc-internal-manuals/paye-manual/paye72028"),
    "hmrc_tax_equalisation": Source(
        "HMRC: Tax equalisation (HS212)",
        "https://www.gov.uk/government/publications/tax-equalisation-hs212-self-assessment-helpsheet"),
    # --- UK treatment of benefits ---
    "uk_accommodation_value": Source(
        "GOV.UK: Living accommodation, work out the value",
        "https://www.gov.uk/expenses-and-benefits-accommodation/work-out-the-value"),
    "uk_relocation_exempt": Source(
        "GOV.UK: Relocation costs, what is exempt (up to £8,000)",
        "https://www.gov.uk/expenses-and-benefits-relocation/whats-exempt"),
    "uk_relocation_report": Source(
        "GOV.UK: Relocation costs, what to report and pay",
        "https://www.gov.uk/expenses-and-benefits-relocation/what-to-report-and-pay"),
    "hmrc_temporary_accommodation": Source(
        "HMRC EIM03117: removal costs, temporary living accommodation",
        "https://www.gov.uk/hmrc-internal-manuals/employment-income-manual/eim03117"),
    # --- Social security ---
    "uk_ss_from_switzerland": Source(
        "GOV.UK: Social security for workers coming to the UK from the EEA or Switzerland",
        "https://www.gov.uk/guidance/social-security-contributions-for-workers-coming-to-the-uk-from-the-eea-or-switzerland"),
    "ch_ss_rates": Source(
        "Swiss Federal Social Insurance Office: contribution rates (AHV/IV/EO, ALV)",
        "https://sozialversicherungen.admin.ch/de/d/6877/download"),
    "ch_tax_calculator": Source(
        "Swiss Federal Tax Administration: tax calculator",
        "https://swisstaxcalculator.estv.admin.ch/"),
    # --- Immigration ---
    "uk_gbm_visa": Source(
        "GOV.UK: Senior or Specialist Worker visa (Global Business Mobility)",
        "https://www.gov.uk/senior-specialist-worker-visa"),
    "uk_gbm_eligibility": Source(
        "GOV.UK: Senior or Specialist Worker visa, eligibility",
        "https://www.gov.uk/senior-specialist-worker-visa/eligibility"),
    "uk_gbm_costs": Source(
        "GOV.UK: Senior or Specialist Worker visa, how much it costs",
        "https://www.gov.uk/senior-specialist-worker-visa/how-much-it-costs"),
    "uk_gbm_documents": Source(
        "GOV.UK: Senior or Specialist Worker visa, documents you need",
        "https://www.gov.uk/senior-specialist-worker-visa/documents-you-need-to-apply"),
    "uk_health_surcharge": Source(
        "GOV.UK: Immigration health surcharge, how much you pay",
        "https://www.gov.uk/healthcare-immigration-application/how-much-pay"),
    "uk_visit_swiss": Source(
        "GOV.UK: Visiting the UK as an EU, EEA or Swiss citizen",
        "https://www.gov.uk/guidance/visiting-the-uk-as-an-eu-eea-or-swiss-citizen"),
    "uk_eta": Source(
        "GOV.UK: Electronic travel authorisation (ETA)",
        "https://www.gov.uk/eta"),
    "uk_eta_apply": Source(
        "GOV.UK: Apply for an ETA",
        "https://www.gov.uk/eta/apply"),
    "uk_sponsor_licence": Source(
        "GOV.UK: Apply for a sponsor licence",
        "https://www.gov.uk/uk-visa-sponsorship-employers/apply-for-your-licence"),
    "uk_certificate_of_sponsorship": Source(
        "GOV.UK: Certificates of sponsorship",
        "https://www.gov.uk/uk-visa-sponsorship-employers/certificates-of-sponsorship"),
    "uk_skills_charge": Source(
        "GOV.UK: Immigration skills charge",
        "https://www.gov.uk/uk-visa-sponsorship-employers/immigration-skills-charge"),
    "uk_sponsor_duties": Source(
        "GOV.UK: Sponsor responsibilities",
        "https://www.gov.uk/uk-visa-sponsorship-employers/your-responsibilities"),
}


def sources(*keys):
    return [SOURCES[key] for key in keys]