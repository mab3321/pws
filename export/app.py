import os
import time
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'multi'

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
    """Ensure po files contain at least one of 'desc', 'fty', or 'pl' in their names."""
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
        po_files = filter_empty_files(request.files.getlist('po_files[]'))
        single_files = filter_empty_files(request.files.getlist('single_files[]'))

        if not po_files and not single_files:
            flash('No files were selected for upload.')
            return redirect(request.url)

        # Validate po files
        if po_files:
            po_filenames = [file.filename for file in po_files]
            if not validate_po_files(po_filenames):
                flash('Error: po files must contain "desc.xlsx", "fty", or "pl" in the names.')
                return redirect(request.url)

        # Validate single files
        if single_files:
            single_filenames = [file.filename for file in single_files]
            if not validate_single_files(single_filenames):
                flash('Error: Single files must contain both "fty" and "pl" in the names.')
                return redirect(request.url)

        # Create the timestamped folder for po_files
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        print(f"Po Files are {po_files}")
        print(f"Single Files are {single_files}")
        if po_files:
            po_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f"po{timestamp}")
            os.makedirs(po_folder_path, exist_ok=True)
            # Save the po files
            for file in po_files:
                filename = secure_filename(file.filename)
                save_path = os.path.join(po_folder_path, filename)
                file.save(save_path)
        # Save the single files to the single folder
        if single_files:
            single_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f"single{timestamp}")
            os.makedirs(single_folder_path, exist_ok=True)
            # Save the single files
            for file in single_files:
                filename = secure_filename(file.filename)
                save_path = os.path.join(single_folder_path, filename)
                file.save(save_path)
        

        flash('Files successfully uploaded.')
        return redirect(url_for('upload_files'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
