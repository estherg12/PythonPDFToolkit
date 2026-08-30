import os
import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader, PdfWriter
import pymupdf  # PyMuPDF
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
    print("Select PDFs to merge")
    files = pick_files("Select PDFs to Merge")
    if not files: return
    print(f"Selected {len(files)} files for merging.")
    print("Choose output file name and location.")
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
    reader = PdfReader(file)
    total_pages = len(reader.pages)
    print(f"\nLoaded PDF with {total_pages} total page(s).")

    print("\nSplit Modes:")
    print("1. All individual pages (1 page per PDF)")
    print("2. Custom split (choose number of output PDFs and page ranges)")
    mode = input("Select mode (1/2, default 2): ").strip() or "2"

    folder = filedialog.askdirectory(title="Select Output Folder")
    if not folder: return

    base_name = os.path.splitext(os.path.basename(file))[0]

    # Helper function to parse inputs like "1-3, 5, 7-9" into 0-indexed integer list
    def parse_page_range(range_str, max_p):
        selected = []
        for part in range_str.split(","):
            part = part.strip()
            if "-" in part:
                start, end = map(int, part.split("-"))
                selected.extend(range(start - 1, end))
            elif part:
                selected.append(int(part) - 1)
        return [p for p in selected if 0 <= p < max_p]

    if mode == "1":
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            out_path = os.path.join(folder, f"{base_name}_page_{i+1}.pdf")
            with open(out_path, "wb") as f:
                writer.write(f)
        print(f"Split into {total_pages} individual files in: {folder}")

    else:
        try:
            num_splits = int(input(f"How many output PDFs do you want to create? (2 to {total_pages}): ").strip())
            if not (1 <= num_splits <= total_pages):
                print(f"[!] Please enter a number between 1 and {total_pages}.")
                return

            for i in range(num_splits):
                print(f"\n--- PDF {i + 1} of {num_splits} ---")
                range_input = input(f"Enter pages for PDF #{i+1} (e.g., '1-2, 4' or '3'): ").strip()
                page_indices = parse_page_range(range_input, total_pages)

                if not page_indices:
                    print(f"No valid pages provided for PDF #{i+1}. Skipping this file.")
                    continue

                writer = PdfWriter()
                for idx in page_indices:
                    writer.add_page(reader.pages[idx])

                out_name = input(f"Enter filename for PDF #{i+1} (default: {base_name}_part_{i+1}.pdf): ").strip()
                if not out_name:
                    out_name = f"{base_name}_part_{i+1}.pdf"
                if not out_name.endswith(".pdf"):
                    out_name += ".pdf"

                out_path = os.path.join(folder, out_name)
                with open(out_path, "wb") as f:
                    writer.write(f)
                print(f"Created: {out_name} with pages {[p+1 for p in page_indices]}")

            print(f"\nAll parts successfully saved to: {folder}")

        except ValueError as e:
            print(f"Invalid input: {e}")

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

# 4. COMPRESS PDF
def compress_pdf():
    file = pick_file("Select PDF to Compress")
    if not file: return
    output = pick_save("Save Compressed PDF")
    if not output: return

    doc = pymupdf.open(file)
    # Garbage=4 cleans unused objects, deflate=True compresses streams
    doc.save(output, garbage=4, deflate=True, clean=True)
    doc.close()
    
    orig_size = os.path.getsize(file) / 1024
    new_size = os.path.getsize(output) / 1024
    print(f"Compressed: {orig_size:.1f} KB -> {new_size:.1f} KB")

# 5. PDF TO DOCX
def pdf_to_docx():
    file = pick_file("Select PDF to Convert")
    if not file: return
    output = pick_save("Save Word Document", ".docx", [("Word Document", "*.docx")])
    if not output: return

    cv = Converter(file)
    cv.convert(output, start=0, end=None)
    cv.close()
    print(f"Converted to Word: {output}")

# 6. COMPARE PDFS (Highlight text differences)
def compare_pdfs():
    file1 = pick_file("Select First PDF")
    file2 = pick_file("Select Second PDF")
    if not file1 or not file2: return

    doc1, doc2 = pymupdf.open(file1), pymupdf.open(file2)
    max_pages = max(len(doc1), len(doc2))
    diff_found = False

    for page_num in range(max_pages):
        text1 = doc1[page_num].get_text() if page_num < len(doc1) else "[NO PAGE]"
        text2 = doc2[page_num].get_text() if page_num < len(doc2) else "[NO PAGE]"
        if text1 != text2:
            diff_found = True
            print(f"Difference detected on Page {page_num + 1}")

    if not diff_found:
        print("Documents have identical text across all pages.")

# 7. SIGN WITH CERTIFICADO DIGITAL (.p12 / .pfx)
def sign_pdf():
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
    from pyhanko.sign import fields, signers
    from pyhanko.sign.pkcs11 import open_pkcs11_session
    import getpass

    pdf_file = pick_file("Select PDF to Sign")
    if not pdf_file: return
    cert_file = pick_file("Select Digital Certificate (.p12 / .pfx)", [("Certificates", "*.p12 *.pfx")])
    if not cert_file: return
    
    passphrase = getpass.getpass("Enter Certificate Password: ").encode()
    output_pdf = pick_save("Save Signed PDF")
    if not output_pdf: return

    try:
        signer = signers.load_crypto(
            key_file=cert_file,
            passphrase=passphrase
        )
        with open(pdf_file, 'rb') as inf:
            w = IncrementalPdfFileWriter(inf)
            fields.append_signature_field(
                w, sig_field_spec=fields.SigFieldSpec(sig_field_name='Signature1')
            )
            with open(output_pdf, 'wb') as outf:
                signers.sign_pdf(
                    w, signers.PdfSignatureMetadata(field_name='Signature1'),
                    signer=signer, output=outf
                )
        print(f"Document signed securely: {output_pdf}")
    except Exception as e:
        print(f"Signing failed: {e}")

