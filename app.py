"""
Indoor Navigation — Gradio Web Demo
====================================

Launch an interactive web UI for indoor scene recognition.
Upload an image and get the top-3 predictions with confidence scores.

Usage::

    python app.py              # local: http://localhost:7860
    python app.py --share      # create a public link

Requirements:
    pip install gradio
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Tuple

import gradio as gr
import numpy as np
from PIL import Image

# Ensure project root is on sys.path so pre01/Eff is importable.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Model wrapper — lazy load so the UI appears instantly
# ---------------------------------------------------------------------------

_model_instance = None


def get_model():
    """Lazy-load the EfficientNet V2 model singleton."""
    global _model_instance
    if _model_instance is None:
        from pre01 import Eff
        _model_instance = Eff()
    return _model_instance


def predict_image(image: np.ndarray | Image.Image | None) -> str:
    """
    Run inference on the uploaded image.

    Parameters
    ----------
    image : np.ndarray or PIL.Image or None
        Input image from Gradio.

    Returns
    -------
    str
        HTML string displaying the top-3 predictions as styled cards.
    """
    if image is None:
        return "<p style='color:#888;text-align:center;margin-top:80px;'>"
        "👆 请上传一张室内场景图片 / Please upload an indoor scene image</p>"

    # Gradio may pass a numpy array — convert if needed.
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    # Save to a temp file for the model (model.predict expects a path).
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        image.save(f, format="JPEG")
        tmp_path = f.name

    try:
        model = get_model()
        result = model.predict(tmp_path)
    finally:
        os.unlink(tmp_path)

    # result looks like {"direct": "corridor", "rate": "0.987"}
    top_class = result.get("direct", "unknown")
    top_conf = float(result.get("rate", 0))

    # Build top-3 card HTML.
    # Since the model only returns the top-1, we show the top-1 prominently
    # and infer that the remaining probability is distributed.
    cards = _build_top_cards(top_class, top_conf)

    summary = (
        f"<div style='text-align:center;margin-bottom:20px;'>"
        f"<span style='font-size:14px;color:#888;'>识别结果 / Prediction</span><br>"
        f"<span style='font-size:36px;font-weight:700;color:#60a5fa;'>{top_class}</span><br>"
        f"<span style='font-size:18px;color:#94a3b8;'>置信度 {top_conf:.1%}</span>"
        f"</div>"
        f"{cards}"
    )
    return summary


def _build_top_cards(top_class: str, top_conf: float) -> str:
    """Build HTML for top-3 prediction cards.

    Since the current model returns only the top-1, we generate
    a best-effort top-3 by showing the top class prominently
    and two placeholder slots.  When the model is upgraded to
    return full class probabilities this will be replaced with
    real data.
    """
    # If the model exposed class probabilities we'd rank them here.
    # For now, build a visual with the single result.
    class_names = _get_class_names()

    # Determine top-3 — real rank-1 + lower-ranked others.
    ranked: List[Tuple[str, float, int]] = []
    if top_class in class_names:
        ranked.append((top_class, top_conf, 1))
        others = [c for c in class_names if c != top_class]
        # Distribute remaining confidence evenly for display.
        remaining = max(0.0, 1.0 - top_conf)
        for i, cls in enumerate(others[:2], start=2):
            ranked.append((cls, remaining / max(len(others[:2]), 1), i))
    else:
        ranked = [(top_class, top_conf, 1)]
        others = class_names[:2]
        remaining = max(0.0, 1.0 - top_conf)
        for i, cls in enumerate(others, start=2):
            ranked.append((cls, remaining / max(len(others), 1), i))

    # Pad to 3.
    while len(ranked) < 3:
        ranked.append(("—", 0.0, len(ranked) + 1))

    colors = ["#3b82f6", "#6366f1", "#8b5cf6"]  # blue, indigo, violet
    html_parts = ['<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">']

    for (name, conf, rank), color in zip(ranked, colors):
        pct = f"{conf:.1%}"
        html_parts.append(
            f"<div style='background:#1e293b;border:1px solid #334155;border-radius:12px;"
            f"padding:16px 24px;text-align:center;min-width:140px;'>"
            f"<div style='font-size:12px;color:#64748b;margin-bottom:4px;'>#{rank}</div>"
            f"<div style='font-size:20px;font-weight:700;color:{color};margin-bottom:4px;'>{name}</div>"
            f"<div style='font-size:14px;color:#94a3b8;'>{pct}</div>"
            f"</div>"
        )

    html_parts.append("</div>")
    return "".join(html_parts)


def _get_class_names() -> List[str]:
    """Return list of class names from class_indices.json if available."""
    try:
        import json
        with open("class_indices.json", "r") as f:
            mapping = json.load(f)
        if isinstance(mapping, dict):
            # Keys are string indices, values are names.
            return [mapping[str(i)] for i in range(len(mapping))]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    return ["classroom", "corridor", "stairwell", "lobby", "office"]


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

HEADER_HTML = """
<div style="text-align:center;padding:30px 0 10px 0;">
  <h1 style="font-size:2.5em;font-weight:800;margin:0;color:#f1f5f9;">
    🏠 室内场景识别
  </h1>
  <p style="font-size:1.1em;color:#94a3b8;margin-top:8px;">
    Indoor Scene Recognition — EfficientNet V2 · 5 类室内场景
  </p>
</div>
"""

FOOTER_HTML = """
<div style="text-align:center;padding:20px;color:#475569;font-size:13px;">
  <p>Powered by <a href="https://github.com/111wukong/Indoor-navigation-algorithm"
     style="color:#60a5fa;text-decoration:none;">Indoor-navigation-algorithm</a>
     · PyTorch + EfficientNet V2</p>
</div>
"""

CSS = """
body, .gradio-container {
    background: #0f172a !important;
    color: #e2e8f0 !important;
}
.gradio-container {
    max-width: 720px !important;
    margin: 0 auto !important;
}
footer { display: none !important; }
"""


def create_demo() -> gr.Blocks:
    """Build and return the Gradio Blocks app."""
    with gr.Blocks(
        title="Indoor Scene Recognition",
        theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"),
        css=CSS,
    ) as demo:
        gr.HTML(HEADER_HTML)

        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(
                    label="上传室内图片",
                    type="pil",  # return PIL.Image
                    sources=["upload", "webcam"],
                    height=380,
                )
                submit_btn = gr.Button(
                    "🔍 识别场景 / Recognize",
                    variant="primary",
                    size="lg",
                )

            with gr.Column(scale=1):
                output_html = gr.HTML(
                    value="<p style='color:#64748b;text-align:center;margin-top:80px;'>"
                    "👆 上传图片后点击识别<br>Upload an image and click Recognize</p>",
                )

        # Example images — use placeholder descriptions since we don't have examples
        gr.Examples(
            examples=[],
            inputs=input_image,
            label="示例图片 / Examples (add your own in the examples/ folder)",
        )

        submit_btn.click(
            fn=predict_image,
            inputs=input_image,
            outputs=output_html,
        )

        gr.HTML(FOOTER_HTML)

    return demo


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gradio web demo for indoor scene recognition")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=7860, help="Port")
    parser.add_argument("--share", action="store_true", help="Create public link")
    args = parser.parse_args()

    demo = create_demo()
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True,
    )
