from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict


DEFAULT_COMFYUI_URL = "http://127.0.0.1:8188"
LEGACY_VGF_ROOT = "/mnt/c/ai_projects/video-gen-factory"


def project_root() -> Path:
    root = os.environ.get("VIDEO_FACTORY_ROOT") or os.environ.get("VGF_ROOT")
    if root:
        return Path(root).expanduser().resolve()
    return Path(__file__).resolve().parent


def comfyui_url() -> str:
    return os.environ.get("COMFYUI_URL", DEFAULT_COMFYUI_URL).rstrip("/")


def rewrite_paths(payload: Any, replacements: Dict[str, str]) -> Any:
    if isinstance(payload, str):
        for old, new in replacements.items():
            payload = payload.replace(old, new)
        return payload
    if isinstance(payload, list):
        return [rewrite_paths(item, replacements) for item in payload]
    if isinstance(payload, dict):
        return {key: rewrite_paths(value, replacements) for key, value in payload.items()}
    return payload


def workflow_path(name_or_path: str) -> Path:
    path = Path(name_or_path)
    if path.is_absolute():
        return path
    return project_root() / "workflows" / name_or_path


def output_dir() -> Path:
    return Path(os.environ.get("VIDEO_FACTORY_OUTPUT_DIR", str(project_root() / "output_videos"))).expanduser().resolve()

