import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="PDF Image Overlay", page_icon="📄", layout="wide")

st.title("📄 PDF Image Overlay Tool")
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
    
    # Generate button
    if st.button("🎨 Generate PDF", type="primary", use_container_width=True):
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>💡 Tip: Use PNG images with transparent backgrounds for best results</p>
    <p>🎨 Background mode places the image behind text, Overlay mode places it on top</p>
</div>
""", unsafe_allow_html=True)