import os
import time
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'multi'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_multi_files(filenames):
    """Check if filenames contain the required patterns for .xlsx and .pdf files, and allow .csv files without pattern validation."""
    required_patterns = ['fty', 'pl', 'des']
    allowed_extensions = ['.xlsx', '.pdf', '.csv']
    
    for name in filenames:
        if name.endswith('.csv'):
            continue  # Skip pattern validation for .csv files
        elif not any(pattern in name for pattern in required_patterns) or not any(name.endswith(ext) for ext in ['.xlsx', '.pdf']):
            return False
    
    # Ensure all files have valid extensions
    valid_extensions = [any(name.endswith(ext) for ext in allowed_extensions) for name in filenames]

    if not all(valid_extensions):
        return False
    
    return True

def allowed_single_files(filenames):
    """Check if filenames contain 'pl' or 'fty' and are either .pdf or .csv files."""
    required_patterns = ['pl', 'fty']
    allowed_extensions = ['.pdf', '.csv']
    
    for name in filenames:
        if not any(pattern in name for pattern in required_patterns):
            return False
        if not any(name.endswith(ext) for ext in allowed_extensions):
            return False
    
    return True

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        if 'multi_files[]' not in request.files and 'single_files[]' not in request.files:
            flash('No files part')
            return redirect(request.url)

        # Handle multi files
        multi_files = request.files.getlist('multi_files[]')
        multi_filenames = [file.filename for file in multi_files]
        if multi_files and not allowed_multi_files(multi_filenames):
            flash('Error: Multi files must contain "fty", "pl", or "des" in the names and have .xlsx or .pdf extensions. CSV files are allowed without pattern validation.')
            return redirect(request.url)

        # Handle single files
        single_files = request.files.getlist('single_files[]')
        single_filenames = [file.filename for file in single_files]
        if single_files and not allowed_single_files(single_filenames):
            flash('Error: Single files must contain "pl" or "fty" and have .pdf or .csv extensions.')
            return redirect(request.url)

        # Save all files to the same timestamped folder
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f"po{timestamp}")
        os.makedirs(folder_path, exist_ok=True)

        for file in multi_files + single_files:
            filename = secure_filename(file.filename)
            save_path = os.path.join(folder_path, filename)
            file.save(save_path)
        
        flash('Files successfully uploaded to the multi folder')
        return redirect(url_for('upload_files'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
