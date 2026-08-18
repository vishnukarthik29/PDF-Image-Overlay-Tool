# tabs/pdf_overlay.py
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image, ImageDraw
import base64
import tempfile
import os

# streamlit-drawable-canvas (0.9.3, latest) calls streamlit.elements.image.image_to_url,
# an internal helper removed in newer Streamlit versions. Shim it with a plain base64
# data URL (which the component just assigns as an <img src>) before importing the package.
import streamlit.elements.image as _st_image
if not hasattr(_st_image, "image_to_url"):
    def _image_to_url_shim(image, *_args, **_kwargs):
        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
    _st_image.image_to_url = _image_to_url_shim

from streamlit_drawable_canvas import st_canvas

def get_output_filename(original_filename):
    """Generate output filename based on original PDF name"""
    if original_filename.lower().endswith('.pdf'):
        base_name = original_filename[:-4]
        return f"{base_name}_signed.pdf"
    return f"{original_filename}_signed.pdf"

def render():
    """Render the PDF Image Overlay tab"""
    st.markdown("Upload a PDF and an image to add your signature or stamp to the document")
    
    # Create two columns for uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📑 Upload PDF")
        pdf_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf")
    
    with col2:
        st.subheader("🖼️ Upload Image")
        image_file = st.file_uploader("Choose an image (PNG recommended for transparency)", 
                                     type=['png', 'jpg', 'jpeg'], key="image")
    
    # Show preview if files are uploaded
    if pdf_file and image_file:
        st.success("✅ Files uploaded successfully!")
        
        # Display image preview
        st.subheader("Image Preview")
        img = Image.open(image_file)
        st.image(img, width=200, caption="Your uploaded image")
        
        # Get PDF info and detect page size
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        # Detect page size from first page
        first_page = pdf_reader.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)
        
        # Determine page size name
        page_size_name = get_page_size_name(page_width, page_height)
        
        st.info(f"📄 PDF has {num_pages} page(s) | Page Size: **{page_size_name}** ({page_width:.1f} × {page_height:.1f} points)")
        
        st.markdown("---")

        # Position settings
        st.subheader("⚙️ Position Settings")

        col1, col2 = st.columns(2)

        with col1:
            # Add background/overlay option
            layer_mode = st.radio(
                "Layer Mode:",
                ["Overlay (on top)", "Background (behind)"],
                key="layer_mode",
                help="Choose whether to place the image on top of or behind the PDF content"
            )

            page_selection = st.radio(
                "Apply to pages:",
                ["All pages", "First page only", "Last page only", "Custom range"],
                key="page_sel"
            )

            if page_selection == "Custom range":
                page_range = st.text_input(
                    "Enter page numbers (e.g., 1,3,5 or 1-3)",
                    value="1",
                    key="range"
                )

            # Determine if using background mode
            is_background = "Background" in layer_mode

        with col2:
            if not is_background:
                # Adjust default size based on page size
                default_width = min(200, int(page_width * 0.3))
                default_height = min(75, int(page_height * 0.1))
                max_width = int(page_width * 0.8)
                max_height = int(page_height * 0.8)

                image_width = st.slider("Image Width (px)", 50, max_width, default_width, 10, key="width")
                image_height = st.slider("Image Height (px)", 25, max_height, default_height, 5, key="height")
            else:
                st.info("🖼️ Background mode: Image will fill the entire page")
                image_width = None
                image_height = None

        # Session state anchor: top-left corner of the stamp, in canvas pixels
        # (canvas origin is top-left, unlike PDF points which are bottom-left).
        anchor_key = "overlay_anchor_px"
        size_key = "overlay_anchor_size"
        nonce_key = "overlay_canvas_nonce"
        current_size_signature = (round(page_width), round(page_height), image_width, image_height)

        canvas_width = 600
        canvas_height = int(canvas_width * (page_height / page_width))
        canvas_scale = canvas_width / page_width  # canvas px per PDF point

        if not is_background:
            if anchor_key not in st.session_state or st.session_state.get(size_key) != current_size_signature:
                # Center the stamp by default
                st.session_state[anchor_key] = (
                    (canvas_width - image_width * canvas_scale) / 2,
                    (canvas_height - image_height * canvas_scale) / 2,
                )
                st.session_state[size_key] = current_size_signature
                st.session_state[nonce_key] = st.session_state.get(nonce_key, 0) + 1

            st.markdown("**🖱️ Drag the stamp directly on the preview below to reposition it**")

            preset_cols = st.columns(6)
            margin_px = 25
            presets = {
                "↖ Top-Left": (margin_px, margin_px),
                "↑ Top-Center": ((canvas_width - image_width * canvas_scale) / 2, margin_px),
                "↗ Top-Right": (canvas_width - image_width * canvas_scale - margin_px, margin_px),
                "↙ Bottom-Left": (margin_px, canvas_height - image_height * canvas_scale - margin_px),
                "↓ Bottom-Center": ((canvas_width - image_width * canvas_scale) / 2, canvas_height - image_height * canvas_scale - margin_px),
                "↘ Bottom-Right": (canvas_width - image_width * canvas_scale - margin_px, canvas_height - image_height * canvas_scale - margin_px),
            }
            for preset_col, (label, pos) in zip(preset_cols, presets.items()):
                if preset_col.button(label, key=f"preset_{label}", use_container_width=True):
                    st.session_state[anchor_key] = pos
                    st.session_state[nonce_key] = st.session_state.get(nonce_key, 0) + 1

            left_px, top_px = st.session_state[anchor_key]
        else:
            left_px, top_px = 0, 0

        st.markdown("---")

        # PREVIEW SECTION (draggable canvas)
        col_prev1, col_prev2 = st.columns([2, 1])

        with col_prev1:
            page_background = render_page_background(pdf_file, canvas_width, canvas_height)

            if not is_background:
                canvas_key = f"overlay_canvas_{st.session_state.get(nonce_key, 0)}"
                # The component's frontend reloads the canvas via loadFromJSON whenever
                # the incoming initial_drawing prop is not deep-equal to the drawing it
                # captured on first mount (its "initialState", which never changes after
                # that). So we must keep passing the *exact same* dict every rerun for a
                # given canvas_key -- rebuilding it (even with identical-looking values)
                # or passing None (which becomes a *different*, near-empty dict) makes it
                # look like a real external change and forces a reset, which caused drags
                # to silently snap back and then jump on the next drag. Cache the dict in
                # session_state once per canvas_key and reuse the same object thereafter.
                drawing_cache_key = "overlay_canvas_drawing"
                drawing_cache_owner_key = "overlay_canvas_drawing_owner"
                if st.session_state.get(drawing_cache_owner_key) != canvas_key:
                    initial_drawing = build_stamp_drawing(img, left_px, top_px, image_width, image_height, canvas_scale)
                    st.session_state[drawing_cache_key] = initial_drawing
                    st.session_state[drawing_cache_owner_key] = canvas_key
                else:
                    initial_drawing = st.session_state[drawing_cache_key]

                canvas_result = st_canvas(
                    background_image=page_background,
                    background_color="#ffffff",
                    height=canvas_height,
                    width=canvas_width,
                    drawing_mode="transform",
                    initial_drawing=initial_drawing,
                    display_toolbar=False,
                    update_streamlit=True,
                    key=canvas_key,
                )

                if canvas_result.json_data is not None:
                    objects = canvas_result.json_data.get("objects", [])
                    if objects:
                        stamp_obj = objects[0]
                        new_left, new_top = stamp_obj["left"], stamp_obj["top"]
                        if (round(new_left), round(new_top)) != (round(left_px), round(top_px)):
                            st.session_state[anchor_key] = (new_left, new_top)
                            left_px, top_px = new_left, new_top

                # Convert canvas pixels (top-left origin) to PDF points (bottom-left origin)
                x_pos = left_px / canvas_scale
                y_pos = page_height - (top_px / canvas_scale) - image_height
            else:
                bg_preview = Image.blend(
                    page_background.convert("RGB"),
                    img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS).convert("RGB"),
                    alpha=0.3
                )
                st.image(bg_preview, caption="Position Preview (not to scale)", use_container_width=True)
                x_pos, y_pos = 0, 0

        with col_prev2:
            st.info(f"""
            **Preview Info:**
            - Page Size: {page_size_name}
            - Dimensions: {page_width:.0f}×{page_height:.0f}pt
            - Mode: {layer_mode}
            - Size: {image_width if image_width else 'Full Page'} × {image_height if image_height else 'Full Page'} px
            - Position: ({x_pos:.0f}, {y_pos:.0f}) pt
            """)

        st.markdown("---")
        
        # Generate button
        if st.button("🎨 Generate PDF", type="primary", use_container_width=True, key="generate_overlay"):
            with st.spinner("Processing PDF..."):
                try:
                    # Reset file pointers
                    pdf_file.seek(0)
                    image_file.seek(0)
                    
                    # Parse page selection
                    if page_selection == "Custom range":
                        pages_to_process = parse_page_range(page_range, num_pages)
                    else:
                        pages_to_process = get_pages_to_process(page_selection, num_pages)
                    
                    # Process the PDF
                    output = process_pdf(pdf_file, image_file, pages_to_process, num_pages,
                                       is_background, image_width, image_height, x_pos, y_pos)
                    
                    # Success message and download button
                    st.success("✅ PDF generated successfully!")
                    
                    # Generate output filename based on original PDF name
                    output_filename = get_output_filename(pdf_file.name)
                    
                    st.download_button(
                        label="⬇️ Download Signed PDF",
                        data=output,
                        file_name=output_filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    st.exception(e)
    
    else:
        st.info("👆 Please upload both a PDF file and an image to get started")


def get_page_size_name(width, height):
    """Determine the name of the page size"""
    tolerance = 5
    
    sizes = {
        'Letter': (612, 792),
        'A4': (595.27, 841.89),
        'Legal': (612, 1008),
        'A3': (841.89, 1190.55),
        'A5': (419.53, 595.27),
        'Tabloid': (792, 1224),
    }
    
    for name, (w, h) in sizes.items():
        if (abs(width - w) < tolerance and abs(height - h) < tolerance) or \
           (abs(width - h) < tolerance and abs(height - w) < tolerance):
            return name
    
    return f"Custom ({width:.0f}x{height:.0f}pt)"


def render_page_background(pdf_file, canvas_width, canvas_height):
    """Render the first page of the PDF as a PIL image sized for the canvas."""
    try:
        import fitz  # PyMuPDF
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()

        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        first_page_obj = pdf_document[0]

        zoom = canvas_width / first_page_obj.rect.width
        mat = fitz.Matrix(zoom, zoom)
        pix = first_page_obj.get_pixmap(matrix=mat)

        background = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pdf_document.close()

        if background.size != (canvas_width, canvas_height):
            background = background.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)

    except Exception:
        st.warning("⚠️ Could not render PDF preview. Install PyMuPDF (`pip install PyMuPDF`) for better preview.")
        background = Image.new('RGB', (canvas_width, canvas_height), 'white')
        draw = ImageDraw.Draw(background)
        draw.rectangle([0, 0, canvas_width - 1, canvas_height - 1], outline='gray', width=2)

        for i in range(1, 4):
            y = canvas_height * i // 4
            draw.line([(0, y), (canvas_width, y)], fill='lightgray', width=1)
            x = canvas_width * i // 4
            draw.line([(x, 0), (x, canvas_height)], fill='lightgray', width=1)

    return background


