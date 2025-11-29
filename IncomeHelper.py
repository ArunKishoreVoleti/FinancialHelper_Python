"""
Income Helper Module: Salary Projection with Tax Calculations, Investment Tracking, and Analytics.

This module provides comprehensive financial planning tools for salary projections, tax calculations,
investment tracking, and advanced analytics. It includes support for:
  - Income tax calculations using progressive tax slabs and cess
  - Salary projections with annual hikes and investment growth
  - Multi-year financial forecasting with compound returns
  - Export to multiple formats (TXT, Excel, HTML)
  - Advanced analytics including CAGR, correlation analysis, and visualization

Author: Arun Kishore Voleti
Date: 2025-11-29
Version: 1.0
"""

import math
import os
from typing import List, Dict, Tuple, Optional

import pandas as pd
import matplotlib.pyplot as plt


class TaxCalculator:
    """
    Tax calculator for computing income tax based on progressive tax slabs and cess.
    
    Supports Indian tax system with configurable tax slabs, standard deduction, and cess rate.
    Attributes:
        STD_DEDUCTION (float): Standard deduction amount (default: ₹50,000).
        CESS_RATE (float): Cess rate applied on computed tax (default: 4%).
        SLABS (List[Tuple[float, float]]): List of (slab_amount, rate) tuples defining tax brackets.
    """
    STD_DEDUCTION = 50_000
    CESS_RATE = 0.04
    SLABS = [
        (400_000, 0.00),
        (400_000, 0.05),
        (400_000, 0.10),
        (400_000, 0.15),
        (400_000, 0.20),
        (400_000, 0.25),
        (float("inf"), 0.30),
    ]

    def __init__(
        self,
        slabs: Optional[List[Tuple[float, float]]] = None,
        cess_rate: Optional[float] = None,
        std_deduction: Optional[float] = None
    ) -> None:
        """
        Initialize a TaxCalculator with customizable tax parameters.
        
        Args:
            slabs: Optional list of (slab_amount, tax_rate) tuples. If None, uses class default.
            cess_rate: Optional cess rate (0.0 to 1.0). If None, uses class default (4%).
            std_deduction: Optional standard deduction amount. If None, uses class default (₹50,000).
        """
        self.slabs = slabs if slabs is not None else self.SLABS
        self.cess_rate = cess_rate if cess_rate is not None else self.CESS_RATE
        self.std_deduction = std_deduction if std_deduction is not None else self.STD_DEDUCTION

    def compute_tax(self, gross_yearly: float) -> float:
        """
        Compute total income tax for a given gross yearly income.
        
        Applies standard deduction, then calculates tax using progressive slabs,
        and finally applies cess on the computed tax amount.
        
        Args:
            gross_yearly: Gross yearly salary in INR (before any deductions).
        
        Returns:
            Total tax amount including cess, in INR.
        
        Examples:
            >>> calc = TaxCalculator()
            >>> tax = calc.compute_tax(1_000_000)
            >>> print(f"Tax for ₹1,000,000: ₹{tax:,.0f}")
        """
        # Calculate taxable income after standard deduction
        taxable_income = max(0.0, gross_yearly - self.std_deduction)
        if taxable_income <= 0:
            return 0.0
        
        # Apply progressive tax slabs
        remaining = taxable_income
        tax = 0.0
        for slab_amount, rate in self.slabs:
            take = min(remaining, slab_amount)
            if take <= 0:
                break
            tax += take * rate
            remaining -= take
        
        # Apply cess (additional tax on computed tax)
        tax += tax * self.cess_rate
        return tax


