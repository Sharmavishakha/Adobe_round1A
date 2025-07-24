# import fitz  # PyMuPDF
# import json

# def extract_pdf_structure(pdf_path):
#     doc = fitz.open(pdf_path)
#     elements = []

#     for page_num in range(len(doc)):
#         page = doc[page_num]
#         blocks = page.get_text("dict")["blocks"]

#         for block in blocks:
#             if "lines" in block:
#                 for line in block["lines"]:
#                     spans = line.get("spans", [])
#                     if not spans:
#                         continue

#                     text = " ".join(span["text"] for span in spans).strip()
#                     if not text:
#                         continue

#                     font_size = spans[0]["size"]
#                     font_name = spans[0]["font"]
#                     is_bold = "Bold" in font_name or "bold" in font_name

#                     elements.append({
#                         "text": text,
#                         "size": font_size,
#                         "bold": is_bold,
#                         "page": page_num + 1
#                     })
#     return elements


# def classify_headings(elements):
#     if not elements:
#         return "", []

#     # Determine the largest font size on the first 1–2 pages
#     candidate_title_elements = [e for e in elements if e["page"] <= 2]
#     max_font_size = max(e["size"] for e in candidate_title_elements)
#     title = next((e["text"] for e in candidate_title_elements if e["size"] == max_font_size), "")

#     headings = []
#     for e in elements:
#         if e["text"] == title:
#             continue
#         if e["size"] >= 18:
#             level = "H1"
#         elif e["size"] >= 14:
#             level = "H2"
#         elif e["size"] >= 12:
#             level = "H3"
#         else:
#             continue

#         headings.append({
#             "level": level,
#             "text": e["text"],
#             "page": e["page"]
#         })

#     return title, headings


# def save_json(title, headings, output_path):
#     data = {
#         "title": title,
#         "outline": headings
#     }
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)



import fitz  # PyMuPDF
import json
import re


def extract_pdf_structure(pdf_path):
    doc = fitz.open(pdf_path)
    elements = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    spans = line.get("spans", [])
                    if not spans:
                        continue

                    text = " ".join(span["text"] for span in spans).strip()
                    if not text:
                        continue

                    font_size = spans[0]["size"]
                    font_name = spans[0]["font"]
                    is_bold = "Bold" in font_name or "bold" in font_name

                    elements.append({
                        "text": text,
                        "size": font_size,
                        "bold": is_bold,
                        "page": page_num + 1
                    })

    return elements

def is_probable_heading(text):
    """
    Heuristic to catch bold lines that are likely true headings.
    - Short
    - Starts with uppercase
    - Doesn't end with punctuation
    """
    return (
        len(text.split()) <= 8 and
        text[0].isupper() and
        not text.strip().endswith((".", ":", ";")) and
        text.strip()[0].isalpha()
    )


def looks_like_heading(text):
    """
    Detects if text looks like a section heading based on numbering pattern.
    E.g., "1 Introduction", "2.3 Evaluation", "3.2.1 Metrics"
    """
    return bool(re.match(r"^\d+(\.\d+)*\s+\w+", text))


def get_heading_level(text):
    """
    Determines H1, H2, H3 based on section numbering depth.
    """
    match = re.match(r"^(\d+(\.\d+)*)", text)
    if not match:
        return "H2"
    dots = match.group(1).count(".")
    if dots == 0:
        return "H1"
    elif dots == 1:
        return "H2"
    else:
        return "H3"


def classify_headings(elements):
    if not elements:
        return "", []

    # Detect title
    candidate_title_elements = [e for e in elements if e["page"] <= 2]
    max_font_size = max(e["size"] for e in candidate_title_elements)
    title = next((e["text"] for e in candidate_title_elements if e["size"] == max_font_size), "")

    headings = []

    for i, e in enumerate(elements):
        if e["text"] == title:
            continue

        text = e["text"]
        size = e["size"]
        bold = e["bold"]

        if looks_like_heading(text):
            level = get_heading_level(text)
            headings.append({
                "level": level,
                "text": text,
                "page": e["page"]
            })

        elif bold and is_probable_heading(text) and size >= 10:
            level = "H2"
            headings.append({
                "level": level,
                "text": text,
                "page": e["page"]
            })

    return title, headings


def save_json(title, headings, output_path):
    data = {
        "title": title,
        "outline": headings
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
