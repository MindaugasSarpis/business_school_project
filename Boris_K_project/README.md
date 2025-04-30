# 📄 Invoice Reader

## 📋 Description
This Python script extracts invoice data (invoice number, date, and amount) from PDF files in a specified folder and saves the extracted data to a CSV file. It uses the `fitz` library (PyMuPDF) to read PDF files and `pandas` to handle data and save it to a CSV file.

## 📦 Requirements
To run this script on another PC, you need to have the following Python packages installed:

- `PyMuPDF` (fitz)
- `pandas`

You can install these packages using `pip`:

```sh
pip install pymupdf pandas
```

## 🛠️ Setup Instructions

1. **Clone or Download the Script**: Download the `Invoice_reader.py` script to your local machine.

2. **Prepare the Invoices Folder**: Create a folder named `invoices_folder` and place all your PDF invoices in this folder.

3. **Run the Script**: Open a terminal or command prompt, navigate to the directory containing the `Invoice_reader.py` script, and run the script:

    ```sh
    python "Invoice_reader.py"
    ```

    The script will process all PDF files in the specified folder, extract the invoice data, and save it to a CSV file named `invoice_data.csv`.

4. **View the Results**: The script will automatically open the generated CSV file after processing the invoices.

## 💻 Example Usage

```python
# Example usage
folder_path = "invoices_folder"  # Change this to the folder containing your PDFs
process_invoices(folder_path)
```

## 📝 Script Overview
- `extract_invoice_data(pdf_path)`: Extracts invoice number, date, and amount from a given PDF file using regex patterns.
- `process_invoices(folder_path, output_csv="invoice_data.csv")`: Reads multiple invoice PDFs from a folder, extracts data using `extract_invoice_data`, and saves the data to a CSV file.

## 📊 Output

The script will output a CSV file (`invoice_data.csv`) containing the extracted invoice data with the following columns:

- **File Name**
- **Invoice Number**
- **Invoice Date**
- **Invoiced Amount**

## 📈 Example Output

```csv
File Name,Invoice Number,Invoice Date,Invoiced Amount
invoice1.pdf,12345,01 January 2025,1000.00
invoice2.pdf,67890,15 February 2025,1500.50
```

## 🗒️ Notes
- Ensure that the PDF files in the `invoices_folder` are properly formatted and contain the necessary invoice information for accurate extraction.
- Modify the regex patterns in the script if your invoices have different formats or labels.

Enjoy using the Invoice Reader script! 🎉