class SalaryInvestmentProjector:
    """
    Multi-year salary and investment projection engine with tax and deduction calculations.
    
    Projects salary growth, investment accumulation, compound returns, and various financial
    metrics over multiple years. Supports annual salary hikes and investment increases.
    
    Attributes:
        SALARY_CAP (float): Maximum salary cap to prevent unbounded growth (default: ₹50,00,000).
        INVEST_MONTHLY_CAP (float): Maximum monthly investment amount (default: ₹100,000).
        SALARY_HIKE_RATE (float): Annual salary hike rate (default: 5%).
        PROF_TAX_MONTH (float): Monthly professional tax amount (default: ₹200).
    """

    
    SALARY_CAP = 5_000_000
    INVEST_MONTHLY_CAP = 100_000
    SALARY_HIKE_RATE = 0.05
    PROF_TAX_MONTH = 200

    def __init__(
        self,
        tax_calc: Optional[TaxCalculator] = None,
        salary_hike_rate: Optional[float] = None,
        salary_cap: Optional[float] = None,
        invest_monthly_cap: Optional[float] = None
    ) -> None:
        """
        Initialize a SalaryInvestmentProjector with optional custom parameters.
        
        Args:
            tax_calc: Custom TaxCalculator instance. If None, creates default TaxCalculator.
            salary_hike_rate: Annual salary hike rate (0.0 to 1.0). If None, uses class default (5%).
            salary_cap: Maximum salary cap to prevent unbounded growth. If None, uses class default.
            invest_monthly_cap: Monthly investment cap. If None, uses class default (₹100,000).
        """
        self.tax_calc = tax_calc if tax_calc is not None else TaxCalculator()
        self.salary_hike_rate = salary_hike_rate if salary_hike_rate is not None else self.SALARY_HIKE_RATE
        self.salary_cap = salary_cap if salary_cap is not None else self.SALARY_CAP
        self.invest_monthly_cap = invest_monthly_cap if invest_monthly_cap is not None else self.INVEST_MONTHLY_CAP

    def project_year(
        self,
        gross_yearly: float,
        monthly_investment: float,
        other_deductions: float,
        running_invest_total: float,
        cumulative_return: float,
        expected_return: float
    ) -> Tuple[Dict[str, float], float, float]:
        """
        Project financial metrics for a single year.
        
        Calculates salary components (gross, net, tax, deductions), investment tracking,
        and portfolio returns for one year. This method is called iteratively for multi-year projections.
        
        Args:
            gross_yearly: Gross yearly salary in INR.
            monthly_investment: Monthly investment amount in INR.
            other_deductions: Other monthly deductions (e.g., loan EMI) in INR.
            running_invest_total: Cumulative investment amount up to this year.
            cumulative_return: Portfolio value including returns up to this year.
            expected_return: Expected annual return rate (as a percentage, e.g., 12 for 12%).
        
        Returns:
            Tuple containing:
                - Dictionary with year-wise financial metrics (gross, net, tax, investment, etc.)
                - Updated running_invest_total
                - Updated cumulative_return
        """
        # Calculate salary components
        basic = 0.40 * gross_yearly  # Basic salary as 40% of gross
        emp_pf = 0.12 * basic  # Employee provident fund
        employer_pf = 0.12 * basic  # Employer provident fund contribution
        prof_tax_yearly = self.PROF_TAX_MONTH * 12  # Annual professional tax
        tax_yearly = self.tax_calc.compute_tax(gross_yearly)  # Compute income tax

        # Calculate total common deductions (excluding voluntary investment)
        common_ded_yearly = emp_pf + employer_pf + prof_tax_yearly
        common_ded_month = common_ded_yearly / 12

        # Calculate net salary
        net_salary_yearly = gross_yearly - tax_yearly
        net_monthly = net_salary_yearly / 12

        # Calculate monthly breakdown
        gross_monthly = gross_yearly / 12
        tax_monthly = tax_yearly / 12
        monthly_investment_capped = min(monthly_investment, self.invest_monthly_cap)

        # Calculate remaining salary after all deductions and investments
        salary_left_month = net_monthly - monthly_investment_capped - common_ded_month - other_deductions
        invest_percentage = (monthly_investment_capped / net_monthly * 100.0) if net_monthly > 0 else 0

        # Update investment totals
        total_invest_yearly = monthly_investment_capped * 12
        running_invest_total += total_invest_yearly

        # Calculate compound returns
        cumulative_return = (cumulative_return + total_invest_yearly) * (1 + expected_return / 100)
        return_percentage = ((cumulative_return - running_invest_total) /
                             running_invest_total * 100) if running_invest_total > 0 else 0

        # Determine investment intensity remark
        remarks = "High" if invest_percentage > 40 else "Good"

        # Build result dictionary with all metrics
        result = {
            "year": 0,
            "gross_yearly": round(gross_yearly),
            "gross_monthly": round(gross_monthly),
            "tax_yearly": round(tax_yearly),
            "tax_monthly": round(tax_monthly),
            "net_salary_yearly": round(net_salary_yearly),
            "net_monthly": round(net_monthly),
            "common_ded_month": round(common_ded_month),
            "other_deductions": round(other_deductions),
            "total_invest_yearly": round(total_invest_yearly),
            "monthly_investment": round(monthly_investment_capped),
            "salary_left_month": round(salary_left_month),
            "invest_percentage": round(invest_percentage, 2),
            "remarks": remarks,
            "running_invest_total": round(running_invest_total),
            "cumulative_return": round(cumulative_return),
            "return_percentage": round(return_percentage, 2)
        }

        return result, running_invest_total, cumulative_return

    def run_projection(
        self,
        start_gross: float,
        years: int,
        start_monthly_investment: float,
        invest_hike_percent: float,
        expected_return: float,
        other_deductions: float
    ) -> List[Dict[str, float]]:
        """
        Run multi-year salary and investment projection.
        
        Iteratively projects financial metrics for each year, applying annual salary hikes
        and investment increases while tracking compound returns.
        
        Args:
            start_gross: Starting gross yearly salary in INR.
            years: Number of years to project (positive integer).
            start_monthly_investment: Starting monthly investment amount in INR.
            invest_hike_percent: Annual investment increase rate as a percentage (e.g., 10 for 10%).
            expected_return: Expected annual portfolio return as a percentage (e.g., 12 for 12%).
            other_deductions: Fixed monthly deductions in INR (e.g., loan EMI).
        
        Returns:
            List of dictionaries, each containing year-wise financial metrics.
            
        Examples:
            >>> projector = SalaryInvestmentProjector()
            >>> projections = projector.run_projection(
            ...     start_gross=1_000_000,
            ...     years=10,
            ...     start_monthly_investment=50_000,
            ...     invest_hike_percent=10,
            ...     expected_return=12,
            ...     other_deductions=5_000
            ... )
            >>> print(f"Year 1 net salary: ₹{projections[0]['net_salary_yearly']:,}")
        """
        results: List[Dict[str, float]] = []
        gross = float(start_gross)
        monthly_invest = float(start_monthly_investment)
        running_invest_total = 0.0
        cumulative_return = 0.0

        for y in range(1, years + 1):
            # Project current year
            res, running_invest_total, cumulative_return = self.project_year(
                gross, monthly_invest, other_deductions,
                running_invest_total, cumulative_return, expected_return
            )
            res["year"] = y
            results.append(res)

            # Apply annual hikes for next year (capped at salary_cap and invest_monthly_cap)
            gross = min(gross * (1 + self.salary_hike_rate), self.SALARY_CAP)
            monthly_invest = min(
                monthly_invest * (1 + invest_hike_percent / 100),
                self.invest_monthly_cap
            )

        return results


