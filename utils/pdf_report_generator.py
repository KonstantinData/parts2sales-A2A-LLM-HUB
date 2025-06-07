from pathlib import Path
import json
from typing import Iterable, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

__all__ = ["generate_pdf_report"]


def load_events(jsonl_path: Path) -> Iterable[Dict[str, Any]]:
    """Load AgentEvent entries from a JSONL workflow log."""
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def generate_pdf_report(
    log_path: Path,
    output_dir: Path = Path("logs/reports"),
    template_path: Path = Path("templates/report_template.html"),
) -> Path:
    """Render a workflow log as a PDF report and return the created file path."""
    entries = list(load_events(log_path))
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_path.name)
    html_content = template.render(entries=entries)

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{log_path.stem}_report.pdf"
    HTML(string=html_content, base_url=str(template_path.parent)).write_pdf(
        str(pdf_path)
    )
    return pdf_path
