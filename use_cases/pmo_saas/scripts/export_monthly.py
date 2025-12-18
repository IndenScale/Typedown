import sys
from pathlib import Path
from collections import defaultdict

# Add project root to sys.path to import typedown core
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

from typedown.core.workspace import Workspace

def main():
    use_case_root = Path(__file__).resolve().parents[1]
    
    print(f"Loading Workspace from {use_case_root}...")
    workspace = Workspace(root=use_case_root)
    workspace.load(use_case_root)
    workspace.resolve()
    
    # 1. Gather Tables
    # Access properties directly on the entity wrappers
    employees = {e.id: e for e in workspace.get_entities_by_type("Employee")}
    projects = {p.id: p for p in workspace.get_entities_by_type("Project")}
    policies = {p.region_code: p for p in workspace.get_entities_by_type("RegionalPolicy")}
    worklogs = workspace.get_entities_by_type("WorkLog")
    expenses = workspace.get_entities_by_type("ExpenseItem")
    
    # Check default policy
    remote_policy = policies.get("REMOTE")
    default_allowance = remote_policy.travel_allowance_per_day if remote_policy else 0.0

    print("\n--- Monthly Performance & Budget Report (2024-03) ---\n")
    
    project_costs = defaultdict(lambda: {"labor": 0.0, "travel_allowance": 0.0, "expense": 0.0})
    
    # 2. Calculate Labor & Allowance Costs
    print(f"{'Project':<25} | {'Person':<15} | {'Type':<12} | {'Days':<5} | {'Labor':<10} | {'Allow.':<8} | {'Total'}")
    print("-" * 90)
    
    for log in worklogs:
        emp = employees.get(log.employee_id)
        proj = projects.get(log.project_id)
        
        if not emp or not proj:
            continue
            
        # Basic Labor Cost
        labor_cost = log.work_days * emp.base_cost_per_day
        
        # Travel Allowance (Fixed calculation based on policy)
        if log.location.value == "ONSITE":
             policy = policies.get(proj.region)
             allowance_rate = policy.travel_allowance_per_day if policy else 0.0
        else:
             allowance_rate = 0.0
             
        allowance_cost = log.work_days * allowance_rate
        total_sub = labor_cost + allowance_cost
        
        project_costs[proj.id]["labor"] += labor_cost
        project_costs[proj.id]["travel_allowance"] += allowance_cost
        
        print(f"{proj.name:<25} | {emp.name:<15} | {log.activity_type.value:<12} | {log.work_days:<5} | {labor_cost:>10,.0f} | {allowance_cost:>8,.0f} | {total_sub:,.0f}")

    # 3. Calculate Direct Expenses
    print("\n--- Direct Expenses (Non-Payroll) ---")
    print(f"{'Project':<25} | {'Category':<15} | {'Vendor':<15} | {'Amount':<10} | {'Description'}")
    print("-" * 100)
    
    for exp in expenses:
        proj = projects.get(exp.project_id)
        if not proj: continue
        
        project_costs[proj.id]["expense"] += exp.amount
        print(f"{proj.name:<25} | {exp.category.value:<15} | {exp.vendor or '-':<15} | {exp.amount:>10,.2f} | {exp.description}")

    # 4. Final Budget Summary
    print("\n\n--- Final Budget Health ---")
    print(f"{'Project':<25} | {'Budget Cap':<12} | {'Labor':<10} | {'Allow.':<8} | {'Expenses':<10} | {'Total Cost':<12} | {'Remaining'}")
    print("-" * 100)
    
    for proj_id, costs in project_costs.items():
        proj = projects.get(proj_id)
        if not proj: continue
        
        total_labor = costs["labor"]
        total_allow = costs["travel_allowance"]
        total_exp = costs["expense"]
        total_cost = total_labor + total_allow + total_exp
        
        remaining = proj.budget_cap - total_cost
        status = "OVERRUN" if remaining < 0 else "OK"
        
        print(f"{proj.name:<25} | {proj.budget_cap:>12,.0f} | {total_labor:>10,.0f} | {total_allow:>8,.0f} | {total_exp:>10,.2f} | {total_cost:>12,.2f} | {remaining:,.2f} {status}")
        
    print("\n--- Export Complete ---")

if __name__ == "__main__":
    main()
