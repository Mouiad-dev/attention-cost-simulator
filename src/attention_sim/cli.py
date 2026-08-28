"""Interface layer. Parses user input, orchestrates simulator + plotter, prints.

This file contains NO math and NO drawing. It only wires things together:
  1. read the context lengths the user asked for
  2. ask the simulator for the numbers
  3. print a table (rich)
  4. ask the plotter to draw the chart
  5. print the headline ratio

If we ever add a FastAPI service, it would import simulator/plotter directly
and reuse them untouched. This CLI is just ONE possible front door.
"""

import typer
from rich.console import Console
from rich.table import Table

from .plotter import plot_costs
from .simulator import growth_ratio, simulate

app = typer.Typer(help="Simulate how attention cost grows with context length (N²).")
console = Console()


@app.command()
def run(
    lengths: list[int] = typer.Argument(
        ...,
        help="Context lengths in tokens, e.g. 1000 10000 100000",
    ),
    output: str = typer.Option(
        "attention_cost.png",
        "--output",
        "-o",
        help="Where to save the chart image.",
    ),
) -> None:
    """Compute and chart attention cost for the given context lengths."""
    # simulate() validates (empty list, negative lengths) and raises ValueError.
    # We catch it here and show a clean message instead of a scary traceback.
    try:
        points = simulate(lengths)
    except ValueError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1)

    # --- 1. print the numbers as a table ---
    table = Table(title="Attention cost by context length")
    table.add_column("Tokens", justify="right", style="cyan")
    table.add_column("Linear (~N)", justify="right")
    table.add_column("Attention (~N²)", justify="right", style="yellow")

    for point in points:
        table.add_row(
            f"{point.length:,}",
            f"{point.linear_cost:,.0f}",
            f"{point.attention_cost:,.0f}",
        )
    console.print(table)

    # --- 2. draw the chart ---
    saved_path = plot_costs(points, output)
    console.print(f"[green]Chart saved to:[/green] {saved_path}")

    # --- 3. the headline number (needs >= 2 points) ---
    if len(points) >= 2:
        ratio = growth_ratio(points)
        shortest = points[0].length
        longest = points[-1].length
        console.print(
            f"\n[bold]Headline:[/bold] going from {shortest:,} to {longest:,} tokens, "
            f"attention cost multiplies by [bold red]{ratio:,.0f}x[/bold red]."
        )


if __name__ == "__main__":
    app()