import os
from parser_utils import extract_pdf_structure, classify_headings, save_json

INPUT_DIR = r"C:/Users/hp/OneDrive/Desktop/round1A/input"
OUTPUT_DIR = r"C:/Users/hp/OneDrive/Desktop/round1A/output"

def main():
    print("Running script...")

    files_found = False

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".pdf"):
            files_found = True
            print(f"Processing {filename}...")
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))

            elements = extract_pdf_structure(pdf_path)
            title, headings = classify_headings(elements)
            save_json(title, headings, output_path)

    if not files_found:
        print("No PDF files found in input folder.")

if __name__ == "__main__":
    main()
