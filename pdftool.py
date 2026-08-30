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

# 4. COMPRESS PDF
def compress_pdf():
    file = pick_file("Select PDF to Compress")
    if not file: return
    output = pick_save("Save Compressed PDF")
    if not output: return

    doc = fitz.open(file)
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

    doc1, doc2 = fitz.open(file1), fitz.open(file2)
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