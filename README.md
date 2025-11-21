# 📚 PDF Pages Extractor App

This repository contains a simple web application built with **Streamlit** that allows users to upload a PDF file, select a range of pages to extract, and download the resulting sub-document as a new PDF file.

## ✨ Features

  * **User-Friendly Interface:** Intuitive web interface powered by Streamlit.
  * **Simple Upload:** Drag-and-drop or browse functionality for PDF files.
  * **Page Range Selection:** Uses number inputs to easily specify the start and end pages for extraction.
  * **Efficient Processing:** Utilizes the robust `PyPDF2` library for fast page manipulation.
  * **Direct Download:** Allows instant download of the extracted PDF file.

## ⚙️ How to Run Locally

### Prerequisites

You need **Python 3.x** and `pip` installed on your system.

### 1\. Clone the Repository

```bash
git clone https://github.com/chusk2/pdf_pages_extractor.git
cd pdf_pages_extractor
```

### 2\. Install Dependencies

The application requires the `streamlit` and `PyPDF2` libraries.

```bash
pip install streamlit PyPDF2
```

### 3\. Run the App

Execute the Streamlit command to launch the web application:

```bash
streamlit run pdf_pages_extractor.py
```

This command will automatically open a browser window displaying the application (usually at `http://localhost:8501`).

## 🖥️ Application Workflow

1.  **Upload:** The user uploads a PDF file using the file uploader widget.
2.  **Input:** The app calculates the total number of pages and presents two dynamic **number input** fields constrained by the document's length for selecting the start and end pages.
3.  **Extraction:** Upon clicking the **'Extract Pages'** button, the script uses `PyPDF2.PdfReader` to read the input and `PyPDF2.PdfWriter` to create the new document, copying the specified page range.
4.  **Download:** The resulting PDF is held in memory using `io.BytesIO` and made available for the user via a **Download button**.

## 🤝 Contributing

Contributions are welcome\! Feel free to open an issue or submit a pull request if you find a bug or want to add a feature (e.g., extracting non-consecutive pages).

## 👤 Author

[**danicoder**](https://github.com/chusk2)
