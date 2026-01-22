# tabs/pdf_merger.py
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import pandas as pd

def render():
    """Render the PDF Merger tab"""
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
                    output = merge_pdfs(uploaded_pdfs, merge_order, add_bookmarks)
                    
                    # Success message and download button
                    st.success(f"✅ Successfully merged {len(uploaded_pdfs)} PDF files!")
                    st.download_button(
                        label="⬇️ Download Merged PDF",
                        data=output,
                        file_name="merged_document.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Show merge summary
                    st.info(f"📄 Merged PDF contains {total_pages} pages from {len(uploaded_pdfs)} documents")
                
                except Exception as e:
                    st.error(f"❌ Error merging PDFs: {str(e)}")
                    st.exception(e)
    
    else:
        st.info("👆 Please upload two or more PDF files to merge")


def merge_pdfs(uploaded_pdfs, merge_order, add_bookmarks):
    """Merge multiple PDFs into one"""
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
    
    return output