# streamlit app to extract pages from a PDF file
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

st.set_page_config(
    page_title=None,
    page_icon=None,
    layout='centered',
    initial_sidebar_state='auto',
    menu_items=None
)

st.header('PDF Extractor App 📚 → 💻')
st.subheader('Extract pages from a pdf file and download them.')

st.markdown('Page created by [danicoder](https://github.com/chusk2/) 🧔🏻')
st.markdown('App code available @ **[github](https://github.com/chusk2/pdf_pages_extractor)**')

# center the image using columns
c1, c2, c3 = st.columns([1,3,1])
with c2:
    st.image('./pdf_extractor_logo.png')


col1, col2 = st.columns([2,1])

# upload file column
with col1:

    c1, c2  =st.columns([1,1])
    with c1:
        file = st.file_uploader('Upload a PDF file', type = 'pdf')
    with c2:
        st.image('./upload_icon.jpg', width=100)

with col2:
    if file:
        st.session_state.file_name = file.name
        reader = PdfReader(file)
        pdf_length = len(reader.pages)

        st.write(f'The uploaded file has {pdf_length} pages.')

        start_page = st.number_input(label = 'Enter start page:',
                                    min_value = 1,
                                    max_value = pdf_length,
                                    value = 1,
                                    step = 1 )

        end_page = st.number_input(label = 'Enter end page:',
                                    min_value = 1,
                                    max_value = pdf_length,
                                    value = 1,
                                    step = 1 )
        
        if st.button('Extract Pages'):
            # extract the pages from pdf file
            pages_to_extract = reader.pages[start_page - 1 : end_page]

            writer = PdfWriter()
            for page in pages_to_extract:
                writer.add_page(page)
            
            # write all pages
            if len(writer.pages) > 0:
                # Use a BytesIO buffer to hold the resulting PDF in memory
                output_pdf_bytes = BytesIO()
                writer.write(output_pdf_bytes)
                output_pdf_bytes.seek(0)
                st.session_state.pdf_bytes = output_pdf_bytes
                st.session_state.file_ready = True
            else:
                st.session_state.file_ready = False
                st.warning('No pages selected to extract.')
    
    # if the file is removed, clear the session state
    else:
        if 'file_ready' in st.session_state:
            st.session_state.file_ready = False
        if 'pdf_bytes' in st.session_state:
            del st.session_state['pdf_bytes']
        if 'file_name' in st.session_state:
            del st.session_state['file_name']

# Download button appears below the columns
if st.session_state.get('file_ready', False):
    st.download_button(label = 'Download the extracted pages as PDF file',
                        data = st.session_state.pdf_bytes,
                        file_name = f"extracted_{st.session_state.file_name}",
                        mime= 'application/pdf')
