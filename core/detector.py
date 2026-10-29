"""
Basic steganography detection helpers.
LSB plane analysis and simple statistical checks.
"""

from PIL import Image
import numpy as np


def extract_lsb_plane(image_path: str, output_path: str) -> None:
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    lsb = (arr & 1) * 255
    Image.fromarray(lsb.astype(np.uint8)).save(output_path)
    print(f"LSB plane saved → {output_path}")


def simple_lsb_score(image_path: str) -> float:
    img = Image.open(image_path).convert("L")
    arr = np.array(img)
    lsb = arr & 1
    diffs = np.abs(np.diff(lsb.astype(int), axis=1)).mean()
    return float(diffs)


def report(image_path: str) -> dict:
    score = simple_lsb_score(image_path)
    return {
        "file": image_path,
        "lsb_transition_score": round(score, 4),
        "note": "Low scores (~0.5) are common for natural images. Structured high scores may indicate LSB embedding. This is a basic heuristic only.",
    }
