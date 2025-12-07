# Manga Translator

An automated pipeline for translating Japanese manga and comics into English. This tool detects Japanese text in images, removes it cleanly, translates it to English, and renders the translation back onto the image. Now featuring a modern GUI interface for interactive editing.

## Overview

This project implements a multi-modal processing pipeline that combines:
- Optical Character Recognition (OCR) for Japanese text
- Image inpainting for text removal
- Machine translation (Japanese to English)
- Text rendering and placement
- **NEW**: Interactive GUI editor for manual adjustments

## Features

- Automatic Japanese text detection and extraction
- Clean text removal using inpainting
- Translation to natural English
- Smart text placement that fits within original speech bubbles
- Support for both horizontal and vertical text layouts
- Batch processing capabilities
- **NEW**: Interactive GUI editor with:
  - Real-time text bounding box editing
  - Font family and size customization
  - Text color and alignment controls
  - Drag-and-drop text positioning
  - Live preview of translations
  - Export to various image formats

## GUI Features

### Interactive Editor
- **Image Display**: High-quality image viewing with zoom and pan
- **Bounding Box Editing**: Click and drag to adjust text regions
- **Text Editing**: Edit translations directly in the interface
- **Typesetting Controls**: 
  - Font family selection (includes manga-style fonts)
  - Adjustable font sizes
  - Text alignment (Left, Center, Right)
  - Custom text colors
- **Real-time Preview**: See changes immediately as you edit
- **Export Options**: Save final images in PNG or JPEG format

### Performance Optimizations
- **Memory Management**: Efficient handling of large images
- **Lazy Loading**: Components load only when needed
- **Caching System**: Improved rendering performance
- **Progress Monitoring**: Real-time translation progress with timing
- **Resource Optimization**: Memory usage tracking and cleanup

## Requirements

### System Requirements
- Python 3.8 or higher
- 4GB+ RAM (8GB recommended for GUI)
- GPU recommended but not required (CPU processing is slower)

### Dependencies
- Python 3.8+
- Pillow (PIL)
- numpy
- opencv-python
- torch (for GPU support in EasyOCR and iopaint)
- manga-ocr
- easyocr
- pyphen
- googletrans
- iopaint (Requires separate installation if not using pip package)
- **GUI Dependencies**:
  - PySide6 (for the GUI interface)
  - psutil (for performance monitoring)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/manga-translator.git
cd manga-translator
```

### 2. Create virtual environment
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install GUI dependencies (optional but recommended)
```bash
pip install PySide6 psutil
```

### 5. Configure translation
The pipeline currently uses `googletrans` for translation, which requires no API key setup.

## Usage

### Command Line Interface

#### Basic Usage
```bash
python main.py path/to/manga_page.jpg
```
The output file (`manga_page_translated.jpg`) will be saved in the `output/` directory.

### Graphical User Interface (GUI)

#### Launching the GUI
```bash
python gui/main_window.py
```

#### GUI Workflow

1. **Load Image**
   - Click "Upload Image" or use File → Open Image
   - Supported formats: PNG, JPG, JPEG, BMP, TIFF

2. **Run Translation**
   - Click "Translate (TL)" button
   - Monitor progress in the status bar
   - Translation runs in background thread

3. **Edit Translations**
   - Click on any green bounding box to select it
   - Edit text in the "Text Editor" dock panel
   - Adjust fonts, colors, and alignment in "Typesetting" panel
   - Drag bounding boxes to reposition text

4. **Save Result**
   - Click "Save Final Image" or use File → Save Image
   - Choose format (PNG or JPEG)
   - Image saved with all edits applied

#### GUI Controls

**File Operations**
- Upload Image (Ctrl+O)
- Save Image (Ctrl+S)
- Exit (Ctrl+Q)

**Translation**
- Translate (TL) - Run the translation pipeline
- Progress bar shows current status

**Text Editing**
- Select text regions by clicking bounding boxes
- Edit text directly in the text editor panel
- Adjust font properties in the typesetting panel

**View Controls**
- Zoom In (Ctrl++) / Zoom Out (Ctrl+-)
- Fit to Window
- Mouse wheel + Ctrl for precise zooming

**Canvas Interaction**
- Click: Select text region
- Drag: Move selected bounding box
- Delete key: Remove selected region
- Escape: Deselect all regions

#### GUI Panels

**Text Editor Panel**
- Shows translated text for selected region
- Real-time editing with immediate preview
- Appears automatically when a region is selected

**Typesetting Panel**
- Font Family: Dropdown with available fonts
- Font Size: Spin box (8-200px)
- Text Color: Color picker button
- Alignment: Left, Center, Right options

**Status Bar**
- Current status message
- Mouse coordinates
- Zoom level indicator

### Advanced Usage

#### Performance Monitoring
The GUI includes built-in performance monitoring:
- Real-time memory usage tracking
- CPU utilization monitoring
- Step-by-step timing information
- Performance metrics in worker thread

#### Optimized Components
For better performance with large images:
- Use `gui/optimized_editor_canvas.py` for memory-efficient rendering
- Use `gui/optimized_translation_worker.py` for detailed progress monitoring

## Project Structure

```
manga-translator/
├── main.py                     # Main CLI pipeline script
├── gui/
│   ├── main_window.py         # Main GUI application window
│   ├── editor_canvas.py       # Image display and editing canvas
│   ├── translation_worker.py  # Background translation thread
│   ├── optimized_editor_canvas.py    # Performance-optimized canvas
│   └── optimized_translation_worker.py # Performance-optimized worker
├── ocr_module.py              # Text detection and extraction
├── inpainting_module.py       # Text removal
├── translation_module.py      # Text translation
├── text_renderer.py           # English text placement
├── requirements.txt           # Python dependencies
├── fonts/                     # Font files for text rendering
├── data/                      # Sample data and dictionaries
├── test_*.py                  # Test scripts
└── output/                    # Translated images folder
```

## How It Works

### Pipeline Steps

1. **Text Detection (OCR)**
   - Detects Japanese text regions using EasyOCR
   - Extracts text content using manga-ocr
   - Saves bounding box coordinates for each text block

2. **Text Removal (Inpainting)**
   - Creates masks for detected text regions
   - Uses inpainting to fill in removed text areas
   - Preserves background artwork and details

3. **Translation**
   - Translates extracted Japanese text to English
   - Uses DeepL/Google API or local models
   - Preserves context and natural phrasing

4. **Text Rendering**
   - Calculates appropriate font size for each text block
   - Wraps text to fit within original boundaries
   - Renders English text with readable formatting

5. **GUI Editing (Optional)**
   - Interactive bounding box adjustment
   - Manual text editing and typesetting
   - Real-time preview of changes

## Testing

### Run Integration Tests
```bash
# Test basic GUI integration
python test_gui_simple.py

