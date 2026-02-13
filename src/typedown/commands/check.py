import typer
from pathlib import Path
from typing import Optional, Literal

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result

Stage = Literal["syntax", "structure", "local", "global"]


def check(
    stage: Optional[str] = typer.Argument(
        None,
        help="Validation stage: syntax, structure, local, global"
    ),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    fast: bool = typer.Option(False, "--fast", help="Fast mode: syntax + structure only"),
    full: bool = typer.Option(False, "--full", help="Full mode: all stages including global"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """
    Unified validation command with four-stage progressive model.
    
    Stages (in order):
        syntax    - Markdown/YAML parsing
        structure - Pydantic instantiation (no validators)
        local     - Pydantic validators (single-entity rules)
        global    - Reference resolution + Spec execution
    
    Examples:
        typedown check              # Default: local stage
        typedown check syntax       # Only syntax check
        typedown check structure    # syntax + structure
        typedown check --fast       # syntax + structure (shortcut)
        typedown check --full       # All stages (pre-commit)
        typedown check global       # Full validation with specs
    
    [Best Practices]
    
    1. Validation Logic Placement:
    
       Use @field_validator for: single field format/transform
         - Email format, date parsing, string normalization
         - Example: ensure email is lowercase
    
       Use @model_validator for: cross-field consistency within one entity
         - Start date < End date, total = sum(items)
         - Example: validate status transition rules
    
       Use spec block for: cross-entity business rules and aggregations
         - "All admins must have MFA enabled" (queries all User entities)
         - "Total orders per customer cannot exceed 100" (aggregation)
         - Example: statistical constraints, global invariants
    
    2. Reference Patterns:
    
       In Markdown text: Use wiki link syntax [[target]] for inline references.
       
       In Entity block: Use [[entity-id]] syntax for typed references:
         ```entity Order: order-001
         customer: [[customer-alice]]     # Reference single entity
         items:
           - [[product-laptop]]           # Reference in lists
           - [[product-mouse]]
         ```
    
       DON'T: Manually define id fields as foreign keys
         ```entity Order: order-001
         customer_id: "customer-alice"  # Avoid this pattern
         ```
    
       The [[...]] syntax in entities is type-checked and validated during the
       global stage. References must point to existing entities with valid
       IDs (alphanumeric, dots, dashes, underscores).
    
    3. Statistical Constraints:
    
       DON'T create virtual aggregate classes for counts/sums.
       Instead, write a spec that collects entities and reports diagnostics:
    
       ```spec:check_customer_order_limit
       @target(type="Customer", scope="global")
       def check_order_limit(customer: Customer, ctx: Context):
           orders = ctx.find_all("Order", lambda o: o.customer == customer.id)
           if len(orders) > 100:
               ctx.report(f"Customer {customer.name} has {len(orders)} orders (limit: 100)")
       ```
    """
    # Determine target stage
    target_stage: Stage = "local"  # default
    if fast:
        target_stage = "structure"
    elif full:
        target_stage = "global"
    elif stage:
        if stage not in ("syntax", "structure", "local", "global"):
            if not as_json:
                print(f"[red]Error: Unknown stage '{stage}'. Use: syntax, structure, local, global[/red]")
            raise typer.Exit(code=2)
        target_stage = stage  # type: ignore
    
    stages: list[Stage] = ["syntax", "structure", "local", "global"]
    target_idx = stages.index(target_stage)
    stages_to_run = stages[:target_idx + 1]
    
    with cli_session(path, as_json=as_json, require_project=True) as ctx:
        all_passed = True
        stage_results = {}
        
        for s in stages_to_run:
            passed = _run_stage(ctx, s)
            stage_results[s] = passed
            if not passed:
                all_passed = False
                # Stop on first failure (fail-fast)
                break
        
        if as_json:
            result = {
                "passed": all_passed,
                "stage": target_stage,
                "stages_executed": stages_to_run,
                "stage_results": stage_results,
                "diagnostics": [
                    e.to_dict() for e in ctx.compiler.diagnostics.errors
                ]
            }
            cli_result(ctx, result, exit_on_error=False)
            if not all_passed:
                raise typer.Exit(code=1)
        else:
            ctx.display_console.print()
            if all_passed:
                ctx.display_console.print(
                    f"[green]✓ Check passed: {target_stage} stage(s) completed[/green]"
                )
            else:
                failed_stage = next((s for s in stages_to_run if not stage_results.get(s, True)), target_stage)
                ctx.display_console.print(
                    f"[red]✗ Check failed at {failed_stage} stage[/red]"
                )
                raise typer.Exit(code=1)


def _run_stage(ctx, stage: Stage) -> bool:
    """Run a single validation stage."""
    console = ctx.display_console
    
    if stage == "syntax":
        console.print("[dim]Stage 1/4:[/dim] [bold]syntax[/bold] - Markdown/YAML parsing...")
        passed = ctx.compiler.lint()
        if passed:
            console.print("  [green]✓[/green] Syntax check passed")
        return passed
    
    elif stage == "structure":
        console.print("[dim]Stage 2/4:[/dim] [bold]structure[/bold] - Pydantic instantiation...")
        passed = ctx.compiler.check_structure()
        if passed:
            console.print("  [green]✓[/green] Structure check passed")
        return passed
    
    elif stage == "local":
        console.print("[dim]Stage 3/4:[/dim] [bold]local[/bold] - Pydantic validators...")
        passed = ctx.compiler.check_local()
        if passed:
            console.print("  [green]✓[/green] Local validation passed")
        return passed
    
    elif stage == "global":
        console.print("[dim]Stage 4/4:[/dim] [bold]global[/bold] - Reference resolution + Specs...")
        passed = ctx.compiler.check_global()
        if passed:
            console.print("  [green]✓[/green] Global validation passed")
        return passed
    
    return False
