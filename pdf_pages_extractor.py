# streamlit app to extract pages from a PDF file
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import tempfile
import os

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
        
        if file:
            reader = PdfReader(file)
            pdf_length = len(reader.pages)

            st.write(f'The uploaded file has {pdf_length} pages.')
    with c2:
        st.image('./upload_icon.jpg', width=100)


# Helper function to parse page selection (single pages only, no ranges)
def parse_page_selection(selection_str, max_pages, allow_ranges=True):
    indices = []
    parts = selection_str.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        if '-' in part:
            if not allow_ranges:
                raise ValueError(f"Ranges like '{part}' are not allowed in text input. Please use the 'Add interval of pages' button for ranges.")
            try:
                start_str, end_str = part.split('-')
                start = int(start_str)
                end = int(end_str)
                if start > end:
                    raise ValueError(f"Invalid range '{part}': Start page must be less than or equal to end page.")
                indices.extend(range(start - 1, end))
            except ValueError as e:
                raise ValueError(f"Invalid range format '{part}': {e}")
        else:
            try:
                indices.append(int(part) - 1)
            except ValueError:
                raise ValueError(f"Invalid page number '{part}'.")
    
    # Validate indices
    if any(i < 0 or i >= max_pages for i in indices):
        raise ValueError(f"Page numbers must be between 1 and {max_pages}.")
        
    return indices

# Helper function to render interval builder
def render_interval_builder(mode_key, max_pages, default_intervals=None):
    ids_key = f'{mode_key}_interval_ids'
    next_id_key = f'{mode_key}_next_id'

    if ids_key not in st.session_state:
        st.session_state[ids_key] = default_intervals if default_intervals is not None else []
    
    if next_id_key not in st.session_state:
        # If we have default intervals, next_id should be higher than the max default id
        max_id = max(st.session_state[ids_key]) if st.session_state[ids_key] else -1
        st.session_state[next_id_key] = max_id + 1

    intervals = []
    
    # Iterate over IDs
    for i, interval_id in enumerate(st.session_state[ids_key]):
        st.markdown(f"**Interval {i+1}**")
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            start = st.number_input(f'Start page', min_value=1, max_value=max_pages, value=1, step=1, key=f'{mode_key}_start_{interval_id}')
        with c2:
            end = st.number_input(f'End page', min_value=1, max_value=max_pages, value=1, step=1, key=f'{mode_key}_end_{interval_id}')
        with c3:
            st.write("") # Spacer to align button
            st.write("")
            if st.button("❌", key=f'{mode_key}_remove_{interval_id}'):
                st.session_state[ids_key].remove(interval_id)
                st.rerun()
        
        intervals.append((start, end))

    if st.button('Add interval of pages', key=f'{mode_key}_add_btn'):
        st.session_state[ids_key].append(st.session_state[next_id_key])
        st.session_state[next_id_key] += 1
        st.rerun()
        
    return intervals

# Sidebar Menu
st.sidebar.title("Menu")
mode = st.sidebar.radio("Select Option", ["Extract Pages", "Reorder Pages", "Remove Pages"])

