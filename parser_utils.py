

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
                    y_coord = spans[0]["origin"][1]

                    elements.append({
                        "text": text,
                        "size": font_size,
                        "bold": is_bold,
                        "page": page_num + 1,
                        "y": y_coord
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


def group_title_lines(candidates, max_gap=5):
    grouped = []
    current_group = []

    for i in range(len(candidates) - 1):
        curr = candidates[i]
        next_ = candidates[i + 1]

        same_style = curr["size"] == next_["size"] and curr["bold"] == next_["bold"]
        close_y = abs(next_["y"] - curr["y"]) < max_gap and curr["page"] == next_["page"]

        if same_style and close_y:
            if not current_group:
                current_group.append(curr)
            current_group.append(next_)
        else:
            if current_group:
                grouped.append(current_group)
                current_group = []

    if current_group:
        grouped.append(current_group)

    if not grouped:
        return [candidates]  # fallback to ungrouped

    return grouped

def is_bullet_point(text):
    bullet_starts = ("•", "●", "-", "*")
    return (
        text.strip().startswith(bullet_starts) or
        re.match(r"^\d+\s+credits", text.strip().lower()) or
        re.match(r"^●?\s*\d+\s+credits", text.strip().lower())
    )

def classify_headings(elements):
    if not elements:
        return "", []

    candidate_title_elements = [e for e in elements if e["page"] <= 2]
    max_font_size = max((e["size"] for e in candidate_title_elements), default=0)

    # Step 1: Group likely title candidates
    large_texts = [e for e in candidate_title_elements if e["size"] >= max_font_size * 0.9]
    grouped = group_title_lines(sorted(large_texts, key=lambda x: (x["page"], x["y"])))

    if grouped:
        best_group = max(grouped, key=lambda g: sum(len(x["text"]) for x in g))
        combined_title = " ".join(e["text"].strip() for e in best_group).strip()

        # Reject if the "title" looks like a party line or marketing text (heuristic)
        if len(combined_title.split()) <= 4 and combined_title.lower() in ["hope to see you there!", "rsvp", "address"]:
            title = ""
        else:
            title = combined_title
    else:
        title = ""

    headings = []
    used = set()
    exclude_keywords = {"s.no", "name", "age", "relationship", "date"}

    for e in elements:
        text = e["text"].strip()
        if not text or text.lower() in used or text == title:
            continue
        clean_text = text.lower()
        used.add(clean_text)

        if clean_text in exclude_keywords:
            continue

        if len(text.split()) < 2 and not looks_like_heading(text):
            continue

        if looks_like_heading(text):
            level = get_heading_level(text)
            headings.append({
                "level": level,
                "text": text,
                "page": e["page"]
            })

        elif (
            e["bold"]
            and is_probable_heading(text)
            and e["size"] >= max_font_size * 0.75
            and not is_bullet_point(text)
            and len(text.split()) <= 8
        ):
            # even if it's not all uppercase, if it's decorative and large, keep it
            headings.append({
                "level": "H1",
                "text": text,
                "page": e["page"]
            })

    return title, headings


# def classify_headings(elements):
#     if not elements:
#         return "", []

#     # Detect probable title using multi-line grouping
#     candidate_title_elements = [e for e in elements if e["page"] <= 2]
#     max_font_size = max(e["size"] for e in candidate_title_elements)

#     large_texts = [e for e in candidate_title_elements if e["size"] >= max_font_size * 0.9]
#     grouped = group_title_lines(sorted(large_texts, key=lambda x: (x["page"], x["y"])))

#     if grouped:
#         best_group = max(grouped, key=lambda g: sum(len(x["text"]) for x in g))
#         title = " ".join(e["text"].strip() for e in best_group).strip()
#     else:
#         title = next((e["text"] for e in candidate_title_elements if e["size"] == max_font_size), "")

#     headings = []
#     used = set()  # Avoid duplicates
#     exclude_keywords = {"s.no", "name", "age", "relationship", "date"}

#     for e in elements:
#         text = e["text"].strip()
#         if not text or text == title or text.lower() in used:
#             continue
#         if is_bullet_point(text):
#             continue
#         clean_text = text.lower().strip()
#         used.add(clean_text)

#         # Skip likely form/table fields
#         if clean_text in exclude_keywords:
#             continue

#         # Also skip pure numbers or overly short one-word lines
#         if len(text.split()) < 2 and not looks_like_heading(text):
#             continue

#         if looks_like_heading(text):
#             level = get_heading_level(text)
#             headings.append({
#                 "level": level,
#                 "text": text,
#                 "page": e["page"]
#             })

#         elif (
#             e["bold"]
#             and is_probable_heading(text)
#             and e["size"] >= max_font_size * 0.75
#             and not is_bullet_point(text)
#             and text.isupper()  # All caps headings like "PATHWAY OPTIONS"
#             and len(text.split()) <= 5  # Usually short headings
#         ):
#             level = "H1" if e["size"] >= max_font_size * 0.9 else "H2"
#             headings.append({
#                 "level": level,
#                 "text": text,
#                 "page": e["page"]
#             })


#     return title, headings


def save_json(title, headings, output_path):
    data = {
        "title": title,
        "outline": headings
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
