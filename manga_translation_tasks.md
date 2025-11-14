# Manga Translation Project - MVP Task List

## Project Overview
Build a pipeline to: Extract Japanese text from manga/comic images → Remove text (inpainting) → Translate to English → Place translated text back

---

## Phase 1: Environment Setup

### Task 1.1: Install Python and Basic Tools **[Difficulty: 2/10]** [No dependencies]
- [x] 1.1.1: Verify Python 3.8+ is installed (`python --version`)
- [x] 1.1.2: Create project folder (e.g., `manga-translator`)
- [x] 1.1.3: Create virtual environment: `python -m venv venv`
- [x] 1.1.4: Activate virtual environment:
  - Windows: `venv\Scripts\activate`
  - Mac/Linux: `source venv/bin/activate`

### Task 1.2: Install Core Libraries **[Difficulty: 3/10]** [Depends on: 1.1]
- [x] 1.2.1: Install image processing: `pip install Pillow opencv-python`
- [x] 1.2.2: Install OCR: `pip install manga-ocr`
- [x] 1.2.3: Install ML framework: `pip install torch torchvision` (or CPU version if no GPU)
- [x] 1.2.4: Install utilities: `pip install numpy matplotlib`

### Task 1.3: Test Installation **[Difficulty: 2/10]** [Depends on: 1.2]
- [x] 1.3.1: Create `test_imports.py` and test all imports work
- [x] 1.3.2: Run test script successfully

---

## Phase 2: OCR (Text Detection & Extraction)

### Task 2.1: Basic OCR Setup **[Difficulty: 4/10]** [Depends on: 1.3]
- [x] 2.1.1: Create `ocr_module.py`
- [x] 2.1.2: Initialize manga-ocr model
- [x] 2.1.3: Write function to load test image
- [x] 2.1.4: Write function to extract text from image
 
### Task 2.2: Text Location Detection **[Difficulty: 6/10]** [Depends on: 2.1]
- [x] 2.2.1: Install EasyOCR for bounding boxes: `pip install easyocr`
- [x] 2.2.2: Write function to detect text regions (x, y, width, height)
- [x] 2.2.3: Save coordinates for each detected text block
- [x] 2.2.4: Visualize bounding boxes on test image
 
### Task 2.3: Test OCR Pipeline **[Difficulty: 3/10]** [Depends on: 2.2]
- [x] 2.3.1: Test with 2-3 sample manga images
- [x] 2.3.2: Verify text extraction accuracy
- [x] 2.3.3: Debug any issues with text detection
 
---
 
## Phase 3: Translation Module

### Task 3.1: Choose Translation Method **[Difficulty: 3/10]** [Depends on: 1.3]
- [x] 3.1.1: Decide: Local model (JustFrederik/sugoi-v4-ja-en-ct2)
- [x] 3.1.2: Sign up for API key if using DeepL/Google (free tier) (N/A for local model)
- [x] 3.1.3: Store API key securely (environment variable or config file) (N/A for local model)

### Task 3.2: Setup Translation **[Difficulty: 4/10]** [Depends on: 3.1]
- [x] 3.2.1: Install translation library: `pip install transformers sentencepiece ctranslate2`
- [x] 3.2.2: Create `translation_module.py`
- [x] 3.2.3: Write function to translate Japanese text to English
- [x] 3.2.4: Test translation with sample Japanese sentences

---

## Phase 4: Inpainting (Text Removal)

### Task 4.1: Setup Inpainting Model **[Difficulty: 5/10]** [Depends on: 1.3]
- [x] 4.1.1: Install IOpaint: `pip install iopaint`
- [x] 4.1.2: Create `inpainting_module.py` (or adapt existing)
- [x] 4.1.3: Write function to initialize IOpaint model (e.g., LaMa)

### Task 4.2: Implement Text Removal **[Difficulty: 6/10]** [Depends on: 4.1, 2.2]
- [x] 4.2.1: Write function to create mask from text bounding boxes (Adapt for IOpaint)
- [x] 4.2.2: Write function to apply IOpaint inpainting to masked regions
- [x] 4.2.3: Test on sample image - verify text is cleanly removed