with col2:
    if file:
        # Reset state if a new file is uploaded
        if 'file_name' not in st.session_state or st.session_state.file_name != file.name:
            st.session_state.file_name = file.name
            # Reset all interval states
            for m in ['extract', 'reorder', 'remove']:
                if f'{m}_interval_ids' in st.session_state:
                    del st.session_state[f'{m}_interval_ids']
                if f'{m}_next_id' in st.session_state:
                    del st.session_state[f'{m}_next_id']
            
            st.session_state.file_ready = False
            if 'pdf_bytes' in st.session_state:
                del st.session_state['pdf_bytes']

        if mode == "Extract Pages":
            st.subheader("Extract Pages")
            
            # Use the helper function, default to 1 interval for Extract mode
            intervals = render_interval_builder('extract', pdf_length, default_intervals=[0])
            
            if st.button('Extract Pages'):
                writer = PdfWriter()
                
                for interval in intervals:
                    start_page, end_page = interval
                    # extract the pages from pdf file
                    pages_to_extract = reader.pages[start_page - 1 : end_page]

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

        elif mode == "Reorder Pages":
            st.subheader("Reorder Pages")
            
            pages_to_move_str = st.text_input("Pages to move (e.g., '1, 4, 7')", value="")
            
            st.write("---")
            st.write("Or add intervals:")
            intervals = render_interval_builder('reorder', pdf_length, default_intervals=[])
            
            c1, c2 = st.columns(2)
            with c1:
                destination_page = st.number_input("Destination Page", min_value=1, max_value=pdf_length, value=1)
            with c2:
                position = st.radio("Position", ["Before", "After"])
            
            if st.button("Reorder Pages"):
                try:
                    indices_to_move = parse_page_selection(pages_to_move_str, pdf_length, allow_ranges=False)
                    
                    # Add intervals to indices_to_move
                    for start, end in intervals:
                        if start > end:
                             st.error(f"Invalid interval: Start page {start} must be less than or equal to end page {end}.")
                             st.stop()
                        indices_to_move.extend(range(start - 1, end))
                    
                    if not indices_to_move:
                        st.warning("No pages selected to move.")
                        st.stop()

                    # Create list of all page indices
                    all_indices = list(range(pdf_length))
                    
                    # Remove indices to move
                    remaining_indices = [i for i in all_indices if i not in indices_to_move]
                    
                    # Calculate insertion index
                    dest_index = destination_page - 1
                    
                    if dest_index in indices_to_move:
                        st.error("Destination page cannot be one of the pages being moved.")
                        st.stop()
                        
                    # Find where the destination page is in the remaining list
                    try:
                        insert_pos = remaining_indices.index(dest_index)
                    except ValueError:
                        st.error("Error calculating destination.")
                        st.stop()
                    
                    if position == "After":
                        insert_pos += 1
                    
                    # Insert
                    new_order = remaining_indices[:insert_pos] + indices_to_move + remaining_indices[insert_pos:]
                    
                    # Write new PDF to temp file
                    writer = PdfWriter()
                    for i in new_order:
                        writer.add_page(reader.pages[i])
                    
                    # Create temp file
                    temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf', prefix='reordered_')
                    os.close(temp_fd)
                    
                    with open(temp_path, 'wb') as f:
                        writer.write(f)
                    
                    st.session_state.temp_file_path = temp_path
                    st.session_state.file_ready = True
                    st.success("Pages reordered successfully!")
                    
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        elif mode == "Remove Pages":
            st.subheader("Remove Pages")
            
            pages_to_remove_str = st.text_input("Pages to remove (e.g., '1, 4, 7')", value="")
            
            st.write("---")
            st.write("Or add intervals:")
            intervals = render_interval_builder('remove', pdf_length, default_intervals=[])
            
            if st.button("Remove Pages"):
                try:
                    indices_to_remove = parse_page_selection(pages_to_remove_str, pdf_length, allow_ranges=False)
                    
                    # Add intervals to indices_to_remove
                    for start, end in intervals:
                        if start > end:
                             st.error(f"Invalid interval: Start page {start} must be less than or equal to end page {end}.")
                             st.stop()
                        indices_to_remove.extend(range(start - 1, end))
                    
                    if not indices_to_remove:
                        st.warning("No pages selected to remove.")
                        st.stop()

                    # Create list of all page indices
                    all_indices = list(range(pdf_length))
                    
                    # Keep pages NOT in removal list
                    indices_to_keep = [i for i in all_indices if i not in indices_to_remove]
                    
                    if not indices_to_keep:
                        st.error("Cannot remove all pages.")
                        st.stop()

                    # Write new PDF to temp file
                    writer = PdfWriter()
                    for i in indices_to_keep:
                        writer.add_page(reader.pages[i])
                    
                    # Create temp file
                    temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf', prefix='removed_')
                    os.close(temp_fd)
                    
                    with open(temp_path, 'wb') as f:
                        writer.write(f)
                    
                    st.session_state.temp_file_path = temp_path
                    st.session_state.file_ready = True
                    st.success(f"Removed {len(indices_to_remove)} pages successfully!")
                    
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    
    # if the file is removed, clear the session state
    else:
        if 'file_ready' in st.session_state:
            st.session_state.file_ready = False
        if 'pdf_bytes' in st.session_state:
            del st.session_state['pdf_bytes']
        if 'temp_file_path' in st.session_state:
            # Clean up temp file if it exists
            if os.path.exists(st.session_state.temp_file_path):
                os.remove(st.session_state.temp_file_path)
            del st.session_state['temp_file_path']
        if 'file_name' in st.session_state:
            del st.session_state['file_name']

# Download button appears below the columns
if st.session_state.get('file_ready', False):
    # Check if we have a temp file or BytesIO
    if 'temp_file_path' in st.session_state and os.path.exists(st.session_state.temp_file_path):
        # Read temp file for download
        with open(st.session_state.temp_file_path, 'rb') as f:
            file_data = f.read()
        
        # Download button with cleanup callback
        if st.download_button(
            label='Download processed file',
            data=file_data,
            file_name=f"processed_{st.session_state.file_name}",
            mime='application/pdf',
            on_click=lambda: None  # Cleanup happens on next rerun
        ):
            # This block executes after download is initiated
            pass
        
        # Clean up temp file after download button is rendered
        # The file will be deleted when user uploads a new file or removes current file
        
    elif 'pdf_bytes' in st.session_state:
        # Extract Pages mode - use BytesIO
        st.download_button(
            label='Download the result PDF file',
            data=st.session_state.pdf_bytes,
            file_name=f"extracted_{st.session_state.file_name}",
            mime='application/pdf'
        )