# ============================================================================
# Report Generation Functions: Text, Excel, and HTML exports
# ============================================================================

def save_report_text(projections: List[Dict[str, float]], filename: str = "report.txt") -> None:
    """
    Export projections to a formatted plain text file.
    
    Creates a comprehensive text report with column descriptions and formatted tabular data.
    Columns are left-aligned with fixed widths for readability.
    
    Args:
        projections: List of yearly projection dictionaries from run_projection().
        filename: Output filename for the text report (default: "report.txt").
    
    Returns:
        None. Prints success message upon completion.
        
    Examples:
        >>> projections = projector.run_projection(...)
        >>> save_report_text(projections, "my_report.txt")
        # Creates a formatted text file with salary and investment data
    """
    widths = {
        "year": 5,
        "gross_yearly": 10,
        "gross_monthly": 10,
        "tax_yearly": 8,
        "tax_monthly": 8,
        "net_salary_yearly": 8,
        "net_monthly": 8,
        "common_ded_month": 14,
        "other_deductions": 13,
        "total_invest_yearly": 10,
        "monthly_investment": 10,
        "salary_left_month": 13,
        "invest_percentage": 10,
        "remarks": 8,
        "running_invest_total": 16,
        "cumulative_return": 18,
        "return_percentage": 12
    }

    # Column descriptions explaining what each metric represents
    descriptions = [
        ("Gross/Y", "Total salary earned in the year before deductions."),
        ("Gross/M", "Monthly salary before deductions."),
        ("Tax/Y", "Income tax calculated on yearly income."),
        ("Tax/M", "Income tax applicable per month."),
        ("Net/Y", "Actual salary received after tax deductions."),
        ("Net/M", "Monthly take-home after tax deductions."),
        ("Common Ded/M", "PF employee + PF employer + professional tax per month."),
        ("Other Ded/M", "Any other deductions you entered (monthly)."),
        ("Invest/Y", "Total amount invested per year."),
        ("Invest/M", "Monthly investment amount after cap."),
        ("Salary Left/M", "Amount remaining each month after investment and deductions."),
        ("Invest %", "Investment percentage of monthly take-home."),
        ("Running Invest/Y", "Total money invested so far over the years."),
        ("Cumulative Return/Y", "Total portfolio value including returns."),
        ("Return %", "Percentage gain made on total invested amount.")
    ]

    with open(filename, "w", encoding="utf-8") as f:
        # Write column descriptions header
        f.write("==== Column Descriptions ====\n")
        for col, desc in descriptions:
            f.write(f"{col:<20}: {desc}\n")
        f.write("\n")

        # Format and write table header
        header = (
            f"{'Year':<{widths['year']}}|"
            f"{'Gross/Y':<{widths['gross_yearly']}}|"
            f"{'Gross/M':<{widths['gross_monthly']}}|"
            f"{'Tax/Y':<{widths['tax_yearly']}}|"
            f"{'Tax/M':<{widths['tax_monthly']}}|"
            f"{'Net/Y':<{widths['net_salary_yearly']}}|"
            f"{'Net/M':<{widths['net_monthly']}}|"
            f"{'Common Ded/M':<{widths['common_ded_month']}}|"
            f"{'Other Ded/M':<{widths['other_deductions']}}|"
            f"{'Invest/Y':<{widths['total_invest_yearly']}}|"
            f"{'Invest/M':<{widths['monthly_investment']}}|"
            f"{'Invest %':<{widths['invest_percentage']}}|"
            f"{'Salary Left/M':<{widths['salary_left_month']}}|"
            f"{'Remarks':<{widths['remarks']}}|"
            f"{'Running Invest/Y':<{widths['running_invest_total']}}|"
            f"{'Cumulative Return/Y':<{widths['cumulative_return']}}|"
            f"{'Return %':<{widths['return_percentage']}}"
        )

        f.write(header + "\n")
        f.write("-" * len(header) + "\n")

        # Write data rows for each year's projection
        for p in projections:
            row = (
                f"{p['year']:<{widths['year']}}|"
                f"{p['gross_yearly']:<{widths['gross_yearly']}}|"
                f"{p['gross_monthly']:<{widths['gross_monthly']}}|"
                f"{p['tax_yearly']:<{widths['tax_yearly']}}|"
                f"{p['tax_monthly']:<{widths['tax_monthly']}}|"
                f"{p['net_salary_yearly']:<{widths['net_salary_yearly']}}|"
                f"{p['net_monthly']:<{widths['net_monthly']}}|"
                f"{p['common_ded_month']:<{widths['common_ded_month']}}|"
                f"{p['other_deductions']:<{widths['other_deductions']}}|"
                f"{p['total_invest_yearly']:<{widths['total_invest_yearly']}}|"
                f"{p['monthly_investment']:<{widths['monthly_investment']}}|"
                f"{p['invest_percentage']:<{widths['invest_percentage']}.2f}|"
                f"{p['salary_left_month']:<{widths['salary_left_month']}}|"
                f"{p['remarks']:<{widths['remarks']}}|"
                f"{p['running_invest_total']:<{widths['running_invest_total']}}|"
                f"{p['cumulative_return']:<{widths['cumulative_return']}}|"
                f"{p['return_percentage']:<{widths['return_percentage']}.2f}"
            )
            f.write(row + "\n")

    print(f"Report saved to {filename}")