def build_stamp_drawing(img, left_px, top_px, image_width, image_height, canvas_scale):
    """Build the Fabric.js initial_drawing JSON for a draggable (not resizable/
    rotatable) stamp image object, positioned at (left_px, top_px) in canvas pixels."""
    buffer = BytesIO()
    img.convert("RGBA").save(buffer, format="PNG")
    data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")

    target_width_px = image_width * canvas_scale
    target_height_px = image_height * canvas_scale

    stamp_object = {
        "type": "image",
        "version": "4.4.0",
        "left": left_px,
        "top": top_px,
        "width": img.width,
        "height": img.height,
        "scaleX": target_width_px / img.width,
        "scaleY": target_height_px / img.height,
        "src": data_url,
        "crossOrigin": None,
        "hasControls": False,
        "hasRotatingPoint": False,
        "hasBorders": True,
        "lockScalingX": True,
        "lockScalingY": True,
        "lockRotation": True,
        "selectable": True,
        "evented": True,
    }

    return {"version": "4.4.0", "objects": [stamp_object]}


def get_pages_to_process(page_selection, num_pages):
    """Get the list of page indices to process"""
    if page_selection == "All pages":
        return list(range(num_pages))
    elif page_selection == "First page only":
        return [0]
    elif page_selection == "Last page only":
        return [num_pages - 1]
    return []


