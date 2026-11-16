# Assignment cost estimate: Switzerland → UK

A small Django tool that shows what it costs an employer, and how long it takes, to send an
employee from Zurich to London for two years when the employer pays the UK tax.

- **Tab 1, Cost estimate:** home pay, assignment benefits, UK tax including tax on tax,
  social security and hypothetical Swiss deductions, per year and for the whole assignment.
- **Tab 2, Immigration:** work permit, business visit, passport and employer duties, with time and cost.

Every tax rule and immigration requirement links to the official page it comes from.

**Loom video:** LOOM-LINK

## Install and run

You need Python 3.12 or newer and Git.

Windows (PowerShell):

```
git clone https://github.com/EISAGHANI/cost-estimation-tool.git
cd cost-estimation-tool
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

macOS or Linux: the same, but create and activate the environment with
`python3 -m venv .venv` and `source .venv/bin/activate`.

Open http://127.0.0.1:8000. The form is pre-filled with the test case from the brief:
press **Calculate** to get the cost table for both years.

No API keys, passwords or environment variables are needed. For a production server you
would set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=0`.

## Run the tests

```
python manage.py test
```

## How it works

- `estimates/tax/` holds the rules in plain Python: UK income tax 2026/27 (`uk.py`), tax on tax
  (`gross_up.py`), which country's social security applies (`social_security.py`), hypothetical
  Swiss deductions (`swiss.py`) and the UK treatment of each benefit (`benefits.py`).
- `estimates/calculator.py` builds the four-section table for each year.
- `estimates/immigration.py` lists the immigration requirements with time, cost and source.
- `estimates/sources.py` holds every official link in one place.
- Django (`forms.py`, `views.py`, templates) only handles input checking and display.

Tax on tax: I is the UK taxable pay before tax (home pay minus the hypothetical Swiss deductions,
plus taxable benefits). The UK tax T is found by iteration until T = UKTax(I + T) to within 1p.

Social security: the employee is posted from Switzerland for 24 months, within the 2-year limit for
detached workers, so Swiss contributions continue with a certificate of coverage and no UK National
Insurance is due.

Hypothetical Swiss income tax: CHF AMOUNT, from the Swiss Federal Tax Administration calculator
(tax year 2026, city of Zurich, single, no children, no church tax, salary + bonus CHF 170,000).

## Limitations

- Covers Switzerland → UK for 1 or 2 years. Longer postings, where UK National Insurance applies, are not modelled.
- Uses UK 2026/27 rates for both years and a fixed exchange rate, as the brief allows.
- This is an exercise, not tax advice.

## AI tools used

- **Claude (Anthropic):** to find and compare official GOV.UK, HMRC and Swiss federal pages for
  the tax, social security and immigration rules; to explain tax equalisation and the gross-up
  method; and as a step-by-step guide while I learned Django. I checked every link the tool generated and completed the project myself.