def save_report_excel(projections: List[Dict[str, float]], filename: str = "report.xlsx") -> None:
    """
    Export projections to an Excel spreadsheet file.
    
    Creates an Excel file with properly ordered columns for easy viewing and analysis
    in Excel or compatible spreadsheet applications.
    
    Args:
        projections: List of yearly projection dictionaries from run_projection().
        filename: Output filename for the Excel report (default: "report.xlsx").
    
    Returns:
        None. Prints success or error message.
        
    Raises:
        Implicit exception if pandas or openpyxl is not installed.
    """
    df = pd.DataFrame(projections)
    # Ensure 'year' column appears first, followed by other columns
    cols = ["year"] + [c for c in df.columns if c != "year"]
    df = df[cols]
    try:
        df.to_excel(filename, index=False)
        print(f"Excel report saved to {filename}")
    except Exception as e:
        print(f"Failed to save Excel file: {e}")


def save_report_html(projections: List[Dict[str, float]], filename: str = "report.html") -> None:
    """
    Export projections to an HTML webpage with styled table.
    
    Creates a standalone HTML file that can be opened in any web browser,
    with a centered table format for clean presentation.
    
    Args:
        projections: List of yearly projection dictionaries from run_projection().
        filename: Output filename for the HTML report (default: "report.html").
    
    Returns:
        None. Prints success or error message.
    """
    df = pd.DataFrame(projections)
    html = df.to_html(index=False, justify="center")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Write HTML document structure with metadata
            f.write("<html><head><meta charset='utf-8'><title>Salary Projection Report</title></head><body>\n")
            f.write("<h2>Salary Projection Report</h2>\n")
            f.write(html)
            f.write("\n</body></html>")
        print(f"HTML report saved to {filename}")
    except Exception as e:
        print(f"Failed to save HTML file: {e}")


