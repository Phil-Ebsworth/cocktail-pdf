import os
import glob

pdf_folder = './pdfs'
pdf_files = glob.glob(os.path.join(pdf_folder, '*'))

for file_path in pdf_files:
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")