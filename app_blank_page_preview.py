import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os

st.set_page_config(page_title="PDF Tools", page_icon="📄", layout="wide")

st.title("📄 PDF Tools Suite")

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["📝 PDF Image Overlay", "🖼️ Image to PDF Converter", "🔗 PDF Merger"])

# TAB 1: PDF Image Overlay (Original Functionality)
with tab1:
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
        
        # Get PDF info
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        st.info(f"📄 PDF has {num_pages} page(s)")
        
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
                image_width = st.slider("Image Width (px)", 50, 400, 200, 10, key="width")
                image_height = st.slider("Image Height (px)", 25, 300, 75, 5, key="height")
                
                # Fine-tune position
                x_offset = st.slider("Horizontal Offset", -200, 200, 0, 5, key="x_off")
                y_offset = st.slider("Vertical Offset", -200, 200, 0, 5, key="y_off")
            else:
                st.info("📏 Size automatically set to full page")
                image_width = None  # Will be set to page width
                image_height = None  # Will be set to page height
                x_offset = 0
                y_offset = 0
        
        st.markdown("---")
        
        # PREVIEW SECTION
        st.subheader("👁️ Position Preview")
        
        # Create preview canvas
        preview_width = 400
        preview_height = int(preview_width * (792/612))  # Maintain letter aspect ratio
        
        # Create a white canvas representing the PDF page
        preview_canvas = Image.new('RGB', (preview_width, preview_height), 'white')
        draw = ImageDraw.Draw(preview_canvas)
        
        # Draw border
        draw.rectangle([0, 0, preview_width-1, preview_height-1], outline='gray', width=2)
        
        # Draw grid lines for reference
        for i in range(1, 4):
            y = preview_height * i // 4
            draw.line([(0, y), (preview_width, y)], fill='lightgray', width=1)
            x = preview_width * i // 4
            draw.line([(x, 0), (x, preview_height)], fill='lightgray', width=1)
        
        # Add text labels
        try:
            # Draw corner labels (smaller size)
            draw.text((10, 10), "Top-Left", fill='lightgray')
            draw.text((preview_width-80, 10), "Top-Right", fill='lightgray')
            draw.text((10, preview_height-25), "Bottom-Left", fill='lightgray')
            draw.text((preview_width-100, preview_height-25), "Bottom-Right", fill='lightgray')
        except:
            pass  # Skip if font issues
        
        # Calculate scaled position for preview
        scale_factor = preview_width / 612  # Scale from letter size to preview size
        
        if is_background:
            # Full page background preview
            preview_x = 0
            preview_y = 0
            preview_img_width = preview_width
            preview_img_height = preview_height
            
            # Resize and place the image
            img_resized = img.resize((preview_img_width, preview_img_height), Image.Resampling.LANCZOS)
            
            # Blend with canvas to show it's behind
            preview_canvas = Image.blend(preview_canvas, img_resized, alpha=0.3)
            
        else:
            # Calculate actual position on PDF
            page_width, page_height = letter
            
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
            
            # Apply offsets
            x_pos += x_offset
            y_pos += y_offset
            
            # Scale to preview coordinates
            preview_x = int(x_pos * scale_factor)
            preview_y = int((page_height - y_pos - image_height) * scale_factor)  # Flip Y axis
            preview_img_width = int(image_width * scale_factor)
            preview_img_height = int(image_height * scale_factor)
            
            # Resize the uploaded image to preview size
            img_resized = img.resize((preview_img_width, preview_img_height), Image.Resampling.LANCZOS)
            
            # Paste the image onto preview canvas
            if img.mode == 'RGBA':
                preview_canvas.paste(img_resized, (preview_x, preview_y), img_resized)
            else:
                preview_canvas.paste(img_resized, (preview_x, preview_y))
            
            # Draw a red border around the image position
            draw = ImageDraw.Draw(preview_canvas)
            draw.rectangle(
                [preview_x, preview_y, preview_x + preview_img_width, preview_y + preview_img_height],
                outline='red',
                width=2
            )
        
        # Display preview
        col_prev1, col_prev2 = st.columns([2, 1])
        with col_prev1:
            st.image(preview_canvas, caption="Position Preview (not to scale)", use_container_width=True)
        
        with col_prev2:
            st.info(f"""
            **Preview Info:**
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
                    pages_to_process = []
                    if page_selection == "All pages":
                        pages_to_process = list(range(num_pages))
                    elif page_selection == "First page only":
                        pages_to_process = [0]
                    elif page_selection == "Last page only":
                        pages_to_process = [num_pages - 1]
                    else:  # Custom range
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
                    
                    # Calculate position based on selection
                    page_width, page_height = letter  # 612 x 792 points
                    
                    # Determine if using background mode
                    is_background = "Background" in layer_mode
                    
                    if is_background:
                        # Full page background
                        x_pos = 0
                        y_pos = 0
                        img_width = page_width
                        img_height = page_height
                    else:
                        # Positioned overlay
                        # Horizontal position
                        if horizontal_position == "Left":
                            x_pos = 50
                        elif horizontal_position == "Center":
                            x_pos = (page_width - image_width) / 2
                        else:  # Right
                            x_pos = page_width - image_width - 50
                        
                        # Vertical position
                        if vertical_position == "Top":
                            y_pos = page_height - image_height - 50
                        elif vertical_position == "Middle":
                            y_pos = (page_height - image_height) / 2
                        else:  # Bottom
                            y_pos = 50
                        
                        # Apply offsets
                        x_pos += x_offset
                        y_pos += y_offset
                        img_width = image_width
                        img_height = image_height
                    
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
                        
                        # Only add image to selected pages
                        if i in pages_to_process:
                            # Create image layer
                            packet = BytesIO()
                            can = canvas.Canvas(packet, pagesize=letter)
                            
                            # Draw image with transparency
                            can.drawImage(tmp_img_path, x_pos, y_pos,
                                        width=img_width, height=img_height,
                                        mask='auto')
                            can.save()
                            packet.seek(0)
                            
                            # Merge based on layer mode
                            image_layer = PdfReader(packet)
                            
                            if is_background:
                                # Place image behind: merge original page onto image layer
                                image_page = image_layer.pages[0]
                                image_page.merge_page(page)
                                writer.add_page(image_page)
                            else:
                                # Place image on top: merge image layer onto original page
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
                    
                    # Success message and download button
                    st.success("✅ PDF generated successfully!")
                    
                    st.download_button(
                        label="⬇️ Download Signed PDF",
                        data=output,
                        file_name="signed_document.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    st.exception(e)
    
    else:
        st.info("👆 Please upload both a PDF file and an image to get started")

# TAB 2: Image to PDF Converter
with tab2:
    st.markdown("Convert your images to A4-sized PDF documents")
    
    st.subheader("🖼️ Upload Images")
    uploaded_images = st.file_uploader(
        "Choose image file(s)", 
        type=['png', 'jpg', 'jpeg', 'bmp', 'gif'],
        accept_multiple_files=True,
        key="converter_images"
    )
    
    if uploaded_images:
        st.success(f"✅ {len(uploaded_images)} image(s) uploaded successfully!")
        
        # Show image previews
        st.subheader("📸 Image Preview")
        cols = st.columns(min(4, len(uploaded_images)))
        for idx, img_file in enumerate(uploaded_images[:4]):
            with cols[idx % 4]:
                img = Image.open(img_file)
                st.image(img, caption=img_file.name, use_container_width=True)
        
        if len(uploaded_images) > 4:
            st.info(f"... and {len(uploaded_images) - 4} more image(s)")
        
        st.markdown("---")
        
        # Conversion settings
        st.subheader("⚙️ Conversion Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fit_mode = st.radio(
                "Image Fit Mode:",
                ["Fit to page (maintain aspect ratio)", "Fill page (may crop)", "Stretch to fill"],
                key="fit_mode",
                help="Choose how images should be fitted to the A4 page"
            )
            
            orientation = st.radio(
                "Page Orientation:",
                ["Portrait", "Landscape"],
                key="orientation"
            )
        
        with col2:
            margin = st.slider(
                "Page Margin (mm)",
                0, 50, 10, 5,
                key="margin",
                help="Add margin around the image"
            )
            
            combine_mode = st.radio(
                "PDF Output:",
                ["One PDF with all images", "Separate PDF for each image"],
                key="combine_mode"
            )
        
        st.markdown("---")
        
        # Convert button
        if st.button("🔄 Convert to PDF", type="primary", use_container_width=True, key="convert_btn"):
            with st.spinner("Converting images to PDF..."):
                try:
                    # Set page size based on orientation
                    if orientation == "Portrait":
                        page_size = A4  # 595.27 x 841.89 points
                    else:
                        page_size = (A4[1], A4[0])  # Landscape
                    
                    page_width, page_height = page_size
                    
                    # Convert mm to points (1 mm = 2.83465 points)
                    margin_points = margin * 2.83465
                    
                    # Available space for image
                    available_width = page_width - (2 * margin_points)
                    available_height = page_height - (2 * margin_points)
                    
                    if combine_mode == "One PDF with all images":
                        # Create single PDF with all images
                        packet = BytesIO()
                        can = canvas.Canvas(packet, pagesize=page_size)
                        
                        for img_file in uploaded_images:
                            img_file.seek(0)
                            img = Image.open(img_file)
                            
                            # Convert to RGB if necessary
                            if img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img = img.convert('RGBA')
                                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                                img = background
                            elif img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Calculate image dimensions
                            img_width, img_height = img.size
                            aspect_ratio = img_width / img_height
                            
                            if fit_mode == "Fit to page (maintain aspect ratio)":
                                # Scale to fit within available space
                                if available_width / available_height > aspect_ratio:
                                    # Height is the limiting factor
                                    new_height = available_height
                                    new_width = new_height * aspect_ratio
                                else:
                                    # Width is the limiting factor
                                    new_width = available_width
                                    new_height = new_width / aspect_ratio
                                
                                # Center the image
                                x_pos = margin_points + (available_width - new_width) / 2
                                y_pos = margin_points + (available_height - new_height) / 2
                                
                            elif fit_mode == "Fill page (may crop)":
                                # Scale to fill available space (may crop)
                                if available_width / available_height < aspect_ratio:
                                    # Height fills the space
                                    new_height = available_height
                                    new_width = new_height * aspect_ratio
                                else:
                                    # Width fills the space
                                    new_width = available_width
                                    new_height = new_width / aspect_ratio
                                
                                # Center the image
                                x_pos = margin_points + (available_width - new_width) / 2
                                y_pos = margin_points + (available_height - new_height) / 2
                                
                            else:  # Stretch to fill
                                new_width = available_width
                                new_height = available_height
                                x_pos = margin_points
                                y_pos = margin_points
                            
                            # Save image temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
                                img.save(tmp_img.name, 'JPEG', quality=95)
                                tmp_img_path = tmp_img.name
                            
                            # Draw image on canvas
                            can.drawImage(tmp_img_path, x_pos, y_pos, 
                                        width=new_width, height=new_height)
                            can.showPage()
                            
                            # Clean up temp file
                            os.unlink(tmp_img_path)
                        
                        can.save()
                        packet.seek(0)
                        
                        st.success("✅ PDF created successfully!")
                        
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=packet,
                            file_name="converted_images.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                    
                    else:  # Separate PDF for each image
                        st.success(f"✅ {len(uploaded_images)} PDF(s) created successfully!")
                        
                        cols = st.columns(2)
                        for idx, img_file in enumerate(uploaded_images):
                            img_file.seek(0)
                            img = Image.open(img_file)
                            
                            # Convert to RGB if necessary
                            if img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img = img.convert('RGBA')
                                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                                img = background
                            elif img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Create individual PDF
                            packet = BytesIO()
                            can = canvas.Canvas(packet, pagesize=page_size)
                            
                            # Calculate image dimensions
                            img_width, img_height = img.size
                            aspect_ratio = img_width / img_height
                            
                            if fit_mode == "Fit to page (maintain aspect ratio)":
                                if available_width / available_height > aspect_ratio:
                                    new_height = available_height
                                    new_width = new_height * aspect_ratio
                                else:
                                    new_width = available_width
                                    new_height = new_width / aspect_ratio
                                x_pos = margin_points + (available_width - new_width) / 2
                                y_pos = margin_points + (available_height - new_height) / 2
                            elif fit_mode == "Fill page (may crop)":
                                if available_width / available_height < aspect_ratio:
                                    new_height = available_height
                                    new_width = new_height * aspect_ratio
                                else:
                                    new_width = available_width
                                    new_height = new_width / aspect_ratio
                                x_pos = margin_points + (available_width - new_width) / 2
                                y_pos = margin_points + (available_height - new_height) / 2
                            else:  # Stretch to fill
                                new_width = available_width
                                new_height = available_height
                                x_pos = margin_points
                                y_pos = margin_points
                            
                            # Save image temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
                                img.save(tmp_img.name, 'JPEG', quality=95)
                                tmp_img_path = tmp_img.name
                            
                            # Draw image on canvas
                            can.drawImage(tmp_img_path, x_pos, y_pos,
                                        width=new_width, height=new_height)
                            can.save()
                            packet.seek(0)
                            
                            # Clean up temp file
                            os.unlink(tmp_img_path)
                            
                            # Add download button
                            with cols[idx % 2]:
                                original_name = os.path.splitext(img_file.name)[0]
                                st.download_button(
                                    label=f"⬇️ {img_file.name}",
                                    data=packet,
                                    file_name=f"{original_name}.pdf",
                                    mime="application/pdf",
                                    key=f"download_{idx}"
                                )
                
                except Exception as e:
                    st.error(f"❌ Error converting images: {str(e)}")
                    st.exception(e)
    
    else:
        st.info("👆 Please upload one or more images to convert to PDF")

# TAB 3: PDF Merger
with tab3:
    st.markdown("Merge multiple PDF files into a single document")
    
    st.subheader("📁 Upload PDF Files")
    uploaded_pdfs = st.file_uploader(
        "Choose PDF file(s) to merge", 
        type=['pdf'],
        accept_multiple_files=True,
        key="merger_pdfs"
    )
    
    if uploaded_pdfs:
        st.success(f"✅ {len(uploaded_pdfs)} PDF file(s) uploaded successfully!")
        
        # Display PDF information
        st.subheader("📋 Uploaded PDFs")
        
        pdf_info = []
        total_pages = 0
        
        for idx, pdf_file in enumerate(uploaded_pdfs):
            pdf_file.seek(0)
            reader = PdfReader(pdf_file)
            num_pages = len(reader.pages)
            total_pages += num_pages
            pdf_info.append({
                "Order": idx + 1,
                "Filename": pdf_file.name,
                "Pages": num_pages
            })
        
        # Display as a table
        import pandas as pd
        df = pd.DataFrame(pdf_info)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.info(f"📊 Total pages in merged PDF: **{total_pages}** pages")
        
        st.markdown("---")
        
        # Merge options
        st.subheader("⚙️ Merge Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            merge_order = st.radio(
                "Merge Order:",
                ["As uploaded", "Sort by filename (A-Z)", "Sort by filename (Z-A)"],
                key="merge_order",
                help="Choose the order in which PDFs will be merged"
            )
        
        with col2:
            add_bookmarks = st.checkbox(
                "Add bookmarks for each PDF",
                value=True,
                key="add_bookmarks",
                help="Add a bookmark for each merged PDF for easy navigation"
            )
        
        # Option to reorder manually
        if merge_order == "As uploaded":
            st.info("💡 Tip: You can reorder files by re-uploading them in your desired order")
        
        st.markdown("---")
        
        # Merge button
        if st.button("🔗 Merge PDFs", type="primary", use_container_width=True, key="merge_btn"):
            with st.spinner("Merging PDF files..."):
                try:
                    # Sort PDFs if needed
                    pdfs_to_merge = uploaded_pdfs.copy()
                    
                    if merge_order == "Sort by filename (A-Z)":
                        pdfs_to_merge = sorted(pdfs_to_merge, key=lambda x: x.name)
                    elif merge_order == "Sort by filename (Z-A)":
                        pdfs_to_merge = sorted(pdfs_to_merge, key=lambda x: x.name, reverse=True)
                    
                    # Create PDF writer
                    writer = PdfWriter()
                    
                    # Merge PDFs
                    for pdf_file in pdfs_to_merge:
                        pdf_file.seek(0)
                        reader = PdfReader(pdf_file)
                        
                        # Track starting page for bookmark
                        start_page = len(writer.pages)
                        
                        # Add all pages from this PDF
                        for page in reader.pages:
                            writer.add_page(page)
                        
                        # Add bookmark if option is enabled
                        if add_bookmarks:
                            writer.add_outline_item(
                                title=pdf_file.name,
                                page_number=start_page
                            )
                    
                    # Create output PDF
                    output = BytesIO()
                    writer.write(output)
                    output.seek(0)
                    
                    # Success message and download button
                    st.success(f"✅ Successfully merged {len(pdfs_to_merge)} PDF files!")
                    
                    st.download_button(
                        label="⬇️ Download Merged PDF",
                        data=output,
                        file_name="merged_document.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Show merge summary
                    st.info(f"📄 Merged PDF contains {total_pages} pages from {len(pdfs_to_merge)} documents")
                    
                except Exception as e:
                    st.error(f"❌ Error merging PDFs: {str(e)}")
                    st.exception(e)
    
    else:
        st.info("👆 Please upload two or more PDF files to merge")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>💡 Overlay Tool: Use PNG images with transparent backgrounds for best results</p>
    <p>🎨 Background mode places the image behind text, Overlay mode places it on top</p>
    <p>👁️ Preview shows approximate position - adjust settings and preview updates automatically</p>
    <p>📄 Image Converter: Supports multiple images and A4 format (210 × 297 mm)</p>
    <p>🔗 PDF Merger: Combine multiple PDFs with optional bookmarks for easy navigation</p>
</div>
""", unsafe_allow_html=True)