# IncomeHelper.py - Quick Reference Guide

## Module Overview
Financial planning tool for salary projections, tax calculations, investment tracking, and comprehensive financial analytics.

---

## Classes

### TaxCalculator
Computes income tax using progressive tax slabs with cess.

**Key Methods:**
- `__init__(slabs, cess_rate, std_deduction)`: Initialize with custom tax parameters
- `compute_tax(gross_yearly) -> float`: Calculate total tax for given salary

**Example:**
```python
calc = TaxCalculator()
tax = calc.compute_tax(1_000_000)  # Calculate tax for ₹10 lakhs
```

---

### SalaryInvestmentProjector
Projects salary growth, investments, and returns over multiple years.

**Key Methods:**
- `__init__(tax_calc, salary_hike_rate, salary_cap, invest_monthly_cap)`: Initialize projector
- `project_year(...)`: Calculate metrics for one year
- `run_projection(start_gross, years, start_monthly_investment, invest_hike_percent, expected_return, other_deductions)`: Run multi-year projection

**Example:**
```python
projector = SalaryInvestmentProjector()
projections = projector.run_projection(
    start_gross=1_000_000,
    years=10,
    start_monthly_investment=50_000,
    invest_hike_percent=10,
    expected_return=12,
    other_deductions=5_000
)
```

---

## Functions

### Report Generation

#### save_report_text(projections, filename="report.txt")
Exports projections to formatted text file with descriptions and tabular data.

#### save_report_excel(projections, filename="report.xlsx")
Exports projections to Excel spreadsheet with proper column ordering.

#### save_report_html(projections, filename="report.html")
Exports projections to standalone HTML webpage.

---

### Analytics

#### generate_analytics(projections, out_dir="analytics")
Generates comprehensive analytics with:
- Summary statistics (CSV)
- 8+ visualization plots (PNG)
- Correlation heatmap
- CAGR calculations
- Financial metrics (savings rate, tax rate, ROI)
- Milestone tracking
- Complete data export

**Output Files:**
- `summary_stats.csv`: Statistical summary
- `gross_yearly.png`: Salary growth trend
- `cumulative_return.png`: Portfolio growth
- `investment_percentage.png`: Investment intensity
- `invested_vs_returns_yearwise.png`: Year-wise returns
- `salary_vs_invest_hike_pct.png`: Hike comparison
- `average_pie_chart.png`: Expense distribution
- `correlation_heatmap.png`: Column correlations
- `cagr.txt`: CAGR metrics
- `savings_rate.png`: Savings trend
- `effective_tax_rate.png`: Tax rate trend
- `return_percentage.png`: Portfolio return trend
- `milestones.txt`: Key financial milestones
- `projections_table.csv`: Complete data table

---

### CLI Interface

#### main()
Interactive command-line interface for collecting user inputs and running full analysis.

**User Prompts:**
1. Current yearly gross salary (INR)
2. Current monthly investment (INR)
3. Number of years to project
4. Expected % increase in investment per year
5. Expected annual return %
6. Other deductions per month (INR)

**Output:**
- `report.txt`: Formatted text report
- `report.xlsx`: Excel spreadsheet
- `report.html`: Interactive HTML page
- `analytics/`: Complete analytics directory

---

## Data Structure

### Projection Result Dictionary
Each year's projection contains:
```python
{
    "year": int,                          # Year number
    "gross_yearly": float,                # Gross salary (yearly)
    "gross_monthly": float,               # Gross salary (monthly)
    "tax_yearly": float,                  # Tax (yearly)
    "tax_monthly": float,                 # Tax (monthly)
    "net_salary_yearly": float,           # Net after tax (yearly)
    "net_monthly": float,                 # Net after tax (monthly)
    "common_ded_month": float,            # PF + Professional tax (monthly)
    "other_deductions": float,            # Other deductions (monthly)
    "total_invest_yearly": float,         # Total investment (yearly)
    "monthly_investment": float,          # Investment (monthly, capped)
    "salary_left_month": float,           # Remaining after all deductions
    "invest_percentage": float,           # % of net salary invested
    "remarks": str,                       # "High" if >40% invested, else "Good"
    "running_invest_total": float,        # Cumulative investment so far
    "cumulative_return": float,           # Portfolio value with returns
    "return_percentage": float            # % gain on invested amount
}
```

---

## Tax Calculation Details

### Default Tax Slabs (Indian System)
- Slab 1: ₹4,00,000 @ 0%
- Slab 2: ₹4,00,000 @ 5%
- Slab 3: ₹4,00,000 @ 10%
- Slab 4: ₹4,00,000 @ 15%
- Slab 5: ₹4,00,000 @ 20%
- Slab 6: ₹4,00,000 @ 25%
- Slab 7: Above ₹24 lakhs @ 30%

### Deductions
- Standard Deduction: ₹50,000
- Cess Rate: 4% (applied on computed tax)

---

## Salary Breakdown
- Basic Salary: 40% of gross
- Employee PF: 12% of basic
- Employer PF: 12% of basic
- Professional Tax: ₹200/month (yearly: ₹2,400)
- Income Tax: Progressive tax on (gross - deductions)

---

## Usage Examples

### Example 1: Quick Projection
```python
from IncomeHelper import SalaryInvestmentProjector

projector = SalaryInvestmentProjector()
projections = projector.run_projection(
    start_gross=1_500_000,
    years=5,
    start_monthly_investment=50_000,
    invest_hike_percent=15,
    expected_return=12,
    other_deductions=2_000
)

# Save reports
from IncomeHelper import save_report_text, save_report_excel, generate_analytics
save_report_text(projections)
save_report_excel(projections)
generate_analytics(projections)
```

### Example 2: Interactive CLI
```python
python IncomeHelper.py
# Follow the interactive prompts to enter your financial data
```

### Example 3: Custom Tax Rules
```python
from IncomeHelper import TaxCalculator, SalaryInvestmentProjector

# Custom tax calculator
custom_tax = TaxCalculator(
    std_deduction=100_000,
    cess_rate=0.02
)

# Use with projector
projector = SalaryInvestmentProjector(tax_calc=custom_tax)
projections = projector.run_projection(...)
```

---

## Key Metrics Explained

| Metric | Meaning |
|--------|---------|
| CAGR | Compound Annual Growth Rate of investments/returns |
| Savings Rate | Annual savings as fraction of gross salary |
| Effective Tax Rate | Tax paid as percentage of gross salary |
| ROI | Return on Investment percentage |
| Running Invest Total | Cumulative amount invested over years |
| Cumulative Return | Portfolio value including compound returns |

---

## Requirements

- Python 3.7+
- pandas
- matplotlib
- seaborn (optional, for enhanced heatmaps)
- openpyxl (required for Excel export)

---

## Notes

- All currency amounts in Indian Rupees (INR)
- Projections assume consistent annual hikes and returns
- Investment amounts are capped at ₹100,000/month
- Salary growth is capped at ₹50,00,000/year
- Compound returns calculated annually
