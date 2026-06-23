"""Phase 9 - submission download + validation endpoint."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from ..config import ROOT
from ..store import store

sys.path.insert(0, str(ROOT))

router = APIRouter(prefix="/api/submission", tags=["submission"])


def _csv_path(team: str) -> Path:
    safe = "".join(c for c in team if c.isalnum() or c in "_-") or "team_talentai"
    return ROOT / "results" / f"{safe}.csv"


@router.post("/generate")
def generate(team: str = "team_talentai"):
    from talentai.submission import write_submission

    if not store.ranked:
        raise HTTPException(status_code=400, detail="no ranking loaded; run the pipeline")
    out = _csv_path(team)
    write_submission(store.ranked, out_path=out)
    return {"path": str(out), "rows": min(len(store.ranked), 100), "team": team}


@router.get("/validate")
def validate(team: str = "team_talentai"):
    path = _csv_path(team)
    if not path.exists():
        raise HTTPException(status_code=404, detail="submission not generated yet")

    vp = ROOT / "[PUB] India_runs_data_and_ai_challenge" / \
        "India_runs_data_and_ai_challenge" / "validate_submission.py"
    if not vp.exists():
        return {"valid": None, "errors": ["validator not found in bundle"]}
    spec = importlib.util.spec_from_file_location("validate_submission", vp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    errors = mod.validate_submission(str(path))
    return {"valid": not errors, "errors": errors}


@router.get("/download")
def download(team: str = "team_talentai"):
    path = _csv_path(team)
    if not path.exists():
        raise HTTPException(status_code=404, detail="submission not generated yet")
    return FileResponse(path, media_type="text/csv", filename=path.name)


@router.get("/report.pdf")
def report_pdf(team: str = "team_talentai", top_n: int = 100):
    if not store.ranked:
        raise HTTPException(status_code=400, detail="no ranking loaded; run the pipeline")
    try:
        from ..services.report import build_report_pdf
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="reportlab not installed; run: pip install reportlab",
        )
    safe = "".join(c for c in team if c.isalnum() or c in "_-") or "team_talentai"
    pdf = build_report_pdf(store.ranked[:top_n], store.trap_stats or {}, team)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe}_report.pdf"'},
    )
