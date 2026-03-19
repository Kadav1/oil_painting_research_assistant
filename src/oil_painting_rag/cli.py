"""
cli.py — Typer command-line interface for the Oil Painting Research Assistant.

Commands:
    ask         Ask a question using the full RAG pipeline
    ingest      Register and ingest a source document
    scan-inbox  Batch-ingest all files from data/inbox/
    chunk       Chunk an ingested source
    index       Index chunked sources into ChromaDB + BM25
    status      Show index and source register status
    benchmark   Run the benchmark gold set
    review      Show chunks pending review
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
# ingest
# ---------------------------------------------------------------------------

@app.command()
def ingest(
    file: Path = typer.Argument(..., help="Path to the source file"),
    source_id: Optional[str] = typer.Option(None, "--source-id", help="Override source ID"),
    title: Optional[str] = typer.Option(None, "--title"),
    domain: str = typer.Option("mixed", "--domain"),
    source_family: str = typer.Option("unknown", "--source-family"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Register a source document and save it to raw storage."""
    from oil_painting_rag.ingestion.capture import SourceCapture
    from oil_painting_rag.ingestion.source_registry import SourceRegistry
    from oil_painting_rag.models.source_models import SourceRecord
    from oil_painting_rag.policies.source_policy import infer_trust_tier
    from oil_painting_rag.utils.hash_utils import sha256_hex

    configure_logging()
    cfg.ensure_data_dirs()

    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(1)

    raw_text = file.read_text(encoding="utf-8", errors="replace")
    generated_id = source_id or f"SRC-{sha256_hex(str(file))[:8].upper()}"
    tier = infer_trust_tier(source_family)

    record = SourceRecord(
        source_id=generated_id,
        source_title=title or file.stem,
        source_family=source_family,
        domain=domain,
        trust_tier=tier,
        approval_state="internal_draft_only",
        review_status="draft",
        file_format=file.suffix.lstrip(".") or "txt",
    )

    registry = SourceRegistry()
    capture = SourceCapture()

    try:
        registry.register(record)
        capture.save_raw_file(generated_id, file.suffix.lstrip(".") or "txt", raw_text)
        console.print(f"[green]Ingested:[/green] {generated_id} — {record.source_title}")
        if verbose:
            console.print(f"  Trust tier: {tier}  Domain: {domain}")
    except Exception as exc:
        console.print(f"[red]Ingest error:[/red] {exc}")
        raise typer.Exit(1) from exc


# ---------------------------------------------------------------------------
# scan-inbox
# ---------------------------------------------------------------------------

@app.command(name="scan-inbox")
def scan_inbox(
    domain: str = typer.Option("mixed", "--domain", help="Default domain for all scanned files"),
    source_family: str = typer.Option("unknown", "--source-family", help="Default source family"),
    dry_run: bool = typer.Option(False, "--dry-run", help="List files without ingesting"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Scan data/inbox/ subfolders and batch-ingest all files found."""
    from oil_painting_rag.ingestion.capture import SourceCapture
    from oil_painting_rag.ingestion.source_registry import SourceRegistry
    from oil_painting_rag.models.source_models import SourceRecord
    from oil_painting_rag.policies.source_policy import infer_trust_tier
    from oil_painting_rag.utils.hash_utils import sha256_hex

    configure_logging()
    cfg.ensure_data_dirs()

    inbox_subdirs = {
        "pdf": cfg.INBOX_PDF_DIR,
        "html": cfg.INBOX_HTML_DIR,
        "markdown": cfg.INBOX_MARKDOWN_DIR,
        "text": cfg.INBOX_TEXT_DIR,
        "other": cfg.INBOX_OTHER_DIR,
    }

    # Collect all files across inbox subfolders
    files_found: list[tuple[Path, str]] = []  # (path, subfolder_name)
    for label, inbox_path in inbox_subdirs.items():
        if not inbox_path.exists():
            continue
        for fpath in sorted(inbox_path.iterdir()):
            if fpath.is_file() and not fpath.name.startswith("."):
                files_found.append((fpath, label))

    if not files_found:
        console.print("[yellow]No files found in data/inbox/[/yellow]")
        return

    console.print(f"Found [bold]{len(files_found)}[/bold] file(s) in inbox:")
    for fpath, label in files_found:
        console.print(f"  [{label}] {fpath.name}")

    if dry_run:
        console.print("[yellow]Dry run — no files ingested[/yellow]")
        return

    registry = SourceRegistry()
    capture = SourceCapture()
    tier = infer_trust_tier(source_family)
    ingested = 0
    errors = 0

    for fpath, label in files_found:
        generated_id = f"SRC-{sha256_hex(str(fpath))[:8].upper()}"
        file_format = fpath.suffix.lstrip(".") or label

        try:
            raw_text = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            console.print(f"  [red]Read error:[/red] {fpath.name}: {exc}")
            errors += 1
            continue

        record = SourceRecord(
            source_id=generated_id,
            source_title=fpath.stem,
            source_family=source_family,
            domain=domain,
            trust_tier=tier,
            approval_state="internal_draft_only",
            review_status="draft",
            file_format=file_format,
        )

        try:
            registry.register(record)
            capture.save_raw_file(generated_id, file_format, raw_text)
            console.print(f"  [green]Ingested:[/green] {generated_id} — {fpath.name}")
            ingested += 1
        except Exception as exc:
            console.print(f"  [red]Ingest error:[/red] {fpath.name}: {exc}")
            errors += 1

    console.print(f"\n[bold]Done:[/bold] {ingested} ingested, {errors} errors, {len(files_found)} total")


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
    approval_state: str = typer.Option("internal_draft_only", "--state"),
    limit: int = typer.Option(20, "--limit", "-n"),
) -> None:
    """Show sources/chunks pending review."""
    from oil_painting_rag.ingestion.source_registry import SourceRegistry

    configure_logging()
    registry = SourceRegistry()
    sources = [s for s in registry.all_sources() if s.approval_state == approval_state][:limit]

    if not sources:
        console.print(f"No sources with approval_state={approval_state!r}")
        return

    t = Table(title=f"Sources — {approval_state}")
    t.add_column("Source ID")
    t.add_column("Title")
    t.add_column("Domain")
    t.add_column("Tier", justify="right")
    for s in sources:
        t.add_row(s.source_id, s.source_title[:50], s.domain, str(s.trust_tier))
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
    t.add_column("State")
    for s in all_src:
        t.add_row(s.source_id, s.source_title[:40], s.domain, str(s.trust_tier), s.approval_state)
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