def generate_analytics(projections: List[Dict[str, float]], out_dir: str = "analytics") -> None:
    """
    Generate comprehensive financial analytics with visualizations and reports.
    
    Creates an analytics directory containing:
    - Summary statistics (CSV)
    - Multiple trend visualizations (PNG): gross salary, cumulative returns, investment %, etc.
    - Correlation heatmap for numeric columns
    - CAGR (Compound Annual Growth Rate) calculations
    - Key financial metrics: savings rate, effective tax rate, ROI trends
    - Milestone tracking: when returns exceed invested amount
    - Complete projection table (CSV) with all computed columns
    
    The function generates seaborn heatmaps when available, with matplotlib fallback.
    
    Args:
        projections: List of yearly projection dictionaries from run_projection().
        out_dir: Output directory for analytics files (default: "analytics"). Directory is created if it doesn't exist.
    
    Returns:
        None. Prints progress messages and saves files to out_dir.
        
    Side Effects:
        - Creates multiple PNG files for visualizations
        - Creates CSV files for data export
        - Creates text files for metrics (CAGR, milestones)
        - Attempts to import seaborn; uses matplotlib fallback if unavailable
    """
    # Attempt to import seaborn for enhanced heatmap visualization (optional)
    try:
        import seaborn as sns
    except Exception:
        sns = None

    if not projections:
        print("No projections provided to generate analytics.")
        return

    # Create output directory for analytics files
    os.makedirs(out_dir, exist_ok=True)

    # Convert projections to DataFrame and ensure numeric types
    df = pd.DataFrame(projections)
    numeric_cols = [
        "gross_yearly", "gross_monthly", "tax_yearly", "tax_monthly", "net_salary_yearly",
        "net_monthly", "common_ded_month", "other_deductions", "total_invest_yearly",
        "monthly_investment", "salary_left_month", "invest_percentage", "running_invest_total",
        "cumulative_return", "return_percentage"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Set year as index for time-series analysis
    if "year" in df.columns:
        df.set_index("year", inplace=True)

    # ========================== SUMMARY STATISTICS ==========================
    print("\n--- Summary Statistics ---")
    numeric_df = df.select_dtypes(include="number")
    numeric_stats = numeric_df.describe().T
    print(numeric_stats[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]])

    stats_csv = os.path.join(out_dir, "summary_stats.csv")
    numeric_stats.to_csv(stats_csv)
    print(f"Summary statistics saved to {stats_csv}")

    # ========================== PLOTS & VISUALIZATION HELPER ==========================
    def _save_fig(fig_path: str) -> None:
        """
        Helper function to save matplotlib figures with error handling.
        
        Args:
            fig_path: Absolute path where the figure should be saved.
        """
        try:
            plt.tight_layout()
            plt.savefig(fig_path)
            plt.close()
            print(f"Saved plot: {fig_path}")
        except Exception as e:
            print(f"Failed to save {fig_path}: {e}")
            plt.close()

    # ========================== INDIVIDUAL VISUALIZATIONS ==========================
    
    # 1) Gross Yearly Salary Trend
    if "gross_yearly" in numeric_df.columns:
        plt.figure()
        numeric_df["gross_yearly"].plot(marker="o", title="Gross Yearly Salary")
        plt.xlabel("Year"); plt.ylabel("Amount (INR)")
        _save_fig(os.path.join(out_dir, "gross_yearly.png"))

    # 2) Cumulative Return Over Years
    if "cumulative_return" in numeric_df.columns:
        plt.figure()
        numeric_df["cumulative_return"].plot(marker="o", title="Cumulative Return Over Years")
        plt.xlabel("Year"); plt.ylabel("Amount (INR)")
        _save_fig(os.path.join(out_dir, "cumulative_return.png"))

    # 3) Investment Percentage of Net Monthly Salary
    if "invest_percentage" in numeric_df.columns:
        plt.figure()
        numeric_df["invest_percentage"].plot(marker="o", title="Investment % of Net Monthly")
        plt.xlabel("Year"); plt.ylabel("% of Net Salary")
        _save_fig(os.path.join(out_dir, "investment_percentage.png"))

    # ========================== INVESTED VS RETURNS (Year-wise) ==========================
    # Calculates yearly return separately, not cumulative, for better insight
    if {"cumulative_return", "total_invest_yearly"}.issubset(numeric_df.columns):
        # Calculate previous cumulative (0 for year 1)
        prev_cum = numeric_df["cumulative_return"].shift(1).fillna(0)
        # Yearly return = current cumulative - (previous cumulative + current year investment)
        yearly_return = numeric_df["cumulative_return"] - (prev_cum + numeric_df["total_invest_yearly"])
        numeric_df["yearly_return"] = yearly_return

        plt.figure()
        plt.plot(numeric_df.index, numeric_df["total_invest_yearly"], marker="o", label="Invested (Year)")
        plt.plot(numeric_df.index, numeric_df["yearly_return"], marker="o", label="Return (Year)")
        plt.title("Invested vs Returns (Year-wise)")
        plt.xlabel("Year"); plt.ylabel("Amount (INR)")
        plt.grid(True); plt.legend()
        _save_fig(os.path.join(out_dir, "invested_vs_returns_yearwise.png"))

    # ========================== SALARY HIKE % VS INVESTMENT HIKE % ==========================
    if "gross_yearly" in numeric_df.columns and "total_invest_yearly" in numeric_df.columns:
        # Calculate percentage change year-over-year for both salary and investment
        numeric_df["salary_hike_pct"] = numeric_df["gross_yearly"].pct_change() * 100
        numeric_df["invest_hike_pct"] = numeric_df["total_invest_yearly"].pct_change() * 100

        plt.figure()
        plt.plot(numeric_df.index, numeric_df["salary_hike_pct"], marker="o", label="Salary Hike %")
        plt.plot(numeric_df.index, numeric_df["invest_hike_pct"], marker="o", label="Investment Hike %")
        plt.title("Salary Hike % vs Investment Hike %")
        plt.xlabel("Year"); plt.ylabel("Percentage %")
        plt.grid(True); plt.legend()
        _save_fig(os.path.join(out_dir, "salary_vs_invest_hike_pct.png"))

    # ========================== PIE CHART: AVERAGE EXPENSE DISTRIBUTION ==========================
    # Compute average components for the pie chart visualization
    avg_salary = numeric_df["gross_yearly"].mean() if "gross_yearly" in numeric_df.columns else 0
    avg_tax = numeric_df["tax_yearly"].mean() if "tax_yearly" in numeric_df.columns else 0
    avg_common = (numeric_df["common_ded_month"].mean() * 12) if "common_ded_month" in numeric_df.columns else 0
    avg_other = (numeric_df["other_deductions"].mean() * 12) if "other_deductions" in numeric_df.columns else 0
    avg_invested = numeric_df["total_invest_yearly"].mean() if "total_invest_yearly" in numeric_df.columns else 0
    avg_total_deductions = avg_tax + avg_common + avg_other

    # Prepare pie chart data
    pie_labels = ["Avg Salary", "Avg Total Deductions", "Avg Common Deductions", "Avg Tax", "Avg Invested"]
    pie_values = [avg_salary, avg_total_deductions, avg_common, avg_tax, avg_invested]

    # Create pie chart only if data is available
    if sum(pie_values) > 0:
        plt.figure()
        plt.pie(pie_values, labels=pie_labels, autopct="%1.1f%%", startangle=90)
        plt.title("Average Expense Distribution")
        _save_fig(os.path.join(out_dir, "average_pie_chart.png"))
    else:
        print("Pie chart skipped (no numeric data).")

    # ========================== CORRELATION HEATMAP ==========================
    # Analyzes relationships between numeric columns (safe: only numeric columns)
    corr_df = numeric_df.dropna(axis=1, how="all")  # Remove completely empty columns
    if corr_df.shape[1] >= 2:
        corr_mat = corr_df.corr()
        plt.figure(figsize=(10, 6))
        if sns is not None:
            # Use seaborn for enhanced heatmap if available
            sns.heatmap(corr_mat, annot=True, cmap="Blues")
        else:
            # Fallback to matplotlib-only implementation
            plt.imshow(corr_mat, cmap="Blues", aspect="auto")
            plt.colorbar()
            ticks = range(len(corr_mat.columns))
            plt.xticks(ticks, corr_mat.columns, rotation=45, ha="right")
            plt.yticks(ticks, corr_mat.columns)
            # Add correlation values as text annotations
            for i in range(len(corr_mat.columns)):
                for j in range(len(corr_mat.columns)):
                    plt.text(j, i, f"{corr_mat.iloc[i, j]:.2f}", ha="center", va="center", color="black")
        plt.title("Correlation Matrix (Numeric Columns Only)")
        _save_fig(os.path.join(out_dir, "correlation_heatmap.png"))
    else:
        print("Not enough numeric columns for correlation heatmap.")

    # ========================== CAGR CALCULATIONS ==========================
    # Calculate Compound Annual Growth Rate for invested amounts and portfolio returns
    if "running_invest_total" in numeric_df.columns and "cumulative_return" in numeric_df.columns:
        first_inv = numeric_df["running_invest_total"].iloc[0]
        last_inv = numeric_df["running_invest_total"].iloc[-1]
        first_ret = numeric_df["cumulative_return"].iloc[0]
        last_ret = numeric_df["cumulative_return"].iloc[-1]
        yrs = max(1, len(numeric_df))

        def calc_cagr(start: float, end: float, yrs: int) -> float:
            """
            Calculate CAGR (Compound Annual Growth Rate).
            
            Args:
                start: Starting value
                end: Ending value
                yrs: Number of years
            
            Returns:
                CAGR as a percentage (e.g., 12.5 for 12.5%)
            """
            try:
                return ((end / start) ** (1 / yrs) - 1) * 100 if start > 0 and end > 0 else 0.0
            except Exception:
                return 0.0

        invest_cagr = calc_cagr(first_inv, last_inv, yrs)
        return_cagr = calc_cagr(first_ret, last_ret, yrs)

        # Save CAGR calculations to text file
        with open(os.path.join(out_dir, "cagr.txt"), "w", encoding="utf-8") as f:
            f.write(f"Investment CAGR: {invest_cagr:.2f}%\n")
            f.write(f"Returns CAGR: {return_cagr:.2f}%\n")
        print(f"CAGR written to {os.path.join(out_dir, 'cagr.txt')}")

    # ========================== FINANCIAL METRICS TRENDS ==========================
    # Calculate and visualize key financial ratios and metrics over time
    
    # Savings Rate: Amount saved each month relative to yearly gross salary
    if "salary_left_month" in numeric_df.columns and "gross_yearly" in numeric_df.columns:
        numeric_df["savings_rate"] = (numeric_df["salary_left_month"] * 12) / numeric_df["gross_yearly"]
        plt.figure()
        numeric_df["savings_rate"].plot(marker="o", title="Savings Rate Over Years")
        plt.xlabel("Year"); plt.ylabel("Savings Rate (fraction)")
        _save_fig(os.path.join(out_dir, "savings_rate.png"))

    # Effective Tax Rate: Percentage of gross salary paid as tax
    if "tax_yearly" in numeric_df.columns and "gross_yearly" in numeric_df.columns:
        numeric_df["effective_tax_rate_pct"] = numeric_df["tax_yearly"] / numeric_df["gross_yearly"] * 100
        plt.figure()
        numeric_df["effective_tax_rate_pct"].plot(marker="o", title="Effective Tax Rate (%) Over Years")
        plt.xlabel("Year"); plt.ylabel("Tax %")
        _save_fig(os.path.join(out_dir, "effective_tax_rate.png"))

    # Portfolio Return Percentage: Growth percentage of investments
    if "return_percentage" in numeric_df.columns:
        plt.figure()
        numeric_df["return_percentage"].plot(marker="o", title="Return % (Portfolio) Over Years")
        plt.xlabel("Year"); plt.ylabel("Return %")
        _save_fig(os.path.join(out_dir, "return_percentage.png"))

    # ========================== KEY MILESTONES ==========================
    # Track important financial milestones such as positive returns and salary peaks
    if {"cumulative_return", "running_invest_total"}.issubset(numeric_df.columns):
        # Calculate profit (returns vs invested)
        numeric_df["profit"] = numeric_df["cumulative_return"] - numeric_df["running_invest_total"]
        crossing = numeric_df[numeric_df["profit"] > 0]
        
        with open(os.path.join(out_dir, "milestones.txt"), "w", encoding="utf-8") as f:
            # Write milestone: when portfolio returns turn positive
            if not crossing.empty:
                f.write(f"Returns surpassed investments in Year: {crossing.index[0]}\n")
            else:
                f.write("Returns have NOT surpassed investments yet.\n")
            
            # Write salary peaks and troughs
            if "net_salary_yearly" in numeric_df.columns:
                f.write(f"Max Net Salary Year: {numeric_df['net_salary_yearly'].idxmax()}\n")
                f.write(f"Min Net Salary Year: {numeric_df['net_salary_yearly'].idxmin()}\n")
        print(f"Milestones written to {os.path.join(out_dir, 'milestones.txt')}")

    # ========================== EXPORT FINAL DATA ==========================
    # Save complete projection table with all computed columns for further analysis
    numeric_df.to_csv(os.path.join(out_dir, "projections_table.csv"))
    print(f"Projection table saved to {os.path.join(out_dir, 'projections_table.csv')}")

    print("\nAdvanced analytics generated successfully.")


