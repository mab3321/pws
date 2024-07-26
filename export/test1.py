import os
import shutil

def assign_files():
    current_dir = os.getcwd()
    uploads_dir = os.path.abspath(os.path.join(current_dir, os.pardir, 'uploads'))
    
    pl_pdf_path = None
    fty_pdf_path = None
    csv_path = None

    for filename in os.listdir(uploads_dir):
        if filename.endswith('.pdf') or filename.endswith('.csv'):
            old_filepath = os.path.join(uploads_dir, filename)
            new_filename = filename.replace('-', '')
            new_filepath = os.path.join(uploads_dir, new_filename)
            
            # Rename file to remove dashes
            shutil.move(old_filepath, new_filepath)
            
            # Assign the renamed file to the appropriate variable
            if 'fty' in new_filename.lower() and new_filename.endswith('.pdf'):
                fty_pdf_path = new_filepath
            elif 'pl' in new_filename.lower() and new_filename.endswith('.pdf'):
                pl_pdf_path = new_filepath
            elif new_filename.endswith('.csv'):
                csv_path = new_filepath

    # Check if the required files were found and assigned
    if pl_pdf_path and fty_pdf_path and csv_path:
        print(f"PL PDF Path: {pl_pdf_path}")
        print(f"FTY PDF Path: {fty_pdf_path}")
        print(f"CSV Path: {csv_path}")
        # Return the paths for further use
        return pl_pdf_path, fty_pdf_path, csv_path
    else:
        print("Error: Could not find all required files.")
        return None, None, None

# Example usage
pl_pdf_path, fty_pdf_path, csv_path = assign_files()