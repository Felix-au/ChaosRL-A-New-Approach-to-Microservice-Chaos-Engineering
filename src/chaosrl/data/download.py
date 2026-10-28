"""Downloader for empirical microservice telemetry datasets (RCAEval)."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import zipfile
import requests
from tqdm import tqdm

logger = logging.getLogger("chaosrl.data.download")

DATA_RAW_DIR = Path("data_raw")
RCAEVAL_DIR = DATA_RAW_DIR / "rcaeval"

ZENODO_FILES = {
    "RE1-OB.zip": {
        "url": "https://zenodo.org/api/records/14590730/files/RE1-OB.zip/content",
        "system": "Online Boutique",
        "expected_size_mb": 29.53,
    },
    "RE1-SS.zip": {
        "url": "https://zenodo.org/api/records/14590730/files/RE1-SS.zip/content",
        "system": "Sock Shop",
        "expected_size_mb": 75.43,
    },
}


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest_path: Path, max_size_gb: float = 3.0) -> bool:
    """Download a file with progress reporting and size validation."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "ChaosRL-Research/0.1.0"}

    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            if total_size > max_size_gb * (1024**3):
                logger.error("File exceeds download limit: %s bytes", total_size)
                return False

            with open(dest_path, "wb") as f:
                with tqdm(total=total_size, unit="B", unit_scale=True, desc=dest_path.name) as pbar:
                    for chunk in r.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        return True
    except Exception as e:
        logger.error("Download failed for %s: %s", url, e)
        if dest_path.exists():
            dest_path.unlink()
        return False


def fetch_rcaeval_data(
    include_sock_shop: bool = True,
    max_size_gb: float = 3.0,
) -> Dict[str, dict]:
    """Download and extract RCAEval benchmark dataset subsets."""
    RCAEVAL_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}

    targets = ["RE1-OB.zip"]
    if include_sock_shop:
        targets.append("RE1-SS.zip")

    for filename in targets:
        info = ZENODO_FILES[filename]
        zip_path = DATA_RAW_DIR / filename
        extract_dir = RCAEVAL_DIR / filename.replace(".zip", "")

        # Download if not present
        if not zip_path.exists():
            logger.info("Downloading %s from Zenodo...", filename)
            success = download_file(info["url"], zip_path, max_size_gb=max_size_gb)
            if not success:
                logger.warning("Could not download %s", filename)
                continue

        sha256_hash = compute_sha256(zip_path)
        size_bytes = zip_path.stat().st_size

        # Extract
        if not extract_dir.exists():
            logger.info("Extracting %s to %s...", filename, extract_dir)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

        manifest[filename] = {
            "system": info["system"],
            "sha256": sha256_hash,
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024**2), 2),
            "extract_dir": str(extract_dir),
        }

    manifest_file = DATA_RAW_DIR / "rcaeval_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest

