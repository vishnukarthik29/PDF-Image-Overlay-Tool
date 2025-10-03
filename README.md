# 📄 PDF Image Overlay Tool

A user-friendly Streamlit application that allows you to add signatures, stamps, watermarks, or any image to your PDF documents with precise positioning control and flexible layering options.

## ✨ Features

- **Easy File Upload**: Upload PDF documents and images (PNG, JPG, JPEG)
- **Dual Layer Modes**:
  - **Overlay Mode**: Place images on top of PDF content (perfect for signatures and stamps)
  - **Background Mode**: Add full-page backgrounds behind PDF content (ideal for watermarks and letterheads)
- **Flexible Page Selection**: 
  - Apply to all pages
  - First page only
  - Last page only
  - Custom page range (e.g., 1,3,5 or 1-3)
- **Precise Positioning** (Overlay Mode):
  - 9 preset positions (Top/Middle/Bottom × Left/Center/Right)
  - Fine-tune with horizontal and vertical offset controls
  - Adjustable width and height
- **Full-Page Background** (Background Mode):
  - Automatic page-sized scaling
  - Perfect for watermarks and branded backgrounds
- **Transparency Support**: Works seamlessly with PNG images
- **Live Preview**: See your uploaded image before processing
- **Instant Download**: Generate and download your modified PDF with one click

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone this repository or download the files:
```bash
git clone <your-repository-url>
cd pdf-image-overlay
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Required Dependencies

Create a `requirements.txt` file with the following:
```
streamlit>=1.28.0
PyPDF2>=3.0.0
reportlab>=4.0.0
Pillow>=10.0.0
```

### Running the Application

1. Start the Streamlit server:
```bash
streamlit run app.py
```

2. Your default web browser will automatically open to `http://localhost:8501`

3. If it doesn't open automatically, navigate to the URL shown in your terminal

## 📖 How to Use

### Basic Workflow

1. **Upload Files**:
   - Click "Choose a PDF file" to upload your document
   - Click "Choose an image" to upload your signature/stamp/watermark

2. **Choose Layer Mode**:
   - **Overlay (on top)**: For signatures, stamps, or elements that should appear above content
   - **Background (behind)**: For watermarks, letterheads, or decorative backgrounds

3. **Configure Settings**:
   
   **For Overlay Mode**:
   - Select which pages to apply the image to
   - Choose horizontal position (Left/Center/Right)
   - Choose vertical position (Top/Middle/Bottom)
   - Adjust image size using the sliders
   - Fine-tune position with offset controls
   
   **For Background Mode**:
   - Select which pages to apply the background to
   - Image automatically fills the entire page

4. **Generate PDF**:
   - Click the "🎨 Generate PDF" button
   - Wait for processing to complete
   - Click "⬇️ Download Signed PDF" to save your file

### Use Cases

#### Overlay Mode Examples
- Adding signatures to contracts
- Applying approval stamps to invoices
- Placing logos in specific positions
- Adding date/time stamps

#### Background Mode Examples
- Adding watermarks to all pages
- Creating branded letterheads
- Applying confidentiality backgrounds
- Adding decorative page backgrounds

## 💡 Tips

- **Use PNG images** with transparent backgrounds for best overlay results
- **For backgrounds**: Semi-transparent PNGs work great as watermarks
- **Test with offsets**: Fine-tune your signature position perfectly in overlay mode
- **Preview mode**: Always check the image preview before processing
- **Page ranges**: Use format like "1,3,5" for specific pages or "1-3" for ranges
- **Background positioning**: Background mode ignores position settings and always fills the page

## 🛠️ Technology Stack

- **Streamlit**: Web application framework for the user interface
- **PyPDF2**: PDF reading and manipulation
- **ReportLab**: PDF generation and image overlay creation
- **Pillow (PIL)**: Image processing and format conversion

## 📁 Project Structure

```
pdf-image-overlay/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## ⚠️ Troubleshooting

### Common Issues

**Issue**: "ModuleNotFoundError"
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Image not appearing in PDF
- **Solution**: Check that your image file is not corrupted and try with a PNG file
- **Solution**: Verify the correct layer mode is selected (overlay vs background)

**Issue**: Invalid page range error
- **Solution**: Use correct format: "1,3,5" or "1-3" (page numbers start from 1)
- **Solution**: Ensure page numbers are within the document's page count

**Issue**: Background image not covering full page
- **Solution**: This should work automatically in background mode; if not, verify you selected "Background (behind)" mode

**Issue**: Image quality appears degraded
- **Solution**: Upload higher resolution images
- **Solution**: Adjust the width/height sliders in overlay mode for better sizing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

## 🔄 Version History

- **v1.1.0** (2025): Background mode update
  - Added background/overlay layer mode selection
  - Full-page background support
  - Automatic scaling for background images
  - Dynamic UI based on selected mode
  - Improved user guidance and tooltips

- **v1.0.0** (2024): Initial release
  - Basic PDF overlay functionality
  - Position and size controls
  - Multi-page support
  - Custom page range selection

## 🎯 Future Enhancements

- [ ] Multiple image overlays on single PDF
- [ ] Rotation control for images
- [ ] Batch processing for multiple PDFs
- [ ] Template saving/loading
- [ ] Opacity/transparency control for images
- [ ] Support for more image formats (SVG, WebP)
- [ ] Preview of final PDF before download
- [ ] Password-protected PDF support
- [ ] Custom page sizes beyond letter format
- [ ] Image positioning by coordinates

## 🔐 Privacy & Security

- **Local Processing**: All PDF processing happens locally in your browser/server
- **No Cloud Storage**: Files are not uploaded to any external servers
- **Temporary Files**: Image files are temporarily stored during processing and immediately deleted
- **No Data Collection**: This application does not collect or store any user data

---

Made with ❤️ using Streamlit | Perfect for signatures, stamps, and watermarks