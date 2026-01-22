# tabs/pdf_overlay.py
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image, ImageDraw
import tempfile
import os

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
        
        col1, col2, col3 = st.columns(3)
        
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
                horizontal_position = st.selectbox(
                    "Horizontal Position:",
                    ["Left", "Center", "Right"],
                    index=2,
                    key="h_pos"
                )
                
                vertical_position = st.selectbox(
                    "Vertical Position:",
                    ["Top", "Middle", "Bottom"],
                    index=2,
                    key="v_pos"
                )
            else:
                st.info("🖼️ Background mode: Image will fill the entire page")
                horizontal_position = "Center"
                vertical_position = "Middle"
        
        with col3:
            if not is_background:
                # Adjust default size based on page size
                default_width = min(200, int(page_width * 0.3))
                default_height = min(75, int(page_height * 0.1))
                max_width = int(page_width * 0.8)
                max_height = int(page_height * 0.8)
                
                image_width = st.slider("Image Width (px)", 50, max_width, default_width, 10, key="width")
                image_height = st.slider("Image Height (px)", 25, max_height, default_height, 5, key="height")
                
                # Fine-tune position
                x_offset = st.slider("Horizontal Offset", -200, 200, 0, 5, key="x_off")
                y_offset = st.slider("Vertical Offset", -200, 200, 0, 5, key="y_off")
            else:
                st.info("📏 Size automatically set to full page")
                image_width = None
                image_height = None
                x_offset = 0
                y_offset = 0
        
        st.markdown("---")
        
        # PREVIEW SECTION
        preview_canvas = render_preview(pdf_file, img, page_width, page_height, 
                                       is_background, horizontal_position, vertical_position,
                                       image_width, image_height, x_offset, y_offset)
        
        # Display preview
        col_prev1, col_prev2 = st.columns([2, 1])
        
        with col_prev1:
            st.image(preview_canvas, caption="Position Preview (not to scale)", use_container_width=True)
        
        with col_prev2:
            st.info(f"""
            **Preview Info:**
            - Page Size: {page_size_name}
            - Dimensions: {page_width:.0f}×{page_height:.0f}pt
            - Mode: {layer_mode}
            - Position: {horizontal_position} / {vertical_position}
            - Size: {image_width if image_width else 'Full Page'} × {image_height if image_height else 'Full Page'} px
            - Offset: ({x_offset}, {y_offset})
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
                                       is_background, horizontal_position, vertical_position,
                                       image_width, image_height, x_offset, y_offset)
                    
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


def render_preview(pdf_file, img, page_width, page_height, is_background, 
                   horizontal_position, vertical_position, image_width, image_height, 
                   x_offset, y_offset):
    """Render the position preview"""
    preview_width = 600
    preview_height = int(preview_width * (page_height / page_width))
    
    # Try to render the first page of the PDF
    try:
        import fitz  # PyMuPDF
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()
        
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        first_page_obj = pdf_document[0]
        
        zoom = preview_width / first_page_obj.rect.width
        mat = fitz.Matrix(zoom, zoom)
        pix = first_page_obj.get_pixmap(matrix=mat)
        
        preview_canvas = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        preview_height = pix.height
        pdf_document.close()
        
    except Exception as e:
        st.warning(f"⚠️ Could not render PDF preview. Install PyMuPDF (`pip install PyMuPDF`) for better preview.")
        preview_canvas = Image.new('RGB', (preview_width, preview_height), 'white')
        draw = ImageDraw.Draw(preview_canvas)
        draw.rectangle([0, 0, preview_width-1, preview_height-1], outline='gray', width=2)
        
        for i in range(1, 4):
            y = preview_height * i // 4
            draw.line([(0, y), (preview_width, y)], fill='lightgray', width=1)
            x = preview_width * i // 4
            draw.line([(x, 0), (x, preview_height)], fill='lightgray', width=1)
    
    # Calculate scaled position for preview
    scale_factor = preview_width / page_width
    
    if is_background:
        preview_x = 0
        preview_y = 0
        preview_img_width = preview_width
        preview_img_height = preview_height
        
        img_resized = img.resize((preview_img_width, preview_img_height), Image.Resampling.LANCZOS)
        preview_canvas = Image.blend(preview_canvas, img_resized, alpha=0.3)
    else:
        # Calculate position
        x_pos, y_pos = calculate_position(page_width, page_height, image_width, image_height,
                                          horizontal_position, vertical_position, x_offset, y_offset)
        
        preview_x = int(x_pos * scale_factor)
        preview_y = int((page_height - y_pos - image_height) * scale_factor)
        preview_img_width = int(image_width * scale_factor)
        preview_img_height = int(image_height * scale_factor)
        
        img_resized = img.resize((preview_img_width, preview_img_height), Image.Resampling.LANCZOS)
        
        if img.mode == 'RGBA':
            preview_canvas.paste(img_resized, (preview_x, preview_y), img_resized)
        else:
            preview_canvas.paste(img_resized, (preview_x, preview_y))
        
        draw = ImageDraw.Draw(preview_canvas)
        draw.rectangle(
            [preview_x, preview_y, preview_x + preview_img_width, preview_y + preview_img_height],
            outline='red',
            width=2
        )
    
    return preview_canvas


def calculate_position(page_width, page_height, image_width, image_height,
                      horizontal_position, vertical_position, x_offset, y_offset):
    """Calculate the x, y position for the image"""
    if horizontal_position == "Left":
        x_pos = 50
    elif horizontal_position == "Center":
        x_pos = (page_width - image_width) / 2
    else:  # Right
        x_pos = page_width - image_width - 50
    
    if vertical_position == "Top":
        y_pos = page_height - image_height - 50
    elif vertical_position == "Middle":
        y_pos = (page_height - image_height) / 2
    else:  # Bottom
        y_pos = 50
    
    x_pos += x_offset
    y_pos += y_offset
    
    return x_pos, y_pos


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
                is_background, horizontal_position, vertical_position,
                image_width, image_height, x_offset, y_offset):
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
    
    for i in range(num_pages):
        page = reader.pages[i]
        
        # Get actual page dimensions
        current_page_width = float(page.mediabox.width)
        current_page_height = float(page.mediabox.height)
        current_page_size = (current_page_width, current_page_height)
        
        # Only add image to selected pages
        if i in pages_to_process:
            if is_background:
                x_pos = 0
                y_pos = 0
                img_width = current_page_width
                img_height = current_page_height
            else:
                x_pos, y_pos = calculate_position(current_page_width, current_page_height,
                                                  image_width, image_height,
                                                  horizontal_position, vertical_position,
                                                  x_offset, y_offset)
                img_width = image_width
                img_height = image_height
            
            # Create image layer
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=current_page_size)
            can.drawImage(tmp_img_path, x_pos, y_pos, 
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