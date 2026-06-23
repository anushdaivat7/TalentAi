"""Phase 2 - Job description analysis.

Parses job_description.docx into a structured job profile and persists it to
artifacts/job_profile.json. If sentence-transformers is available it also caches
the JD embedding for the semantic ranking component.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentai import job_profile as jp  # noqa: E402
from talentai import paths  # noqa: E402


def docx_to_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    xml = xml.replace("</w:p>", "\n")
    text = re.sub(r"<[^>]+>", "", xml)
    for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&#39;", "'")]:
        text = text.replace(a, b)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze the JD into a structured profile")
    ap.add_argument("--jd", default=None, help="path to job_description.docx/.md")
    ap.add_argument("--no-embed", action="store_true", help="skip JD embedding")
    args = ap.parse_args()

    profile = jp.structured_profile()

    jd_path = Path(args.jd) if args.jd else (paths.bundle_dir() / "job_description.docx")
    raw_text = ""
    if jd_path.exists():
        try:
            raw_text = docx_to_text(jd_path) if jd_path.suffix == ".docx" \
                else jd_path.read_text(encoding="utf-8")
            profile["raw_text_chars"] = len(raw_text)
        except Exception as e:  # noqa: BLE001
            print(f"[analyze_job] could not parse JD: {e}")

    with open(paths.JOB_PROFILE_JSON, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"[analyze_job] wrote structured profile -> {paths.JOB_PROFILE_JSON}")
    print(json.dumps({k: profile[k] for k in
                      ["role_title", "required_skills", "preferred_skills"]}, indent=2))

    if not args.no_embed:
        try:
            import numpy as np
            from talentai import embeddings as emb

            text = (raw_text + "\n" + profile["summary_text"]) if raw_text else profile["summary_text"]
            vec = emb.embed_one(text)
            np.save(paths.JOB_EMBEDDING_NPY, vec)
            print(f"[analyze_job] cached JD embedding -> {paths.JOB_EMBEDDING_NPY}")
        except Exception as e:  # noqa: BLE001
            print(f"[analyze_job] skipped JD embedding ({e})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
