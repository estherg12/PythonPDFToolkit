import os
import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
from pdf2docx import Converter

# Hide the root Tkinter window
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)

def pick_file(title="Select a file", filetypes=[("PDF files", "*.pdf")]):
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def pick_files(title="Select multiple files", filetypes=[("PDF files", "*.pdf")]):
    return list(filedialog.askopenfilenames(title=title, filetypes=filetypes))

def pick_save(title="Save output as", default_ext=".pdf", filetypes=[("PDF file", "*.pdf")]):
    return filedialog.asksaveasfilename(title=title, defaultextension=default_ext, filetypes=filetypes)

# 1. MERGE PDFs
def merge_pdfs():
    files = pick_files("Select PDFs to Merge")
    if not files: return
    output = pick_save("Save Merged PDF", ".pdf")
    if not output: return

    writer = PdfWriter()
    for file in files:
        writer.append(file)
    with open(output, "wb") as f:
        writer.write(f)
    print(f"Successfully merged into: {output}")

# 2. SPLIT PDF
def split_pdf():
    file = pick_file("Select PDF to Split")
    if not file: return
    folder = filedialog.askdirectory(title="Select Output Folder")
    if not folder: return

    reader = PdfReader(file)
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = os.path.join(folder, f"page_{i+1}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
    print(f"Split {len(reader.pages)} pages into: {folder}")

# 3. REORDER PAGES
def reorder_pdf():
    file = pick_file("Select PDF to Reorder")
    if not file: return
    reader = PdfReader(file)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    order_str = input(f"Enter page order separated by commas (1-indexed, e.g. 3,1,2): ")
    try:
        order = [int(p.strip()) - 1 for p in order_str.split(",")]
        writer = PdfWriter()
        for idx in order:
            if 0 <= idx < total_pages:
                writer.add_page(reader.pages[idx])
        output = pick_save("Save Reordered PDF")
        if not output: return
        with open(output, "wb") as f:
            writer.write(f)
        print(f"Saved reordered PDF to: {output}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    while True:
        print("\n--- LOCAL SECURE PDF TOOLKIT ---")
        print("1. Merge PDFs")
        print("2. Split PDF")
        print("3. Reorder Pages")
        print("4. Compress PDF")
        print("5. PDF to DOCX")
        print("6. Compare PDFs")
        print("7. Sign PDF (Digital Certificate)")
        print("0. Exit")
        
        choice = input("\nSelect an option: ").strip()
        if choice == "1": merge_pdfs()
        elif choice == "2": split_pdf()
        elif choice == "3": reorder_pdf()
        elif choice == "4": compress_pdf()
        elif choice == "5": pdf_to_docx()
        elif choice == "6": compare_pdfs()
        elif choice == "7": sign_pdf()
        elif choice == "0": break
        else: print("[!] Invalid option.")

if __name__ == "__main__":
    main()