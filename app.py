# app.py
import streamlit as st
from tabs import pdf_overlay, image_to_pdf, pdf_merger

st.set_page_config(page_title="PDF Tools", page_icon="📄", layout="wide")
st.title("📄 PDF Tools Suite")

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["📝 PDF Image Overlay", "🖼️ Image to PDF Converter", "🔗 PDF Merger"])

# Load each tab from separate modules
with tab1:
    pdf_overlay.render()

with tab2:
    image_to_pdf.render()

with tab3:
    pdf_merger.render()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    💡 Overlay Tool: Use PNG images with transparent backgrounds for best results<br>
    🎨 Background mode places the image behind text, Overlay mode places it on top<br>
    👁️ Preview shows approximate position - adjust settings and preview updates automatically<br>
    📄 Image Converter: Supports multiple images and A4 format (210 × 297 mm)<br>
    🔗 PDF Merger: Combine multiple PDFs with optional bookmarks for easy navigation
</div>
""", unsafe_allow_html=True)