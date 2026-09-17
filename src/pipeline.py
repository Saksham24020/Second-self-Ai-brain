import typer

from src.classify import classify as run_classify
from src.link import link as run_link
from src.build_graph import generate_graph

app = typer.Typer(help="Pipeline to run classification, linking, and optional graph generation.")

@app.callback(invoke_without_command=True)
def run_all(
    force_classify: bool = typer.Option(False, "--force-classify", help="Re-run classification even if already classified."),
    rebuild_links: bool = typer.Option(False, "--rebuild-links", help="Rebuild the linking index and edges."),
    generate_graph_flag: bool = typer.Option(True, "--graph", help="Generate the knowledge graph after linking.")
):
    """Execute the full pipeline: classification, linking, and optionally graph generation.

    - ``--force-classify`` forces re‑classification of all captures.
    - ``--rebuild-links`` rebuilds the FAISS index from scratch and recomputes all links.
    - ``--graph`` (default true) runs the graph generation step after linking.
    """
    typer.echo("Running classification...")
    run_classify(capture_id=None, all=True, force=force_classify)

    typer.echo("Running linking...")
    run_link(capture_id=None, rebuild=rebuild_links)

    if generate_graph_flag:
        typer.echo("Generating knowledge graph...")
        generate_graph()

    typer.echo("Pipeline completed.")

if __name__ == "__main__":
    app()
