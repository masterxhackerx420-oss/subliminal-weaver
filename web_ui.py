#!/usr/bin/env python3
"""
Expanded Gradio web UI for Subliminal Weaver (WolfSec edition).
Run: python web_ui.py
Requires: pip install gradio pillow numpy cryptography
"""

import gradio as gr
import tempfile
import os

from core.image_stego import embed_message, extract_message, capacity
from core.audio_stego import embed_message_audio, extract_message_audio
from core.detector import extract_lsb_plane, report

THEME = gr.themes.Soft(
    primary_hue="cyan",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_background_fill="*neutral_950",
    body_text_color="*neutral_200",
    block_background_fill="*neutral_900",
    block_border_color="*neutral_700",
    button_primary_background_fill="*primary_600",
    button_primary_text_color="white",
)

def get_capacity(image):
    if image is None:
        return "Upload an image first"
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    image.save(tmp.name)
    try:
        cap = capacity(tmp.name)
        return f"≈ {cap:,} bytes (~{cap/1024:.1f} KB) available"
    except Exception as e:
        return f"Error: {e}"
    finally:
        os.unlink(tmp.name)

def embed_ui(image, message, password, use_audio=False, audio_file=None):
    if not message:
        return None, None, "Enter a message"
    if image is None and audio_file is None:
        return None, None, "Provide a cover image or audio"
    try:
        if image is not None and not use_audio:
            tmp_in = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            image.save(tmp_in.name)
            tmp_out = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            embed_message(tmp_in.name, message, tmp_out.name, password or None)
            os.unlink(tmp_in.name)
            return tmp_out.name, None, "✅ Embedded successfully. Download the image below."
        elif audio_file is not None:
            tmp_out = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            embed_message_audio(audio_file, message, tmp_out.name, password or None)
            return None, tmp_out.name, "✅ Embedded in audio successfully."
        else:
            return None, None, "Choose image or audio mode"
    except Exception as e:
        return None, None, f"❌ Error: {e}"

def extract_ui(image, password, audio_file=None):
    if image is None and audio_file is None:
        return "Provide an image or audio file"
    try:
        if image is not None:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            image.save(tmp.name)
            msg = extract_message(tmp.name, password or None)
            os.unlink(tmp.name)
            return msg
        else:
            return extract_message_audio(audio_file, password or None)
    except Exception as e:
        return f"❌ Error: {e}"

def analyze_ui(image):
    if image is None:
        return "Upload an image", None
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    image.save(tmp.name)
    try:
        info = report(tmp.name)
        text = "\n".join(f"{k}: {v}" for k, v in info.items())
        lsb_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        extract_lsb_plane(tmp.name, lsb_path)
        return text, lsb_path
    except Exception as e:
        return f"Error: {e}", None
    finally:
        os.unlink(tmp.name)

with gr.Blocks(theme=THEME, title="Subliminal Weaver — WolfSec") as demo:
    gr.Markdown(
        """
        # 🐺 Subliminal Weaver
        **WolfSec / DebianGang edition**

        Local-only steganography. Embed and extract messages in images & WAV audio.  
        No telemetry. For creative projects, album art, tracks, and research.
        """
    )

    with gr.Tabs():
        with gr.Tab("🖼️ Embed"):
            with gr.Row():
                with gr.Column():
                    img_in = gr.Image(type="pil", label="Cover image (PNG preferred)")
                    audio_in = gr.Audio(type="filepath", label="Or WAV audio (optional)")
                    msg = gr.Textbox(label="Message to hide", lines=4, placeholder="The cache is the ghost...")
                    pw = gr.Textbox(label="Password (optional — encrypts the payload)", type="password")
                    use_audio = gr.Checkbox(label="Use audio instead of image", value=False)
                    btn_embed = gr.Button("Embed Message", variant="primary")
                with gr.Column():
                    out_img = gr.Image(label="Output image (download)")
                    out_audio = gr.Audio(label="Output audio (download)")
                    status = gr.Textbox(label="Status", interactive=False)
                    cap_display = gr.Textbox(label="Image capacity", interactive=False)
                    btn_cap = gr.Button("Check capacity")

            btn_cap.click(get_capacity, img_in, cap_display)
            btn_embed.click(
                embed_ui,
                [img_in, msg, pw, use_audio, audio_in],
                [out_img, out_audio, status]
            )

        with gr.Tab("🔍 Extract"):
            with gr.Row():
                with gr.Column():
                    img_ex = gr.Image(type="pil", label="Image with hidden message")
                    audio_ex = gr.Audio(type="filepath", label="Or WAV audio")
                    pw_ex = gr.Textbox(label="Password (if used)", type="password")
                    btn_ex = gr.Button("Extract", variant="primary")
                with gr.Column():
                    result = gr.Textbox(label="Extracted message", lines=8, interactive=False)
            btn_ex.click(extract_ui, [img_ex, pw_ex, audio_ex], result)

        with gr.Tab("🔬 Analyze"):
            with gr.Row():
                with gr.Column():
                    img_an = gr.Image(type="pil", label="Image to analyze")
                    btn_an = gr.Button("Analyze", variant="primary")
                with gr.Column():
                    report_txt = gr.Textbox(label="Analysis report", lines=6, interactive=False)
                    lsb_img = gr.Image(label="LSB plane visualization")
            btn_an.click(analyze_ui, img_an, [report_txt, lsb_img])

        with gr.Tab("ℹ️ About"):
            gr.Markdown(
                """
                ### About Subliminal Weaver

                Lightweight, local-first steganography tool.

                **Features**
                - LSB embedding in PNG/BMP images and WAV audio
                - Optional password encryption (Fernet + PBKDF2)
                - Capacity check and basic LSB analysis
                - CLI + this web UI

                **Responsible use**  
                For creative work (hidden messages in art/music), personal privacy, and research.  
                Do not use to conceal illegal content.

                **WolfSec / DebianGang**  
                Part of the DebianGang toolkit. Fork freely.

                Run locally: `python web_ui.py`  
                CLI: `python weaver.py --help`
                """
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False)
