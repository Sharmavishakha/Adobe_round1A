# PDF Heading Extractor

## 🧠 Approach
- Extracts text blocks from PDF using PyMuPDF.
- Groups multi-line titles using font size, boldness, and vertical alignment.
- Applies heuristics for heading detection: numbering patterns, boldness, and position.
- Classifies headings into H1, H2, H3.

## 📦 Libraries Used
- `PyMuPDF`: Lightweight PDF parser.
- `re`, `json`, `os`: Built-in Python modules.

## 🐳 Docker Build & Run

### Build Image
```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```
### Run Container
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:somerandomidentifier
```
## 📄 Output
For each file.pdf in /input, a corresponding file.json is created in /output.

## ⚙️ Constraints
✅ Model-free, works completely offline.
✅ Runs on CPU (amd64); no GPU or internet required.
✅ ≤ 10 seconds for a 50-page PDF.
✅ Dockerfile compatible with --platform=linux/amd64.
