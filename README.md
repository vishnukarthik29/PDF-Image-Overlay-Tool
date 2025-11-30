# 📄 PDF Overlay Tools Suite

A comprehensive Streamlit application that provides three powerful PDF tools in one interface: image overlay/watermarking, image-to-PDF conversion, and PDF merging capabilities.

## ✨ Features

### 🎨 Tab 1: PDF Image Overlay

Add signatures, stamps, watermarks, or any image to your PDF documents with precise control.

- **Dual Layer Modes**:
  - **Overlay Mode**: Place images on top of PDF content (signatures, stamps)
  - **Background Mode**: Add full-page backgrounds behind PDF content (watermarks, letterheads)
- **Flexible Page Selection**: All pages, first/last only, or custom ranges
- **Precise Positioning** (Overlay Mode):
  - 9 preset positions with fine-tune offset controls
  - Adjustable width and height
- **Full-Page Background** (Background Mode): Automatic scaling for watermarks
- **Transparency Support**: Seamless PNG transparency handling

### 🖼️ Tab 2: Image to PDF Converter

Convert single or multiple images into professional A4-sized PDF documents.

- **Batch Processing**: Convert multiple images at once
- **Multiple Fit Modes**:
  - Fit to page (maintain aspect ratio)
  - Fill page (may crop)
  - Stretch to fill
- **Flexible Orientation**: Portrait or landscape
- **Customizable Margins**: 0-50mm adjustable margins
- **Output Options**:
  - Single PDF with all images
  - Separate PDF for each image
- **Format Support**: PNG, JPG, JPEG, BMP, GIF

### 🔗 Tab 3: PDF Merger

Combine multiple PDF files into a single organized document.

- **Batch Merging**: Merge unlimited PDF files
- **Flexible Ordering**:
  - As uploaded
  - Sort by filename (A-Z or Z-A)
- **Bookmark Creation**: Automatic bookmarks for easy navigation
- **Document Overview**: Preview page counts before merging
- **Large File Support**: Handle PDFs of any size

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone this repository:

```bash
git clone https://github.com/vishnukarthik29/PDF-Image-Overlay-Tool.git
cd PDF-Image-Overlay-Tool
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

### Required Dependencies

Create a `requirements.txt` file with:

```
streamlit>=1.28.0
PyPDF2>=3.0.0
reportlab>=4.0.0
Pillow>=10.0.0
pandas>=2.0.0
```

### Running the Application

1. Start the Streamlit server:

```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

## 📖 How to Use

### Tab 1: PDF Image Overlay

**Basic Workflow**:

1. Upload your PDF and image files
2. Choose layer mode (Overlay or Background)
3. Select which pages to modify
4. Configure position and size (Overlay mode)
5. Click "Generate PDF" and download

**Use Cases**:

- Adding signatures to contracts
- Applying approval stamps
- Creating watermarked documents
- Adding branded letterheads
- Date/time stamping

### Tab 2: Image to PDF Converter

**Basic Workflow**:

1. Upload one or more images
2. Select fit mode and orientation
3. Adjust margins if needed
4. Choose output format (combined or separate)
5. Click "Convert to PDF" and download

**Use Cases**:

- Scanning document replacement
- Photo portfolios
- Receipt archiving
- Creating presentation handouts
- Image batch conversion

### Tab 3: PDF Merger

**Basic Workflow**:

1. Upload multiple PDF files
2. Review the file list and total pages
3. Choose merge order
4. Enable bookmarks (recommended)
5. Click "Merge PDFs" and download

**Use Cases**:

- Combining multi-part documents
- Creating complete reports from sections
- Assembling invoice packages
- Merging scanned documents
- Creating comprehensive portfolios

## 💡 Tips & Best Practices

### For Image Overlay

- Use PNG images with transparency for professional overlays
- Test offset values to perfect signature positioning
- Background mode works great for semi-transparent watermarks
- Use page ranges like "1,3,5" or "1-3" for selective application

### For Image Conversion

- Higher resolution images produce better PDFs
- "Fit to page" maintains quality without distortion
- Use margins for better visual presentation
- Landscape orientation works well for wide images
- Batch convert to save time with multiple images

### For PDF Merging

- Add bookmarks for documents you'll navigate frequently
- Sort by filename for automatically organizing files
- Review the page count preview before merging
- Use descriptive filenames for better bookmark labels

## 🛠️ Technology Stack

- **Streamlit**: Modern web application framework
- **PyPDF2**: PDF manipulation and merging
- **ReportLab**: PDF generation and overlay creation
- **Pillow (PIL)**: Image processing and conversion
- **Pandas**: Data display and organization

## 📁 Project Structure

```
pdf-tools-suite/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## ⚠️ Troubleshooting

### Common Issues

**ModuleNotFoundError**

- Solution: Install dependencies with `pip install -r requirements.txt`

**Image not appearing in PDF**

- Check file integrity and try PNG format
- Verify correct layer mode selection

**Invalid page range error**

- Use format: "1,3,5" or "1-3"
- Ensure page numbers are within document range

**Image quality degradation**

- Upload higher resolution source images
- Adjust size settings appropriately

**PDF merge fails**

- Ensure all uploaded files are valid PDFs
- Check that PDFs aren't password-protected

**Conversion produces blank pages**

- Verify images aren't corrupted
- Try different fit mode settings

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 📧 Support

For issues or questions, please open an issue on GitHub.

## 🔄 Version History

- **v2.0.0** (2025): Multi-tool suite update

  - Added Image to PDF Converter
  - Added PDF Merger tool
  - Implemented tabbed interface
  - Enhanced user experience across all tools
  - Added batch processing capabilities

- **v1.1.0** (2025): Background mode update

  - Added background/overlay layer selection
  - Full-page background support
  - Dynamic UI improvements

- **v1.0.0** (2024): Initial release
  - Basic PDF overlay functionality
  - Position and size controls

## 🎯 Future Enhancements

### Overlay Tool

- [ ] Multiple image overlays per PDF
- [ ] Rotation and opacity controls
- [ ] Template saving/loading

### Converter Tool

- [ ] SVG and WebP support
- [ ] Quality presets (web, print, archive)
- [ ] Custom page sizes

### Merger Tool

- [ ] Page range selection from each PDF
- [ ] Drag-and-drop reordering
- [ ] PDF preview before merging

### General

- [ ] Batch processing across tools
- [ ] Password-protected PDF support
- [ ] Cloud storage integration
- [ ] Command-line interface option

## 🔐 Privacy & Security

- **Local Processing**: All operations happen locally
- **No Cloud Storage**: Files aren't uploaded externally
- **Temporary Files**: Automatically deleted after processing
- **No Data Collection**: Zero user data tracking
- **Session-Based**: Files cleared when session ends

## 📊 Performance Notes

- **Overlay Tool**: Processes ~1 second per page
- **Converter Tool**: ~2 seconds per image
- **Merger Tool**: ~0.5 seconds per PDF
- **File Size Limits**: Dependent on available RAM
- **Recommended**: Keep individual PDFs under 50MB for optimal performance

## 🌟 Acknowledgments

Built with modern Python libraries and Streamlit's powerful framework. Special thanks to the open-source community for the excellent tools that make this possible.

---

**Made with ❤️ using Streamlit** | Your complete PDF toolkit in one application
