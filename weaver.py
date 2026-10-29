#!/usr/bin/env python3
"""
Subliminal Weaver — WolfSec edition
Open-source steganography tool for embedding and extracting messages in images and audio.
Local-only. For creative and research use.
"""

import argparse
import sys
from pathlib import Path

from core.image_stego import embed_message, extract_message, capacity
from core.audio_stego import embed_message_audio, extract_message_audio
from core.detector import extract_lsb_plane, report


def main():
    parser = argparse.ArgumentParser(
        description="Subliminal Weaver — Hide and find messages in images & audio (WolfSec)",
        epilog="Use responsibly. Steganography is for privacy, art, and research."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Embed
    emb = sub.add_parser("embed", help="Embed a message")
    emb.add_argument("carrier", help="Input image (PNG/BMP) or WAV")
    emb.add_argument("message", help="Text message to hide")
    emb.add_argument("-o", "--output", required=True, help="Output file")
    emb.add_argument("-p", "--password", help="Optional password for encryption")

    # Extract
    ext = sub.add_parser("extract", help="Extract a message")
    ext.add_argument("carrier", help="Image or WAV containing the message")
    ext.add_argument("-p", "--password", help="Password if encrypted")

    # Detect / analyze
    det = sub.add_parser("analyze", help="Basic analysis of an image")
    det.add_argument("image", help="Image to analyze")
    det.add_argument("--lsb-plane", help="Save LSB plane visualization to this path")

    # Capacity
    cap = sub.add_parser("capacity", help="Show approximate capacity of an image")
    cap.add_argument("image")

    args = parser.parse_args()

    try:
        if args.command == "embed":
            path = Path(args.carrier)
            if path.suffix.lower() in {".png", ".bmp", ".jpg", ".jpeg"}:
                if path.suffix.lower() in {".jpg", ".jpeg"}:
                    print("Warning: JPEG is lossy. Prefer PNG for reliable embedding.")
                embed_message(str(path), args.message, args.output, args.password)
            elif path.suffix.lower() == ".wav":
                embed_message_audio(str(path), args.message, args.output, args.password)
            else:
                print("Unsupported format. Use PNG, BMP, or WAV.")
                sys.exit(1)

        elif args.command == "extract":
            path = Path(args.carrier)
            if path.suffix.lower() in {".png", ".bmp"}:
                msg = extract_message(str(path), args.password)
                print("Extracted message:")
                print(msg)
            elif path.suffix.lower() == ".wav":
                msg = extract_message_audio(str(path), args.password)
                print("Extracted message:")
                print(msg)
            else:
                print("Unsupported format.")
                sys.exit(1)

        elif args.command == "analyze":
            info = report(args.image)
            print("Analysis:")
            for k, v in info.items():
                print(f"  {k}: {v}")
            if args.lsb_plane:
                extract_lsb_plane(args.image, args.lsb_plane)

        elif args.command == "capacity":
            cap_bytes = capacity(args.image)
            print(f"Approximate capacity: {cap_bytes} bytes (~{cap_bytes/1024:.1f} KB)")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
