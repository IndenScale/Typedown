# PMO SaaS - Flagship Demo

This is a comprehensive demonstration of using Typedown as the backend for a Project Management Office (PMO) SaaS system.

## Domain Model

- **HR**: Employees (`models/hr.py`) with Roles, Levels, and Cost Rates.
- **PM**: Projects (`models/pm.py`) with Regional context and Budget Caps.
- **Finance**:
  - Regional Policies (`models/finance.py`) for travel allowances.
  - Expense Items (`models/expense.py`) for non-payroll costs (Logistics, Service, Procurement, etc.).
- **Operations**: WorkLogs (`models/activity.py`) tracking specific activity types (Delivery, Training, etc.) and Location.

## Workflow

1. **Define Org Structure**: See `docs/org/staff.md`.
2. **Define Policies**: See `docs/org/policies.md`.
3. **Plan Projects**: See `docs/projects/portfolio.md`.
4. **Log Time**: See `docs/timesheets/2024_03.md`.
5. **Log Expenses**: See `docs/expenses/2024_03.md`.

## Automation

### 1. Monthly Performance & Budget Report

Run the CLI script to calculate total project costs, combining:

- Labor Cost (based on Daily Rate)
- Travel Allowance (based on Regional Policy)
- Direct Expenses (Logistics, Procurement, Services, etc.)

```bash
uv run python use_cases/pmo_saas/scripts/export_monthly.py
```

### 2. Governance Checks

(Coming soon: rules to ensure no budget overrun and logical work logs)

## Visualization

After building (`td build`), the data can be visualized using standard frontend tools.
