#!/usr/bin/env python3
"""Compile standalone TikZ with Tectonic and export PDF, SVG, PNG, and evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def cache_dir() -> Path:
    if os.environ.get("OPENTIKZ_CACHE_DIR"):
        return Path(os.environ["OPENTIKZ_CACHE_DIR"]).expanduser().resolve()
    if os.environ.get("CONDA_PREFIX"):
        return Path(os.environ["CONDA_PREFIX"]) / "share/opentikz/cache"
    return Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "opentikz"


def runtime() -> dict:
    result = {"python": sys.executable, "cache_dir": str(cache_dir()), "tools": {}}
    prefix = Path(os.environ["CONDA_PREFIX"]).resolve() if os.environ.get("CONDA_PREFIX") else None
    for name in ("tectonic", "pdftocairo"):
        path = shutil.which(name)
        if not path:
            raise RuntimeError(f"required tool missing: {name}")
        if prefix and not Path(path).resolve().is_relative_to(prefix):
            raise RuntimeError(f"{name} is outside activated Conda environment: {path}")
        result["tools"][name] = path
    import pymupdf  # noqa: F401
    result["pymupdf"] = importlib.metadata.version("PyMuPDF")
    result["tectonic_version"] = subprocess.check_output(["tectonic", "--version"], text=True).strip()
    return result


def compile_pdf(tex: Path, output_dir: Path, *, offline: bool = False) -> tuple[Path, str]:
    """Build in isolation, preserving relative project includes via cwd."""
    cache = cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "XDG_CACHE_HOME": str(cache)}
    command = ["tectonic", "--keep-logs", "--outdir", str(output_dir)]
    if offline:
        command.append("--only-cached")
    command.append(tex.name)
    proc = subprocess.run(command, cwd=tex.parent, env=env, capture_output=True,
                          text=True, timeout=300)
    log = proc.stdout + proc.stderr
    tex_log = output_dir / (tex.stem + ".log")
    if tex_log.is_file():
        log += "\n--- TeX log ---\n" + tex_log.read_text(errors="replace")
    pdf = output_dir / (tex.stem + ".pdf")
    if proc.returncode or not pdf.is_file():
        raise RuntimeError("Tectonic compile failed:\n" + log)
    return pdf, log


def render(tex: Path, output_dir: Path, *, dpi: int = 300, offline: bool = False) -> dict:
    import pymupdf
    info = runtime()
    tex = tex.resolve(strict=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / (tex.stem + ".build.log")
    # Invalidate the old receipt before attempting an explicitly requested rebuild.
    receipt_path = output_dir / (tex.stem + ".render.json")
    receipt_path.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="opentikz-figure-") as tmp:
        work = Path(tmp)
        try:
            pdf, log = compile_pdf(tex, work, offline=offline)
            svg = work / (tex.stem + ".svg")
            subprocess.run(["pdftocairo", "-svg", str(pdf), str(svg)], check=True,
                           capture_output=True, text=True, timeout=60)
            with pymupdf.open(pdf) as doc:
                if len(doc) != 1:
                    raise RuntimeError(f"expected one standalone page, found {len(doc)}")
                page = doc[0]
                size = [page.rect.width, page.rect.height]
                page.get_pixmap(dpi=dpi, alpha=False).save(work / (tex.stem + ".png"))
            exports = {}
            for suffix in (".pdf", ".svg", ".png"):
                path = work / (tex.stem + suffix)
                exports[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = {"source": str(tex), "source_sha256": hashlib.sha256(tex.read_bytes()).hexdigest(),
                       "runtime": info, "offline": offline, "dpi": dpi, "page_points": size,
                       "exports_sha256": exports,
                       "scope": "render receipt; external TeX includes and scientific validity require separate review"}
            for name in exports:
                shutil.copy2(work / name, output_dir / name)
            log_path.write_text(log)
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
            return receipt
        except Exception as exc:
            log_path.write_text(str(exc) + "\n")
            raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    try:
        if args.preflight:
            print(json.dumps(runtime(), indent=2))
            return 0
        if not args.target or args.target.suffix != ".tex":
            parser.error("provide a .tex target or --preflight")
        if not 36 <= args.dpi <= 1200:
            parser.error("--dpi must lie in [36, 1200]")
        receipt = render(args.target, args.output_dir or args.target.parent,
                         dpi=args.dpi, offline=args.offline)
        print(json.dumps(receipt, indent=2))
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