# ============================================================================
# Command-Line Interface (CLI) Main Function
# ============================================================================

def main() -> None:
    """
    Interactive CLI for collecting user input and generating financial projections.
    
    Prompts the user for financial parameters, runs the projection, and generates
    reports in multiple formats (text, Excel, HTML) along with comprehensive analytics.
    
    User Inputs:
        - Current yearly gross salary (INR)
        - Current monthly investment amount (INR)
        - Number of years to project
        - Expected annual investment hike percentage
        - Expected annual portfolio return percentage
        - Other fixed monthly deductions (INR)
    
    Outputs:
        - report.txt: Formatted text report
        - report.xlsx: Excel spreadsheet
        - report.html: Interactive HTML page
        - analytics/: Directory containing visualizations and metrics
    
    Returns:
        None. Exits early on input error.
    """
    try:
        # Collect user inputs with validation
        gross = float(input("Enter current yearly gross salary (INR): ").strip())
        monthly_invest = float(input("Enter current monthly investment (INR): ").strip())
        years = int(input("Enter number of years to project: ").strip())
        invest_hike_percent = float(input("Enter expected % increase in investment per year: ").strip())
        expected_return = float(input("Enter expected annual return %: ").strip())
        other_deductions = float(input("Enter other deductions per month (INR): ").strip())
    except Exception:
        print("Invalid input. Enter correct numeric values.")
        return

    # Create projector instance with default settings
    projector = SalaryInvestmentProjector()
    
    # Run projection for specified years
    projections = projector.run_projection(
        gross, years, monthly_invest, invest_hike_percent,
        expected_return, other_deductions
    )

    # Generate and save reports in multiple formats
    save_report_text(projections, "report.txt")
    save_report_excel(projections, "report.xlsx")
    save_report_html(projections, "report.html")
    generate_analytics(projections, out_dir="analytics")

    # Print completion message
    print("\nAll done. Files created:\n - report.txt\n - report.xlsx\n - report.html\n - analytics/ (plots + csvs)")


if __name__ == "__main__":
    """
    Entry point for the Income Helper application.
    Runs the interactive CLI main function when executed directly.
    """
    main()
