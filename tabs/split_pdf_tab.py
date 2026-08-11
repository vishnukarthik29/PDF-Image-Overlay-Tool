"""
Split PDF Tab
--------------
Drop-in tab module for the PDF-Image-Overlay-Tool Streamlit app.

Save this file as tabs/split_pdf_tab.py (same folder as your other tab
modules like pdf_merger.py), then in app.py:

    from tabs import split_pdf_tab

    tab1, tab2, tab3, tab4 = st.tabs([
        "PDF Image Overlay",
        "Image to PDF Converter",
        "PDF Merger",
        "Split PDF",
    ])

    with tab4:
        split_pdf_tab.render()
"""

import io
import zipfile

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter


def render():
    st.header("✂️ Split PDF")
    st.write("Split a PDF into smaller files, grouped by a fixed number of pages, and download them all as a ZIP.")

    uploaded_pdf = st.file_uploader("Upload PDF to split", type=["pdf"], key="split_pdf_uploader")

    if uploaded_pdf is None:
        st.info("Upload a PDF to get started.")
        return

    reader = PdfReader(uploaded_pdf)
    total_pages = len(reader.pages)
    st.success(f"Loaded **{uploaded_pdf.name}** — {total_pages} page(s).")

    split_mode = st.radio(
        "Split mode",
        ["Every N pages", "Custom page ranges", "Every page (1 file per page)"],
        horizontal=True,
    )

    file_groups = []  # list of (label, [page_indices])

    if split_mode == "Every N pages":
        pages_per_split = st.number_input(
            "Pages per split file",
            min_value=1,
            max_value=total_pages,
            value=min(2, total_pages),
            step=1,
        )
        for start in range(0, total_pages, pages_per_split):
            end = min(start + pages_per_split, total_pages)
            label = f"pages_{start + 1}-{end}"
            file_groups.append((label, list(range(start, end))))

    elif split_mode == "Custom page ranges":
        st.caption('Enter one range per line, e.g. "1-2", "3-4", "5" (1-indexed, inclusive).')
        ranges_text = st.text_area(
            "Page ranges",
            value="1-2\n3-4" if total_pages >= 4 else f"1-{total_pages}",
            height=120,
        )
        parse_error = None
        for line in ranges_text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                if "-" in line:
                    start_str, end_str = line.split("-", 1)
                    start_p, end_p = int(start_str), int(end_str)
                else:
                    start_p = end_p = int(line)

                if start_p < 1 or end_p > total_pages or start_p > end_p:
                    raise ValueError

                label = f"pages_{start_p}-{end_p}" if start_p != end_p else f"page_{start_p}"
                file_groups.append((label, list(range(start_p - 1, end_p))))
            except ValueError:
                parse_error = f"Invalid range: '{line}'"
                break

        if parse_error:
            st.error(parse_error + f" — page numbers must be between 1 and {total_pages}.")
            return

    else:  # Every page
        for i in range(total_pages):
            file_groups.append((f"page_{i + 1}", [i]))

    if not file_groups:
        st.warning("No valid page groups to split.")
        return

    st.write(f"This will produce **{len(file_groups)}** file(s):")
    st.write(", ".join(label for label, _ in file_groups))

    if st.button("Split & Prepare ZIP", type="primary"):
        with st.spinner("Splitting PDF..."):
            zip_buffer = io.BytesIO()
            base_name = uploaded_pdf.name.rsplit(".", 1)[0]

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for label, page_indices in file_groups:
                    writer = PdfWriter()
                    for idx in page_indices:
                        writer.add_page(reader.pages[idx])

                    pdf_bytes = io.BytesIO()
                    writer.write(pdf_bytes)
                    pdf_bytes.seek(0)

                    zf.writestr(f"{base_name}_{label}.pdf", pdf_bytes.read())

            zip_buffer.seek(0)

        st.success(f"Done! {len(file_groups)} file(s) ready.")
        st.download_button(
            label="⬇️ Download ZIP",
            data=zip_buffer,
            file_name=f"{base_name}_split.zip",
            mime="application/zip",
        )
