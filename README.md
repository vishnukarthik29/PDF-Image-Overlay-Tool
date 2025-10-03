# 📄 PDF Image Overlay Tool

A user-friendly Streamlit application that allows you to add signatures, stamps, or any image overlay to your PDF documents with precise positioning control.

## ✨ Features

- **Easy File Upload**: Upload PDF documents and images (PNG, JPG, JPEG)
- **Flexible Page Selection**: 
  - Apply to all pages
  - First page only
  - Last page only
  - Custom page range (e.g., 1,3,5 or 1-3)
- **Precise Positioning**:
  - 9 preset positions (Top/Middle/Bottom × Left/Center/Right)
  - Fine-tune with horizontal and vertical offset controls
- **Image Customization**:
  - Adjustable width and height
  - Transparency support for PNG images
- **Live Preview**: See your uploaded image before processing
- **Instant Download**: Generate and download your signed PDF with one click

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

### Running the Application

1. Start the Streamlit server:
```bash
streamlit run app.py
```

2. Your default web browser will automatically open to `http://localhost:8501`

3. If it doesn't open automatically, navigate to the URL shown in your terminal

## 📖 How to Use

1. **Upload Files**:
   - Click "Choose a PDF file" to upload your document
   - Click "Choose an image" to upload your signature/stamp

2. **Configure Position**:
   - Select which pages to apply the image to
   - Choose horizontal position (Left/Center/Right)
   - Choose vertical position (Top/Middle/Bottom)
   - Adjust image size using the sliders
   - Fine-tune position with offset controls

3. **Generate PDF**:
   - Click the "Generate PDF" button
   - Wait for processing to complete
   - Click "Download Signed PDF" to save your file

## 💡 Tips

- **Use PNG images** with transparent backgrounds for best results
- **Test with offsets** to perfectly align your signature
- **Preview mode**: The app shows your image preview before processing
- **Page ranges**: Use format like "1,3,5" for specific pages or "1-3" for ranges

## 🛠️ Technology Stack

- **Streamlit**: Web application framework
- **PyPDF2**: PDF manipulation
- **ReportLab**: PDF generation and overlay
- **Pillow**: Image processing

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

**Issue**: Invalid page range error
- **Solution**: Use correct format: "1,3,5" or "1-3" (page numbers start from 1)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

## 🔄 Version History

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
- [ ] Opacity control for images
- [ ] Support for more image formats

---

Made with ❤️ using Streamlit