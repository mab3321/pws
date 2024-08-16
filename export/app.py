import os
import time
import multiprocessing
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from club import main as club_main
from helpers import *

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'multi'

def start_selenium_job(single_files=None,single_folder_path=None,po_files=None,po_folder_path=None):
    """Start the Selenium job with the provided data."""
    try:
        # Selenium job data
            pl_pdf_path = fty_pdf_path = csv_path = None
            pl_po_pdf_path = fty_po_pdf_path = csv_po_path = desc_po_path = None
            fty_parser = pl_parser = po_parser = None
            final_table_data = None
            pdf_paths = []
            # Extract files and paths
            if single_files:
                pl_pdf_path, fty_pdf_path, csv_path = extract_files_club_single(single_folder_path)
            if po_files:
                pl_po_pdf_path, fty_po_pdf_path, csv_po_path, desc_po_path = extract_files_club_po(po_folder_path)

            if fty_pdf_path:
                fty_parser = MultiSingleParse(fty_pdf_path, csv_path=csv_path)
                pl_parser = PlParse(pl_pdf_path)
            
            if fty_po_pdf_path:
                pl_parser = PlParse(pl_po_pdf_path)
                po_parser = MultiPOParse(path=fty_po_pdf_path, csv_path=csv_po_path, des_path=desc_po_path)
            
            if fty_pdf_path and fty_po_pdf_path:
                final_table_data = add_data_dictionaries(po_parser.extracted_data['final_table'], fty_parser.extracted_data['final_table'])
                fty_merge_path = merge_pdfs(fty_po_pdf_path, fty_pdf_path)
                pl_merge_path = merge_pdfs(pl_po_pdf_path, pl_pdf_path)
                pdf_paths = [fty_merge_path, pl_merge_path]
            elif fty_pdf_path:
                final_table_data = fty_parser.extracted_data['final_table']
                pdf_paths = [pl_pdf_path, fty_pdf_path]
            else:
                final_table_data = po_parser.extracted_data['final_table']
                pdf_paths = [fty_po_pdf_path, pl_po_pdf_path]
            print(final_table_data)
            # Prepare data for the Selenium job
            data = {
                'transaction_id': 123,
                'user_id': 123,
                'URL': 'https://app.psw.gov.pk/app/',
                'UserName': 'CA-01-2688539',
                'Password': 'Express@5599',
                'pdf_paths': pdf_paths,
                'pl_data': pl_parser.extracted_data if pl_parser else None,
                'fty_data': fty_parser.extracted_data if fty_parser else None,
                'po_obj': po_parser if po_parser else None,
                'final_table': final_table_data,
            }
            print(final_table_data)
            required_keys = list(data.keys())
            if not all(key in data for key in required_keys):
                print("Missing required keys in data dictionary")
                return False
            club_main(data)  # Your main Selenium job logic goes here
    except Exception as e:
        print(f"Error in Selenium job: {e}")

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def filter_empty_files(files):
    """Filter out files that have an empty filename."""
    return [file for file in files if file.filename]

def validate_po_files(filenames):
    """Ensure po files contain at least one of 'desc', 'fty', or 'pl' in their names."""
    required_patterns = ['desc', 'fty', 'pl']
    found_patterns = {pattern: False for pattern in required_patterns}

    for name in filenames:
        for pattern in required_patterns:
            if pattern in name:
                found_patterns[pattern] = True

    # Ensure all required patterns are found
    return all(found_patterns.values())

def validate_single_files(filenames):
    """Ensure single files contain both 'fty' and 'pl' in their names."""
    required_patterns = ['fty', 'pl']
    found_patterns = {pattern: False for pattern in required_patterns}

    for name in filenames:
        for pattern in required_patterns:
            if pattern in name:
                found_patterns[pattern] = True

    # Ensure all required patterns are found
    return all(found_patterns.values())

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        single_folder_path = None
        po_folder_path = None
        po_files = filter_empty_files(request.files.getlist('po_files[]'))
        single_files = filter_empty_files(request.files.getlist('single_files[]'))

        if not po_files and not single_files:
            flash('No files were selected for upload.')
            return redirect(request.url)

        # Validate po files
        if po_files:
            po_filenames = [file.filename for file in po_files]
            if not validate_po_files(po_filenames):
                flash('Error: PO files must contain "desc.xlsx", "fty", or "pl" in the names.')
                return redirect(request.url)

        # Validate single files
        if single_files:
            single_filenames = [file.filename for file in single_files]
            if not validate_single_files(single_filenames):
                flash('Error: Single files must contain both "fty" and "pl" in the names.')
                return redirect(request.url)

        try:
            # Create the timestamped folder for po_files
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            print(f"PO Files are {po_files}")
            print(f"Single Files are {single_files}")

            single_file_paths = []
            po_file_paths = []

            if po_files:
                po_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f"po{timestamp}")
                os.makedirs(po_folder_path, exist_ok=True)
                # Save the po files
                for file in po_files:
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(po_folder_path, filename)
                    file.save(save_path)
                    po_file_paths.append(save_path)

            # Save the single files to the single folder
            if single_files:
                single_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f"single{timestamp}")
                os.makedirs(single_folder_path, exist_ok=True)
                # Save the single files
                for file in single_files:
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(single_folder_path, filename)
                    file.save(save_path)
                    single_file_paths.append(save_path)

            # Start the Selenium job using multiprocessing, passing file paths instead of FileStorage objects
            selenium_process = multiprocessing.Process(target=start_selenium_job, args=(single_file_paths, single_folder_path, po_file_paths, po_folder_path))
            selenium_process.start()

            flash('Files successfully uploaded and Selenium job started.')
        except Exception as e:
            flash(f"An error occurred: {e}")
            print(e)

        return redirect(url_for('upload_files'))

    return render_template('upload.html')
if __name__ == '__main__':
    app.run(debug=True)