### Task 4.3: Optimize Inpainting **[Difficulty: 7/10]** [Depends on: 4.2]
- [ ] 4.3.1: Adjust mask padding/dilation for cleaner results
- [ ] 4.3.2: Test with different text sizes and backgrounds (Deferred to Phase 7)
- [ ] 4.3.3: Handle edge cases (text near image borders) (Deferred to Phase 7)

---

## Phase 5: Text Rendering (Placing English Text)

### Task 5.1: Basic Text Placement **[Difficulty: 5/10]** [Depends on: 2.2, 3.2]
- [x] 5.1.1: Install text rendering: Already in Pillow
- [x] 5.1.2: Create `text_renderer.py`
- [x] 5.1.3: Write function to calculate appropriate font size for text box
- [x] 5.1.4: Write function to render English text at saved coordinates

### Task 5.2: Text Formatting **[Difficulty: 7/10]** [Depends on: 5.1]
- [x] 5.2.1: Implement word wrapping for long translations
- [x] 5.2.2: Center text within original bounding box
- [x] 5.2.3: Choose readable font (include font file or use system font)
- [x] 5.2.4: Add text background/outline for readability

### Task 5.3: Test Text Rendering **[Difficulty: 4/10]** [Depends on: 5.2]
- [x] 5.3.1: Test with various text lengths
- [x] 5.3.2: Ensure text fits within speech bubbles
- [x] 5.3.3: Adjust positioning as needed

---

## Phase 6: Integration (Complete Pipeline)

### Task 6.1: Create Main Pipeline **[Difficulty: 6/10]** [Depends on: 2.3, 3.2, 4.2, 5.2]
- [x] 6.1.1: Create `main.py`
- [x] 6.1.2: Import all modules
- [x] 6.1.3: Write pipeline function that chains all steps:
  - Load image → OCR → Inpaint → Translate → Render → Save

### Task 6.2: Add File Handling **[Difficulty: 4/10]** [Depends on: 6.1]
- [x] 6.2.1: Create input/output folders
- [x] 6.2.2: Add command-line arguments for input image path
- [x] 6.2.3: Save output image with timestamp/versioning

### Task 6.3: Error Handling **[Difficulty: 5/10]** [Depends on: 6.1]
- [x] 6.3.1: Add try-catch blocks for each pipeline step
- [x] 6.3.2: Add logging to track progress
- [x] 6.3.3: Handle cases with no text detected

---

## Phase 7: Testing & Polish

### Task 7.1: End-to-End Testing **[Difficulty: 4/10]** [Depends on: 6.3]
- [ ] 7.1.1: Test complete pipeline with 5+ different manga images
- [ ] 7.1.2: Document any failure cases
- [ ] 7.1.3: Measure processing time per image

### Task 7.2: Improvements **[Difficulty: 5/10]** [Depends on: 7.1]
- [ ] 7.2.1: Create before/after comparison visualization
- [ ] 7.2.2: Add progress bars for long operations
- [ ] 7.2.3: Optimize slow steps

### Task 7.3: Documentation **[Difficulty: 3/10]** [Depends on: 7.1]
- [ ] 7.3.1: Write README.md with setup instructions
- [ ] 7.3.2: Add usage examples
- [ ] 7.3.3: Document known limitations

---

## MVP Complete! 🎉

**Next Steps (Post-MVP):**
- Batch processing for multiple images
- Web interface (Gradio/Streamlit)
- Vertical text handling improvements
- Custom font selection
- Quality comparison metrics

---

## Current Status
**Last Updated:** Main pipeline (`main.py`) created with integration, file handling, and error handling.
**Current Phase:** Phase 7 - Testing & Polish
**Next Task:** Task 7.1.1 - Test complete pipeline with 5+ different manga images
**Completed:** Phase 1 (all tasks), Phase 2 (all tasks), Phase 3 (all tasks), Phase 4 (all tasks), Phase 5 (all tasks), Phase 6 (all tasks)