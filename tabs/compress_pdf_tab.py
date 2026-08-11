"""
Compress PDF Tab
------------------
Drop-in tab module for the PDF-Image-Overlay-Tool Streamlit app.

Save this file as tabs/compress_pdf_tab.py (same folder as your other tab
modules like pdf_merger.py, split_pdf_tab.py), then in app.py:

    from tabs import compress_pdf_tab

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "PDF Image Overlay",
        "Image to PDF Converter",
        "PDF Merger",
        "Split PDF",
        "Compress PDF",
    ])

    with tab5:
        compress_pdf_tab.render()

Requires: pikepdf, Pillow
    pip install pikepdf Pillow
"""

import io
import os

import streamlit as st
from PIL import Image

try:
    import pikepdf
    from pikepdf import Name
except ImportError:
    pikepdf = None


QUALITY_PRESETS = {
    "Low compression (best quality)": {"quality": 80, "max_dim": 2500},
    "Recommended": {"quality": 60, "max_dim": 1800},
    "High compression (smallest size)": {"quality": 35, "max_dim": 1200},
}


def _compress_pdf(input_bytes: bytes, quality: int, max_dim: int) -> tuple[bytes, dict]:
    """Recompress embedded images in a PDF. Returns (output_bytes, stats)."""
    pdf = pikepdf.open(io.BytesIO(input_bytes))

    images_processed = 0
    images_skipped = 0

    for page in pdf.pages:
        if "/Resources" not in page or "/XObject" not in page.Resources:
            continue

        xobjects = page.Resources.XObject
        for name in list(xobjects.keys()):
            xobj = xobjects[name]
            if xobj.get("/Subtype") != Name("/Image"):
                continue

            # Skip tiny images (icons, bullets) - not worth recompressing
            try:
                if int(xobj.Width) < 50 or int(xobj.Height) < 50:
                    continue
            except Exception:
                pass

            try:
                pdf_image = pikepdf.PdfImage(xobj)
                pil_image = pdf_image.as_pil_image()
            except Exception:
                images_skipped += 1
                continue

            try:
                w, h = pil_image.size
                if max(w, h) > max_dim:
                    scale = max_dim / max(w, h)
                    pil_image = pil_image.resize(
                        (max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS
                    )

                if pil_image.mode in ("RGBA", "P", "LA"):
                    pil_image = pil_image.convert("RGB")

                buf = io.BytesIO()
                pil_image.save(buf, format="JPEG", quality=quality, optimize=True)
                buf.seek(0)
                new_bytes = buf.read()

                # Only replace if it's actually smaller than the original stream
                if len(new_bytes) < len(xobj.read_bytes()):
                    xobj.write(new_bytes, filter=Name("/DCTDecode"))
                    xobj.ColorSpace = Name("/DeviceRGB")
                    xobj.BitsPerComponent = 8
                    xobj.Width = pil_image.width
                    xobj.Height = pil_image.height
                    if "/SMask" in xobj:
                        del xobj["/SMask"]
                    if "/Decode" in xobj:
                        del xobj["/Decode"]
                    images_processed += 1
                else:
                    images_skipped += 1
            except Exception:
                images_skipped += 1
                continue

    out_buf = io.BytesIO()
    pdf.save(
        out_buf,
        compress_streams=True,
        object_stream_mode=pikepdf.ObjectStreamMode.generate,
        linearize=False,
    )
    pdf.close()
    out_buf.seek(0)

    stats = {
        "images_processed": images_processed,
        "images_skipped": images_skipped,
    }
    return out_buf.read(), stats


def _format_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def render():
    st.header("🗜️ Compress PDF")
    st.write(
        "Shrink PDF file size by recompressing embedded images. "
        "Best for PDFs made of scanned pages or high-resolution photos."
    )

    if pikepdf is None:
        st.error(
            "The `pikepdf` package is required for this tab. "
            "Add `pikepdf` to requirements.txt and reinstall dependencies."
        )
        return

    uploaded_pdf = st.file_uploader("Upload PDF to compress", type=["pdf"], key="compress_pdf_uploader")

    if uploaded_pdf is None:
        st.info("Upload a PDF to get started.")
        return

    input_bytes = uploaded_pdf.getvalue()
    original_size = len(input_bytes)
    st.success(f"Loaded **{uploaded_pdf.name}** — {_format_size(original_size)}")

    preset_name = st.radio(
        "Compression level",
        list(QUALITY_PRESETS.keys()),
        index=1,
        horizontal=True,
    )

    with st.expander("Advanced settings"):
        preset = QUALITY_PRESETS[preset_name]
        quality = st.slider("JPEG quality", min_value=10, max_value=95, value=preset["quality"])
        max_dim = st.slider(
            "Max image dimension (px)",
            min_value=500,
            max_value=4000,
            value=preset["max_dim"],
            step=100,
            help="Images larger than this on their longest side will be downsampled.",
        )

    if st.button("Compress PDF", type="primary"):
        with st.spinner("Compressing... this can take a moment for large files."):
            try:
                output_bytes, stats = _compress_pdf(input_bytes, quality=quality, max_dim=max_dim)
            except Exception as e:
                st.error(f"Compression failed: {e}")
                return

        new_size = len(output_bytes)
        saved_pct = max(0, (1 - new_size / original_size) * 100) if original_size else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Original size", _format_size(original_size))
        col2.metric("Compressed size", _format_size(new_size), delta=f"-{saved_pct:.0f}%")
        col3.metric("Images optimized", stats["images_processed"])

        if new_size >= original_size:
            st.warning(
                "Compressed file isn't smaller — this PDF likely has little "
                "recompressible image data (e.g. mostly text/vector content)."
            )

        base_name = uploaded_pdf.name.rsplit(".", 1)[0]
        st.download_button(
            label="⬇️ Download compressed PDF",
            data=output_bytes,
            file_name=f"{base_name}_compressed.pdf",
            mime="application/pdf",
        )
