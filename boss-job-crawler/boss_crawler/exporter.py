"""Excel export support."""

from __future__ import annotations

from pathlib import Path

from .exceptions import ExportError
from .models import JobInfo


class ExcelExporter:
    """Export crawled jobs to an Excel workbook."""

    def export(self, jobs: list[JobInfo], output_file: str | Path) -> Path:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        rows = [job.to_dict() for job in jobs]
        try:
            import pandas as pd

            dataframe = pd.DataFrame(rows)
            dataframe.to_excel(output_path, index=False)
        except Exception as exc:
            raise ExportError(f"failed to export excel file: {exc}") from exc

        return output_path
