from pypdf import PdfWriter
import os

def merge_pdfs(pdf_list, output_name):
    merger = PdfWriter()

    for pdf in pdf_list:
        if os.path.exists(pdf):
            print(f"Adding {pdf}...")
            merger.append(pdf)
        else:
            print(f"Warning: {pdf} not found. Skipping.")

    print(f"Writing to {output_name}...")
    merger.write(output_name)
    merger.close()
    print("✅ Done!")

def main():
    # In a real app, you might ask the user for inputs
    # For testing, ensure you have dummy.pdf or create empty ones
    pdfs = input("Enter PDF filenames separated by space: ").split()
    output = "merged_document.pdf"
    
    if pdfs:
        merge_pdfs(pdfs, output)
    else:
        print("No files provided.")

if __name__ == "__main__":
    main()