def parse_page_range(page_range, num_pages):
    """Parse custom page range"""
    pages_to_process = []
    try:
        if '-' in page_range:
            start, end = map(int, page_range.split('-'))
            pages_to_process = list(range(start-1, min(end, num_pages)))
        else:
            pages_to_process = [int(p.strip())-1 for p in page_range.split(',') 
                              if 0 <= int(p.strip())-1 < num_pages]
    except:
        st.error("Invalid page range format")
        st.stop()
    
    return pages_to_process


def process_pdf(pdf_file, image_file, pages_to_process, num_pages,
                is_background, image_width, image_height, x_pos, y_pos):
    """Process the PDF and add image overlay"""
    # Reload image for processing
    image_file.seek(0)
    img = Image.open(image_file)

    # Save image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
        img.save(tmp_img.name, 'PNG')
        tmp_img_path = tmp_img.name

    # Process PDF
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    # Reference page size used when the stamp was positioned in the preview,
    # so positions scale proportionally on pages with different dimensions.
    reference_page = reader.pages[0]
    reference_width = float(reference_page.mediabox.width)
    reference_height = float(reference_page.mediabox.height)

    for i in range(num_pages):
        page = reader.pages[i]

        # Get actual page dimensions
        current_page_width = float(page.mediabox.width)
        current_page_height = float(page.mediabox.height)
        current_page_size = (current_page_width, current_page_height)

        # Only add image to selected pages
        if i in pages_to_process:
            if is_background:
                page_x_pos = 0
                page_y_pos = 0
                img_width = current_page_width
                img_height = current_page_height
            else:
                width_ratio = current_page_width / reference_width
                height_ratio = current_page_height / reference_height
                page_x_pos = x_pos * width_ratio
                page_y_pos = y_pos * height_ratio
                img_width = image_width * width_ratio
                img_height = image_height * height_ratio
            
            # Create image layer
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=current_page_size)
            can.drawImage(tmp_img_path, page_x_pos, page_y_pos,
                        width=img_width, height=img_height,
                        mask='auto')
            can.save()
            packet.seek(0)
            
            # Merge based on layer mode
            image_layer = PdfReader(packet)
            if is_background:
                image_page = image_layer.pages[0]
                image_page.merge_page(page)
                writer.add_page(image_page)
            else:
                page.merge_page(image_layer.pages[0])
                writer.add_page(page)
        else:
            writer.add_page(page)
    
    # Create output PDF
    output = BytesIO()
    writer.write(output)
    output.seek(0)
    
    # Clean up temp file
    os.unlink(tmp_img_path)
    
    return output