# PDF Structure Extractor

This project is a Dockerized Python solution for extracting the **title** and **structured outline (H1, H2, H3)** from PDF documents. It is built to run in a constrained offline environment, with no internet access, limited model size (if used), and CPU-only processing. The solution supports general-purpose PDFs such as research papers, forms, academic syllabi, and flyers.

---

## Features

- Automatically processes all `.pdf` files from the input directory
- Extracts document **title** using font size and position heuristics
- Extracts **headings (H1, H2, H3)** using:
  - Section numbering patterns (e.g., `2.1`, `3.2.1`)
  - Font styling (size, boldness)
  - Uppercase detection
- Skips non-headings such as:
  - Form fields (e.g., `Name`, `Date`, `S.No`)
  - Bullet points and tabular content
- Outputs are saved as structured `.json` files

---

## Approach

### 1. **Text & Style Extraction**
Uses [`PyMuPDF`](https://pymupdf.readthedocs.io/) (`fitz`) to extract:
- Text
- Font size
- Font name (to infer boldness)
- Vertical position (`y`) of each text span

### 2. **Title Detection**
- Looks on the first two pages
- Groups top lines with highest font sizes
- Picks the group with most text length as the title

### 3. **Heading Classification**
- Checks for numbering patterns (`1.`, `2.3`, `3.1.2`)
- Uses font size and boldness to assign `H1`, `H2`, `H3` levels
- Applies additional filters to skip:
  - Table labels
  - Form fields
  - Bullet-pointed lines
  - Single-word or short numerical lines

### 4. **JSON Output Format**
Example structure of output file:
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "1. Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "2.1 Objectives",
      "page": 2
    }
  ]
}
```

## Docker Build & Run

### Build Image
```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```
### Run Container
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  mysolutionname:somerandomidentifier
```
## Dependencies
All dependencies are installed within the container and include:
Python 3.10+
PyMuPDF (fitz)
re and json (standard library)

## Constraints
✅ Model-free, works completely offline.
✅ Runs on CPU (amd64); no GPU or internet required.
✅ ≤ 10 seconds for a 50-page PDF.
✅ Dockerfile compatible with --platform=linux/amd64.

## File Structure
```bash
.
├── Dockerfile
├── main.py
├── parser_utils.py
├── input/
│   └── *.pdf
├── output/
│   └── *.json
└── README.md
```
