# Local Secure PDF Toolkit

A standalone, privacy-first PDF manipulation suite written in Python. It provides local equivalents of common online PDF utilities (merging, splitting, compression, signing, format conversion, diffing, and editing) without uploading any data to external servers or cloud services.

---

## Key Features

- **100% Offline & Private:** All cryptographic signing and document parsing happen strictly in memory and local storage.
- **OS File Dialogs:** Uses native system explorer windows for intuitive file picking and saving.
- **Interactive Visual Previews:** Real-time thumbnail preview grids to verify pages before reordering, deleting, or modifying.
- **Smart Signing:** Cryptographic PDF signing via `.p12` or `.pfx` certificates (including legacy FNMT / DNIe algorithms) without overwriting existing signatures.
- **Visual Diffing Engine:** Word-by-word visual layout and text comparison highlighting additions (green), deletions (red), and replacements (orange).

---

## Included Tools

| # | Tool | Description |
| :---: | :--- | :--- |
| **1** | **Merge PDFs** | Combine multiple PDF files in custom sequence into a single file. |
| **2** | **Split PDF** | Extract every page into separate files, or define custom page ranges across multiple output files (e.g., `1-3, 5`). |
| **3** | **Reorder Pages** | Rearrange page sequences with an on-screen visual preview gallery. |
| **4** | **Compress PDF** | Reduce file size via stream deflating, duplicate cleanup, and unreferenced object removal. |
| **5** | **PDF to DOCX** | Convert PDFs into editable Microsoft Word documents with structural layout parsing. |
| **6** | **Compare PDFs** | Generate a text diff log and an annotated PDF displaying color-coded bounding boxes on altered text. |
| **7** | **Digital Signing** | Sign documents cryptographically using a `.p12`/`.pfx` software certificate. |
| **8** | **Delete Pages** | Remove unwanted pages by index while referencing a live thumbnail gallery. |
| **9** | **Insert Page Numbers** | Add customizable page numbers (Format: `1`, `Page 1`, `1 of N`; Fonts: Helvetica, Times, Courier; custom alignments). |
| **10** | **Add Text / Images** | Overlay watermarks, text annotations, stamps, or images with custom opacity and coordinates. |

---

## Prerequisites
- **Python 3.9+** (Tested on Python 3.10–3.13)
- Windows, macOS, or Linux

### Dependencies
Install all required libraries via `pip`:
```pip install pypdf pymupdf pdf2docx pyHanko cryptography pillow```

---

## Quick Start Guide

1. **Clone or Download the Repository:** ```git clone [https://github.com/your-username/PythonPDFToolkit.git](https://github.com/your-username/PythonPDFToolkit.git)
cd PythonPDFToolkit```
2. **Run the Application:** ```python pdftool.py```
3. **Usage Workflow:**
   * Select an option from the main numerical menu (0 to 10)
   * When prompted, use the system Explorer dialog to choose your input files
   * If an operation provides a preview (reorder, delete, page numbers) inpect the thumbnail window before typing parameters in the terminal
   * Choose your destination location and filename in the final save dialog

---

## Certificate Signing Notes (Option 7)

- Supports standard PKCS#12 (.p12 / .pfx) certificate files
- Accommodates legacy encryption formats
- Passwords are typed securely into the terminal using masked input (getpass)
- Appends non - destructive incremental signatures so existing signatures on the PDF remain valid


--- 
## Architecture

- `pypdf`: PDF page tree parsing, merging, splitting and deletions
- `pymupdf`: low - level rendering, thumbnail rasterization, stream compression, text search/diffing, and direct page overlays
- `pdf2docx`: layout extraction (paragraphs, tables, fonts) to `.docx` format
- `pyHanko` + `cryptography`: PKCS#7/CMS digital signing, certificate validation and cryptographic hashing
- `tkinter` + `Pillow`: native OS dialogs and scrollable multicolumn preview canvas