# 8. DELETE PAGES
def delete_pages():
    file = pick_file("Select PDF to Remove Pages From")
    if not file: return
    reader = PdfReader(file)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    del_str = input("Enter page numbers to DELETE separated by commas (e.g. 1, 4, 7): ")
    try:
        pages_to_delete = {int(p.strip()) - 1 for p in del_str.split(",") if p.strip()}
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if i not in pages_to_delete:
                writer.add_page(page)
                
        output = pick_save("Save PDF Without Deleted Pages")
        if not output: return
        with open(output, "wb") as f:
            writer.write(f)
        print(f"Saved updated PDF to: {output}")
    except Exception as e:
        print(f"Error: {e}")

# 9. INSERT PAGE NUMBERS
def insert_page_numbers():
    file = pick_file("Select PDF to Add Page Numbers")
    if not file: return
    
    print("\nPosition Options: 1) Bottom-Center  2) Bottom-Right  3) Top-Right")
    pos_choice = input("Select position (default 1): ").strip() or "1"
    
    print("Format Options: 1) '1'  2) 'Page 1'  3) '1 of N'")
    fmt_choice = input("Select format (default 3): ").strip() or "3"
    
    font_size = float(input("Font size (default 10): ").strip() or "10")
    print("Standard fonts: helv (Helvetica), times (Times-Roman), courier (Courier)")
    font_name = input("Font name (default helv): ").strip() or "helv"
    
    output = pick_save("Save PDF With Page Numbers")
    if not output: return

    doc = pymupdf.open(file)
    total = len(doc)
    for i, page in enumerate(doc):
        cur = i + 1
        if fmt_choice == "1": text = f"{cur}"
        elif fmt_choice == "2": text = f"Page {cur}"
        else: text = f"{cur} of {total}"

        rect = page.rect
        if pos_choice == "2":  # Bottom-Right
            point = pymupdf.Point(rect.width - 80, rect.height - 30)
        elif pos_choice == "3":  # Top-Right
            point = pymupdf.Point(rect.width - 80, 40)
        else:  # Bottom-Center
            point = pymupdf.Point(rect.width / 2 - 20, rect.height - 30)

        page.insert_text(point, text, fontsize=font_size, fontname=font_name, color=(0, 0, 0))

    doc.save(output)
    doc.close()
    print(f"Added page numbers to: {output}")

# 10. ADD TEXT OR IMAGE OVER PDF
def add_text_or_image():
    file = pick_file("Select Base PDF")
    if not file: return
    
    mode = input("Insert (1) Text or (2) Image? (1/2): ").strip()
    doc = pymupdf.open(file)
    total_pages = len(doc)
    
    page_target = input(f"Apply to page number (1-{total_pages}) or 'all': ").strip()
    pages_to_apply = range(total_pages) if page_target.lower() == "all" else [int(page_target) - 1]
    
    if mode == "2":
        img_path = pick_file("Select Image File", [("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if not img_path: return
        x = float(input("X coordinate from top-left (e.g., 100): ").strip() or "100")
        y = float(input("Y coordinate from top-left (e.g., 100): ").strip() or "100")
        w = float(input("Width (e.g., 150): ").strip() or "150")
        h = float(input("Height (e.g., 150): ").strip() or "150")
        rect = pymupdf.Rect(x, y, x + w, y + h)

        for p_idx in pages_to_apply:
            if 0 <= p_idx < total_pages:
                doc[p_idx].insert_image(rect, filename=img_path, overlay=True)
    else:
        text = input("Enter text to insert: ")
        x = float(input("X coordinate (e.g., 100): ").strip() or "100")
        y = float(input("Y coordinate (e.g., 100): ").strip() or "100")
        font_size = float(input("Font size (default 12): ").strip() or "12")
        font_name = input("Font (helv/times/courier, default helv): ").strip() or "helv"
        opacity = float(input("Opacity (0.1 to 1.0, default 1.0): ").strip() or "1.0")
        
        for p_idx in pages_to_apply:
            if 0 <= p_idx < total_pages:
                doc[p_idx].insert_text(
                    pymupdf.Point(x, y), text, fontsize=font_size, 
                    fontname=font_name, color=(0, 0, 0), fill_opacity=opacity
                )

    output = pick_save("Save Modified PDF")
    if not output: return
    doc.save(output)
    doc.close()
    print(f"Successfully inserted content into: {output}")

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
        print("8. Delete Pages")
        print("9. Insert Page Numbers")
        print("10. Add Text or Image")
        print("0. Exit")
        
        choice = input("\nSelect an option: ").strip()
        if choice == "1": merge_pdfs()
        elif choice == "2": split_pdf()
        elif choice == "3": reorder_pdf()
        elif choice == "4": compress_pdf()
        elif choice == "5": pdf_to_docx()
        elif choice == "6": compare_pdfs()
        elif choice == "7": sign_pdf()
        elif choice == "8": delete_pages()
        elif choice == "9": insert_page_numbers()
        elif choice == "10": add_text_or_image()
        elif choice == "0": break
        else: print("Invalid option.")

if __name__ == "__main__":
    main()