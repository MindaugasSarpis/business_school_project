import fitz
import re
import os
import pandas as pd

def extract_invoice_data(pdf_path):
    """Extracts invoice number, date, and amount from a given PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""

        # Read text from all pages
        for page in doc:
            text += page.get_text("text") + "\n"

        # Define regex patterns
        invoice_number_pattern = r"(?:Invoice No.|INVOICE NR:|Invoice Number:|Inv #)[\s:]*([\w\d-]+)"
        date_pattern = r"(?:Date:|Invoice Date:|DATE:|Invoice Date:)[:#]?\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})"
        amount_pattern = r"(?:Total Amount:|Total Due|Total Sum:|TOTAL AMOUNT:)[\s:]*\$?([\d,]+\.?\d*)"

        # Extract values using regex
        invoice_number = re.search(invoice_number_pattern, text, re.IGNORECASE)
        date = re.search(date_pattern, text, re.IGNORECASE)
        amount = re.search(amount_pattern, text, re.IGNORECASE)

        return {
            "File Name": os.path.basename(pdf_path),
            "Invoice Number": invoice_number.group(1) if invoice_number else "Not Found",
            "Invoice Date": date.group(1) if date else "Not Found",
            "Invoiced Amount": amount.group(1) if amount else "Not Found"
        }

    except Exception as e:
        return {"File Name": os.path.basename(pdf_path), "Error": str(e)}

def process_invoices(folder_path, output_csv="invoice_data.csv"):
    """Reads multiple invoice PDFs from a folder and saves extracted data to a CSV file."""
    invoice_list = []
    
    # Scan all PDF files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):  # Process only PDF files
            file_path = os.path.join(folder_path, file_name)
            invoice_data = extract_invoice_data(file_path)
            invoice_list.append(invoice_data)

    # Convert list to a DataFrame and save as CSV
    df = pd.DataFrame(invoice_list)
    df.to_csv(output_csv, index=False)
    
    print(f"✅ Processed {len(invoice_list)} invoices. Data saved to '{output_csv}'.")

    # Automatically open the generated CSV file
    os.startfile(output_csv)

# Example usage
folder_path = "invoices_folder"  # Change this to the folder containing your PDFs
process_invoices(folder_path)