# Test complete workflow
python test_workflow_focused.py

# Test optimized components
python test_optimized_components.py
```

### Test Coverage
- Import resolution testing
- Core pipeline integration
- GUI component functionality
- Performance optimization features
- File operations and error handling

## Limitations

- Best results with clear, printed text
- May struggle with highly stylized or handwritten fonts
- Vertical text handling is basic in current version
- Translation quality depends on chosen method
- Inpainting may produce artifacts on complex backgrounds
- GUI requires additional dependencies (PySide6)

## GUI Troubleshooting

### Common GUI Issues

**"ImportError: No module named 'PySide6'"**
- Solution: Install GUI dependencies
```bash
pip install PySide6 psutil
```

**GUI window doesn't appear**
- Check that PySide6 is properly installed
- Ensure you have a display available (for Linux)
- Try running from command line to see error messages

**Slow performance with large images**
- Use optimized components: `optimized_editor_canvas.py`
- Enable memory optimization features
- Consider resizing very large images before processing

**Translation worker stops responding**
- Check system memory usage
- Try with a smaller test image
- Monitor progress in status bar

**Text editing not working**
- Ensure a text region is selected (green bounding box)
- Check that translation has completed successfully
- Verify text editor panel is visible

### Performance Tips

**For Large Images:**
- Enable image caching in optimized canvas
- Use lazy loading for bounding boxes
- Monitor memory usage with performance tools

**For Better Responsiveness:**
- Translation runs in background thread
- Use batched updates for multiple changes
- Clear cache periodically to free memory

## Known Issues

- Text overlapping image borders may be cut off
- Very long translations might not fit in small speech bubbles
- Background patterns may not perfectly match after inpainting
- Text renderer uses the smallest font size for vertical text boxes
- GUI performance may degrade with very large images (>10MB)

## Performance

### Processing Times
**CLI Version:**
- Single manga page: 10-30 seconds (with GPU)
- Single manga page: 30-90 seconds (CPU only)

**GUI Version:**
- Similar processing times for translation
- Additional time for GUI rendering and interaction
- Real-time preview may slow down with many text regions

### Factors Affecting Speed
- Image resolution
- Amount of text
- Translation method (API vs local)
- Hardware specifications
- GUI interaction complexity

### Memory Usage
- GUI version: ~200-500MB typical usage
- Large images: May require up to 1GB
- Optimized components: 20-30% less memory usage

## Future Improvements

- Web interface for easier usage
- Batch processing with progress tracking
- Better vertical text support
- Custom font selection per text block
- Support for more languages
- OCR model fine-tuning on specific manga styles
- Cloud-based processing options
- Mobile app interface

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install PySide6 psutil

# Run tests
python test_gui_simple.py
python test_workflow_focused.py

# Launch GUI for testing
python gui/main_window.py
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- manga-ocr for Japanese OCR capabilities
- EasyOCR for text detection
- googletrans for translation
- iopaint (LaMa model) for inpainting
- PySide6 for the GUI framework
- The open-source community

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Note:** This is an educational project. Please respect copyright laws when using this tool with commercial manga content.

## Changelog

### Version 2.0 (Current)
- Added interactive GUI editor
- Implemented performance optimizations
- Enhanced error handling and progress reporting
- Added comprehensive testing suite
- Improved memory management for large images

### Version 1.0
- Initial release with CLI interface
- Basic OCR, translation, and inpainting pipeline
- Command-line only interface
