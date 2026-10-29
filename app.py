#!/usr/bin/env python3
"""
Hugging Face Spaces entry point for Subliminal Weaver.
This file is what Spaces expects as the main Gradio app.
"""

# Re-use the expanded UI
from web_ui import demo

if __name__ == "__main__":
    # Spaces routes traffic to port 7860 by default
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
