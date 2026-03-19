"""
cli.py — Typer command-line interface for the Oil Painting Research Assistant.

Commands:
    ask         Ask a question using the full RAG pipeline
    intake      Intake source files — scan inbox or process a single file
    chunk       Chunk an ingested source
    index       Index chunked sources into ChromaDB + BM25
    status      Show index and source register status
    benchmark   Run the benchmark gold set
    review      Show sources pending review
    rebuild     Rebuild indexes from stored chunks
    conflicts   List active conflict records
    sources     List registered sources
    vocab       Show controlled vocabulary summary
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

import oil_painting_rag.config as cfg
from oil_painting_rag.logging_utils import configure_logging, get_logger

app = typer.Typer(
    name="oil-rag",
    help="Oil Painting Research Assistant — RAG CLI",
    no_args_is_help=True,
)
console = Console()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lazy helpers (avoid importing heavy deps at module load time)
# ---------------------------------------------------------------------------

def _get_index_manager():
    from oil_painting_rag.indexing.index_manager import IndexManager
    cfg.ensure_data_dirs()
    return IndexManager()


def _get_retriever(index_manager=None):
    from oil_painting_rag.retrieval.hybrid_retriever import HybridRetriever
    return HybridRetriever(index_manager or _get_index_manager())


def _get_answerer():
    from oil_painting_rag.generation.answerer import Answerer
    return Answerer()


# ---------------------------------------------------------------------------
# ask
# ---------------------------------------------------------------------------

@app.command()
def ask(
    query: str = typer.Argument(..., help="Question to ask"),
    top_k: int = typer.Option(cfg.RETRIEVAL_TOP_K, "--top-k", "-k", help="Max chunks to retrieve"),
    token_budget: int = typer.Option(cfg.RETRIEVAL_TOKEN_BUDGET, "--tokens", help="Token budget"),
    gate: str = typer.Option(cfg.DEFAULT_RETRIEVAL_GATE, "--gate", help="Approval gate"),
    trace: bool = typer.Option(False, "--trace", help="Save retrieval trace"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Ask a research question using the full hybrid RAG pipeline."""
    from oil_painting_rag.models.retrieval_models import RetrievalRequest

    configure_logging()
    mgr = _get_index_manager()
    retriever = _get_retriever(mgr)
    answerer = _get_answerer()

    request = RetrievalRequest(
        query=query,
        top_k=top_k,
        token_budget=token_budget,
        approval_gate=gate,
        enable_trace=trace,
    )

    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}\n")

    try:
        context = retriever.retrieve(request)
    except Exception as exc:
        console.print(f"[red]Retrieval error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if verbose:
        console.print(
            f"[dim]Retrieved {len(context.selected_chunks)} chunks, "
            f"{context.token_budget_used} tokens[/dim]"
        )

    try:
        result = answerer.answer(query, context)
    except Exception as exc:
        console.print(f"[red]Generation error:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"[bold green]Mode:[/bold green] {result.answer_mode}\n")
    console.print(result.answer_text)

    if result.citations:
        console.print("\n[bold]Sources:[/bold]")
        for c in result.citations:
            console.print(f"  • {c}")

    if result.conflict_disclosures:
        console.print("\n[bold yellow]Conflict Disclosures:[/bold yellow]")
        for d in result.conflict_disclosures:
            console.print(f"  ⚠ {d}")

    if result.uncertainty_notes:
        console.print("\n[bold yellow]Uncertainty Notes:[/bold yellow]")
        for n in result.uncertainty_notes:
            console.print(f"  ? {n}")


# ---------------------------------------------------------------------------
# intake
# ---------------------------------------------------------------------------

@app.command()
def intake(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Process a single file (skip inbox scan)"),
) -> None:
    """Intake source files — scan inbox or process a single file."""
    from oil_painting_rag.ingestion.intake_runner import process_file, _collect_inbox_files
    from oil_painting_rag.ingestion.capture import SourceCapture
    from oil_painting_rag.ingestion.intake_classifier import IntakeClassifier
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    configure_logging()
    cfg.ensure_data_dirs()

    classifier = IntakeClassifier()
    registry = SourceRegistry()
    capture = SourceCapture()

    if file:
        if not file.exists():
            console.print(f"[red]File not found:[/red] {file}")
            raise typer.Exit(1)
        result = process_file(file, None, classifier, registry, capture)
        if result and result != "QUIT":
            console.print(f"[green]Done:[/green] registered {result}")
    else:
        files = _collect_inbox_files()
        if not files:
            console.print("[yellow]No files found in data/inbox/[/yellow]")
            return

        console.print(f"Found [bold]{len(files)}[/bold] file(s) in inbox:")
        for fpath, label in files:
            console.print(f"  [{label}] {fpath.name}")

        registered: list[str] = []
        skipped = 0
        for fpath, label in files:
            result = process_file(fpath, label, classifier, registry, capture)
            if result == "QUIT":
                console.print("\nStopped by user.")
                break
            elif result:
                registered.append(result)
            else:
                skipped += 1

        console.print(f"\n[bold]Done:[/bold] {len(registered)} registered, {skipped} skipped, {len(files)} total")


# ---------------------------------------------------------------------------
# chunk
# ---------------------------------------------------------------------------

@app.command()
def chunk(
    source_id: Optional[str] = typer.Argument(None, help="Source ID to chunk (all if omitted)"),
) -> None:
    """Chunk ingested source documents."""
    from oil_painting_rag.chunking.chunker import ProseChunker
    from oil_painting_rag.chunking.table_chunker import TableChunker
    from oil_painting_rag.ingestion.loader import SourceLoader
    from oil_painting_rag.ingestion.source_registry import SourceRegistry
    from oil_painting_rag.storage.filesystem_store import FilesystemStore

    configure_logging()
    cfg.ensure_data_dirs()
    registry = SourceRegistry()
    loader = SourceLoader()
    fs = FilesystemStore()
    prose_chunker = ProseChunker()
    table_chunker = TableChunker()

    sources = registry.all_sources()
    if source_id:
        sources = [s for s in sources if s.source_id == source_id]
        if not sources:
            console.print(f"[red]Source not found:[/red] {source_id}")
            raise typer.Exit(1)

    for src in sources:
        try:
            text = loader.load_clean_text(src.source_id) or loader.extract_text_from_raw(src.source_id)
            if not text:
                console.print(f"[yellow]No text for[/yellow] {src.source_id}")
                continue
            chunks = prose_chunker.chunk_source(src, text)
            table_chunks = table_chunker.chunk_source(src, text)
            all_chunks = chunks + table_chunks
            for ch in all_chunks:
                fs.save_chunk_text(ch.chunk_id, ch.text)
                fs.save_chunk_metadata(ch.chunk_id, ch.model_dump())
            console.print(f"[green]Chunked[/green] {src.source_id}: {len(all_chunks)} chunks")
        except Exception as exc:
            console.print(f"[red]Chunk error[/red] {src.source_id}: {exc}")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

@app.command()
def index(
    source_id: Optional[str] = typer.Argument(None, help="Source ID to index (all if omitted)"),
    rebuild: bool = typer.Option(False, "--rebuild", help="Rebuild from stored chunks"),
) -> None:
    """Index chunked sources into ChromaDB and BM25."""
    configure_logging()
    mgr = _get_index_manager()

    if rebuild:
        console.print("[cyan]Rebuilding indexes from stored chunks…[/cyan]")
        try:
            mgr.rebuild_from_files()
            console.print("[green]Rebuild complete.[/green]")
        except Exception as exc:
            console.print(f"[red]Rebuild error:[/red] {exc}")
            raise typer.Exit(1) from exc
        return

    from oil_painting_rag.ingestion.source_registry import SourceRegistry
    from oil_painting_rag.storage.filesystem_store import FilesystemStore
    from oil_painting_rag.models.chunk_models import ChunkRecord

    registry = SourceRegistry()
    fs = FilesystemStore()

    sources = registry.all_sources()
    if source_id:
        sources = [s for s in sources if s.source_id == source_id]

    for src in sources:
        chunk_ids = fs.chunk_ids_for_source(src.source_id)
        count = 0
        for cid in chunk_ids:
            try:
                meta = fs.load_chunk_metadata(cid)
                if meta:
                    ch = ChunkRecord.model_validate(meta)
                    mgr.upsert_chunk(ch)
                    count += 1
            except Exception as exc:
                logger.warning("Could not index chunk %s: %s", cid, exc)
        if chunk_ids:
            console.print(f"[green]Indexed[/green] {src.source_id}: {count}/{len(chunk_ids)} chunks")


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@app.command()
def status() -> None:
    """Show index counts and source register summary."""
    configure_logging()
    mgr = _get_index_manager()

    idx_status = mgr.status()
    console.print("\n[bold]Index Status[/bold]")
    t = Table()
    t.add_column("Collection")
    t.add_column("Chunk Count", justify="right")
    for name, count in idx_status.get("chroma_counts", {}).items():
        t.add_row(name, str(count))
    console.print(t)

    bm25_size = idx_status.get("bm25_size", 0)
    console.print(
        f"\nBM25 index: {bm25_size} documents"
    )

    from oil_painting_rag.ingestion.source_registry import SourceRegistry
    registry = SourceRegistry()
    sources = registry.all_sources()
    console.print(f"\nRegistered sources: {len(sources)}")


# ---------------------------------------------------------------------------
# review
# ---------------------------------------------------------------------------

@app.command()
def review(
    reviewed: bool = typer.Option(False, "--reviewed", help="Show reviewed sources (default: unreviewed)"),
    limit: int = typer.Option(20, "--limit", "-n"),
) -> None:
    """Show sources pending review."""
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    configure_logging()
    registry = SourceRegistry()
    sources = [s for s in registry.all_sources() if s.qa_reviewed == reviewed][:limit]

    label = "Reviewed" if reviewed else "Pending Review"
    if not sources:
        console.print(f"No {label.lower()} sources found.")
        return

    t = Table(title=f"Sources — {label}")
    t.add_column("Source ID")
    t.add_column("Title")
    t.add_column("Domain")
    t.add_column("Tier", justify="right")
    for s in sources:
        t.add_row(s.source_id, s.short_title[:50], s.domain, str(s.trust_tier))
    console.print(t)


# ---------------------------------------------------------------------------
# rebuild
# ---------------------------------------------------------------------------

@app.command()
def rebuild() -> None:
    """Rebuild all indexes from stored chunk files."""
    configure_logging()
    mgr = _get_index_manager()
    console.print("[cyan]Rebuilding indexes…[/cyan]")
    try:
        mgr.rebuild_from_files()
        console.print("[green]Rebuild complete.[/green]")
    except Exception as exc:
        console.print(f"[red]Rebuild error:[/red] {exc}")
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# conflicts
# ---------------------------------------------------------------------------

@app.command()
def conflicts() -> None:
    """List active conflict records."""
    from oil_painting_rag.storage.metadata_store import MetadataStore

    configure_logging()
    store = MetadataStore()
    all_conflicts = store.load_all_conflicts()

    active = [c for c in all_conflicts if c.get("resolution_status") != "resolved"]
    if not active:
        console.print("[green]No active conflicts.[/green]")
        return

    t = Table(title="Active Conflicts")
    t.add_column("Conflict ID")
    t.add_column("Topic")
    t.add_column("Entity IDs")
    t.add_column("Status")
    for c in active[:50]:
        t.add_row(
            c.get("conflict_id", ""),
            str(c.get("topic", ""))[:40],
            ", ".join(c.get("entity_ids", []))[:40],
            c.get("resolution_status", ""),
        )
    console.print(t)


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------

@app.command()
def sources(
    domain: Optional[str] = typer.Option(None, "--domain"),
    tier: Optional[int] = typer.Option(None, "--tier"),
    limit: int = typer.Option(50, "--limit", "-n"),
) -> None:
    """List registered sources."""
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    configure_logging()
    registry = SourceRegistry()
    all_src = registry.all_sources()

    if domain:
        all_src = [s for s in all_src if s.domain == domain]
    if tier is not None:
        all_src = [s for s in all_src if s.trust_tier == tier]

    all_src = all_src[:limit]
    if not all_src:
        console.print("No sources found.")
        return

    t = Table(title="Registered Sources")
    t.add_column("Source ID")
    t.add_column("Title")
    t.add_column("Domain")
    t.add_column("Tier", justify="right")
    t.add_column("Ready")
    for s in all_src:
        ready = "Yes" if s.ready_for_use else "No"
        t.add_row(s.source_id, s.short_title[:40], s.domain, str(s.trust_tier), ready)
    console.print(t)


# ---------------------------------------------------------------------------
# benchmark
# ---------------------------------------------------------------------------

@app.command()
def benchmark(
    max_records: Optional[int] = typer.Option(None, "--max", "-n"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
) -> None:
    """Run the benchmark gold set through the RAG pipeline."""
    from oil_painting_rag.evaluation.benchmark_runner import BenchmarkRunner

    configure_logging()
    mgr = _get_index_manager()
    runner = BenchmarkRunner(
        index_manager=mgr,
        output_dir=output_dir or cfg.BENCHMARKS_DIR,  # type: ignore[call-arg]
    )
    results = runner.run(max_records=max_records)

    passed = sum(1 for r in results if r.failure_tags == [])
    console.print(
        f"\n[bold]Benchmark complete:[/bold] {len(results)} records, "
        f"{passed} with no automated failures"
    )

    if results:
        out = runner.save_results(results)
        console.print(f"Results: {out}")


# ---------------------------------------------------------------------------
# vocab
# ---------------------------------------------------------------------------

@app.command()
def vocab() -> None:
    """Show a summary of the controlled vocabulary."""
    from oil_painting_rag.utils.enum_utils import load_controlled_vocabulary

    configure_logging()
    cv = load_controlled_vocabulary()

    t = Table(title="Controlled Vocabulary Keys")
    t.add_column("Key")
    t.add_column("Value Count", justify="right")
    for key, values in sorted(cv.items()):
        if isinstance(values, list):
            t.add_row(key, str(len(values)))
        else:
            t.add_row(key, "1")
    console.print(t)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    configure_logging()
    app()


if __name__ == "__main__":
    main()
