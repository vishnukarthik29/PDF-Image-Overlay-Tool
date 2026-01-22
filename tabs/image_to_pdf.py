# tabs/image_to_pdf.py
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from PIL import Image
import tempfile
import os

def render():
    """Render the Image to PDF Converter tab"""
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
                        page_size = A4
                    else:
                        page_size = (A4[1], A4[0])
                    
                    page_width, page_height = page_size
                    margin_points = margin * 2.83465  # mm to points
                    
                    available_width = page_width - (2 * margin_points)
                    available_height = page_height - (2 * margin_points)
                    
                    if combine_mode == "One PDF with all images":
                        output = create_combined_pdf(uploaded_images, page_size, fit_mode, 
                                                    available_width, available_height, margin_points)
                        
                        st.success("✅ PDF created successfully!")
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=output,
                            file_name="converted_images.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        create_separate_pdfs(uploaded_images, page_size, fit_mode,
                                           available_width, available_height, margin_points)
                
                except Exception as e:
                    st.error(f"❌ Error converting images: {str(e)}")
                    st.exception(e)
    
    else:
        st.info("👆 Please upload one or more images to convert to PDF")


def create_combined_pdf(uploaded_images, page_size, fit_mode, available_width, available_height, margin_points):
    """Create a single PDF with all images"""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)
    
    for img_file in uploaded_images:
        img_file.seek(0)
        img = Image.open(img_file)
        img = convert_to_rgb(img)
        
        x_pos, y_pos, new_width, new_height = calculate_image_dimensions(
            img, fit_mode, available_width, available_height, margin_points
        )
        
        # Save and draw image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
            img.save(tmp_img.name, 'JPEG', quality=95)
            tmp_img_path = tmp_img.name
        
        can.drawImage(tmp_img_path, x_pos, y_pos, width=new_width, height=new_height)
        can.showPage()
        
        os.unlink(tmp_img_path)
    
    can.save()
    packet.seek(0)
    return packet


def create_separate_pdfs(uploaded_images, page_size, fit_mode, available_width, available_height, margin_points):
    """Create separate PDF for each image"""
    st.success(f"✅ {len(uploaded_images)} PDF(s) created successfully!")
    
    cols = st.columns(2)
    for idx, img_file in enumerate(uploaded_images):
        img_file.seek(0)
        img = Image.open(img_file)
        img = convert_to_rgb(img)
        
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=page_size)
        
        x_pos, y_pos, new_width, new_height = calculate_image_dimensions(
            img, fit_mode, available_width, available_height, margin_points
        )
        
        # Save and draw image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
            img.save(tmp_img.name, 'JPEG', quality=95)
            tmp_img_path = tmp_img.name
        
        can.drawImage(tmp_img_path, x_pos, y_pos, width=new_width, height=new_height)
        can.save()
        packet.seek(0)
        
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


def convert_to_rgb(img):
    """Convert image to RGB format"""
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        return background
    elif img.mode != 'RGB':
        return img.convert('RGB')
    return img


def calculate_image_dimensions(img, fit_mode, available_width, available_height, margin_points):
    """Calculate image dimensions and position based on fit mode"""
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
    
    return x_pos, y_pos, new_width, new_height